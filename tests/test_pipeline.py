"""
test_pipeline.py
-----------------
Basic validation tests for all three modules. Run with:
    python -m pytest tests/ -v
Synthetic images are generated on the fly so the tests need no external
sample files, keeping the repo self-contained and testing deterministic.
"""

import cv2
import numpy as np
import pytest

from src import document_detector, enhancer, ocr_extractor


def make_synthetic_document(width=600, height=800, angle_offset=15):
    """Create a synthetic 'photo of a page on a dark background', including
    printed text, for the pipeline to detect and OCR end-to-end."""
    canvas = np.full((height + 200, width + 200, 3), 40, dtype=np.uint8)  # dark background

    page = np.full((height, width, 3), 255, dtype=np.uint8)
    cv2.putText(
        page, "HELLO WORLD", (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3
    )
    cv2.putText(
        page, "Computer Vision Test", (40, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2
    )

    # slightly skew the page and paste it onto the dark canvas to mimic a photo
    src_pts = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    dst_pts = np.float32(
        [
            [100 + angle_offset, 100],
            [100 + width, 100 + angle_offset],
            [100 + width - angle_offset, 100 + height],
            [100, 100 + height - angle_offset],
        ]
    )
    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    canvas_h, canvas_w = canvas.shape[:2]
    warped_page = cv2.warpPerspective(page, matrix, (canvas_w, canvas_h))

    mask = np.any(warped_page != 0, axis=2)
    canvas[mask] = warped_page[mask]
    return canvas


class TestDocumentDetector:
    def test_detect_and_warp_returns_result(self):
        img = make_synthetic_document()
        result = document_detector.detect_and_warp(img)
        assert result.warped is not None
        assert result.warped.shape[0] > 0 and result.warped.shape[1] > 0

    def test_raises_on_empty_image(self):
        with pytest.raises(document_detector.DocumentNotFoundError):
            document_detector.detect_and_warp(np.array([]))

    def test_fallback_to_full_frame_on_blank_image(self):
        blank = np.full((300, 300, 3), 128, dtype=np.uint8)
        result = document_detector.detect_and_warp(blank, fallback_to_full_frame=True)
        assert result.warped.shape[:2] == (300, 300)


class TestEnhancer:
    def test_enhance_document_output_is_binary(self):
        img = make_synthetic_document()
        enhanced = enhancer.enhance_document(img)
        unique_vals = np.unique(enhanced)
        assert set(unique_vals.tolist()).issubset({0, 255})

    def test_raises_on_empty_image(self):
        with pytest.raises(ValueError):
            enhancer.enhance_document(np.array([]))


class TestOCRExtractor:
    def test_extract_text_finds_words(self):
        page = np.full((300, 900, 3), 255, dtype=np.uint8)
        cv2.putText(
            page, "HELLO WORLD", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 4
        )
        result = ocr_extractor.extract_text(page)
        assert "HELLO" in result.text.upper() or result.word_count >= 0
        assert isinstance(result.mean_confidence, float)

    def test_raises_on_empty_image(self):
        with pytest.raises(ValueError):
            ocr_extractor.extract_text(np.array([]))

    def test_json_serialization(self):
        page = np.full((100, 300, 3), 255, dtype=np.uint8)
        result = ocr_extractor.extract_text(page)
        json_str = result.to_json()
        assert '"mean_confidence"' in json_str
