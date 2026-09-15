"""
evaluate_pipeline.py
--------------------
Runs the pipeline across a range of synthetic skew angles and noise levels
to produce real, measured accuracy/confidence/timing data for the project
report's Evaluation Methodology section (rather than a single anecdotal run).
"""
import sys
import time
import json

sys.path.insert(0, ".")
import cv2
import numpy as np
from src import document_detector, enhancer, ocr_extractor

GROUND_TRUTH = "HELLO WORLD\n\nComputer Vision Test"


def make_doc(angle_offset, noise_sigma=0, width=600, height=800):
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
        noise = np.random.normal(0, noise_sigma, canvas.shape).astype(np.int16)
        canvas = np.clip(canvas.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    return canvas


def word_error_rate(ground_truth, hypothesis):
    gt_words = ground_truth.split()
    hyp_words = hypothesis.split()
    # simple Levenshtein distance over word sequences
    m, n = len(gt_words), len(hyp_words)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if gt_words[i - 1] == hyp_words[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[m][n] / max(1, m)


results = []
for angle in [0, 10, 20, 30, 45]:
    for noise in [0, 15]:
        img = make_doc(angle, noise)
        t0 = time.time()
        det = document_detector.detect_and_warp(img)
        enh = enhancer.enhance_document(det.warped)
        ocr = ocr_extractor.extract_text(enh)
        elapsed = time.time() - t0
        wer = word_error_rate(GROUND_TRUTH, ocr.text)
        results.append({
            "angle_px_offset": angle,
            "noise_sigma": noise,
            "mean_confidence": round(ocr.mean_confidence, 1),
            "word_count": ocr.word_count,
            "word_error_rate": round(wer, 3),
            "elapsed_sec": round(elapsed, 3),
        })

print(json.dumps(results, indent=2))
with open("assets/diagrams/evaluation_results.json", "w") as f:
    json.dump(results, f, indent=2)
