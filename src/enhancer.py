"""
enhancer.py
-----------
Module 2: Image Enhancement & Binarization.

Responsible for:
    * Converting the warped document to grayscale
    * Denoising
    * Adaptive thresholding (binarization) to produce a clean, scanner-like
      black-and-white page, improving downstream OCR accuracy.

Concepts used (CSE3010 syllabus):
    - Image Enhancement / Restoration     -> Module 1
    - Histogram Processing (CLAHE)        -> Module 1
    - Filtering / denoising               -> Module 1
"""

from __future__ import annotations

import logging

import cv2
import numpy as np

logger = logging.getLogger("doc_scanner.enhancer")


def enhance_document(
    image: np.ndarray,
    apply_clahe: bool = True,
    denoise_strength: int = 9,
    adaptive_block_size: int = 25,
    adaptive_c: int = 15,
) -> np.ndarray:
    """
    Enhance a warped document image and binarize it into a clean scan.

    Steps: grayscale -> (optional) CLAHE contrast equalization ->
    denoise -> adaptive threshold.
    """
    if image is None or image.size == 0:
        raise ValueError("enhance_document received an empty image.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if apply_clahe:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        logger.debug("Applied CLAHE histogram equalization.")

    denoised = cv2.fastNlMeansDenoising(gray, h=denoise_strength)

    block_size = adaptive_block_size if adaptive_block_size % 2 == 1 else adaptive_block_size + 1
    binarized = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        adaptive_c,
    )

    logger.info("Enhancement + binarization complete.")
    return binarized


def sharpen(image: np.ndarray) -> np.ndarray:
    """Apply a mild unsharp-mask style sharpening kernel."""
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(image, -1, kernel)
