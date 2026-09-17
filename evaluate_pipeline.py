"""
evaluate_pipeline.py
---------------------
Quantitative robustness evaluation: runs the full pipeline across a range of
perspective-skew offsets and two sensor-noise conditions against a synthetic
document with known ground-truth text, and reports mean OCR confidence,
Word Error Rate (WER), and elapsed time for each configuration.

Usage:
    python3 evaluate_pipeline.py
"""
import time
import json
import numpy as np
import cv2

from src import document_detector, enhancer, ocr_extractor

GROUND_TRUTH_WORDS = ["HELLO", "WORLD", "Computer", "Vision", "Test"]


def make_synthetic_document(width=600, height=800, angle_offset=15, noise_sigma=0, seed=0):
    rng = np.random.default_rng(seed)
    canvas = np.full((height + 200, width + 200, 3), 40, dtype=np.uint8)

    page = np.full((height, width, 3), 255, dtype=np.uint8)
    cv2.putText(page, "HELLO WORLD", (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
    cv2.putText(page, "Computer Vision Test", (40, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

    src_pts = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    dst_pts = np.float32([
        [100 + angle_offset, 100],
        [100 + width, 100 + angle_offset],
        [100 + width - angle_offset, 100 + height],
        [100, 100 + height - angle_offset],
    ])
    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    canvas_h, canvas_w = canvas.shape[:2]
    warped_page = cv2.warpPerspective(page, matrix, (canvas_w, canvas_h))

    mask = np.any(warped_page != 0, axis=2)
    canvas[mask] = warped_page[mask]

    if noise_sigma > 0:
        noise = rng.normal(0, noise_sigma, canvas.shape)
        canvas = np.clip(canvas.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    return canvas


def levenshtein(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[n][m]


def word_error_rate(ground_truth, hypothesis_text):
    hyp_words = hypothesis_text.split()
    dist = levenshtein(ground_truth, hyp_words)
    return dist / len(ground_truth)


def run_condition(skew, sigma, seed):
    img = make_synthetic_document(angle_offset=skew, noise_sigma=sigma, seed=seed)
    t0 = time.time()
    det = document_detector.detect_and_warp(img)
    enh = enhancer.enhance_document(det.warped)
    res = ocr_extractor.extract_text(enh)
    elapsed = time.time() - t0
    wer = word_error_rate(GROUND_TRUTH_WORDS, res.text)
    return {
        "skew": skew, "sigma": sigma,
        "mean_confidence": round(res.mean_confidence, 1),
        "wer": round(wer, 3),
        "time_s": round(elapsed, 3),
    }


def main():
    conditions = [(s, n) for s in (0, 10, 20, 30, 45) for n in (0, 15)]
    results = [run_condition(s, n, seed=42) for s, n in conditions]
    print(json.dumps(results, indent=2))
    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
