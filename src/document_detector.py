"""
document_detector.py
---------------------
Module 1: Document Detection & Perspective Correction.

Responsible for:
    * Locating the largest quadrilateral (document-like) contour in an image
    * Ordering its four corner points consistently (TL, TR, BR, BL)
    * Computing a perspective (homography) transform and warping the image
      into a flat, top-down view of the document.

Concepts used (CSE3010 syllabus):
    - Edge detection (Canny)              -> Module 3
    - Contour / boundary analysis         -> Module 1/3
    - Homography & perspective transform  -> Module 2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import cv2
import numpy as np

logger = logging.getLogger("doc_scanner.detector")


class DocumentNotFoundError(Exception):
    """Raised when no suitable document-like contour can be located."""


@dataclass
class DetectionResult:
    warped: np.ndarray          # perspective-corrected image (BGR)
    corners: np.ndarray         # the 4 ordered corner points used
    original_shape: tuple       # (h, w) of the input image


def _order_points(pts: np.ndarray) -> np.ndarray:
    """Order 4 points as top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left has smallest sum
    rect[2] = pts[np.argmax(s)]   # bottom-right has largest sum

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right has smallest difference
    rect[3] = pts[np.argmax(diff)]  # bottom-left has largest difference
    return rect


def _four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
    """Apply a perspective (homography) warp defined by 4 corner points."""
    rect = _order_points(pts)
    (tl, tr, br, bl) = rect

    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_width = max(int(width_a), int(width_b))

    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_height = max(int(height_a), int(height_b))

    dst = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ],
        dtype="float32",
    )

    matrix = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
    return warped


def find_document_contour(
    image: np.ndarray,
    canny_low: int = 75,
    canny_high: int = 200,
    approx_epsilon_ratio: float = 0.02,
) -> np.ndarray | None:
    """Locate the largest 4-point contour in the image, or None if not found."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, canny_low, canny_high)
    edged = cv2.dilate(edged, np.ones((3, 3), np.uint8), iterations=1)

    contours, _ = cv2.findContours(
        edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, approx_epsilon_ratio * perimeter, True)
        if len(approx) == 4:
            return approx.reshape(4, 2).astype("float32")

    return None


def detect_and_warp(
    image: np.ndarray,
    resize_height: int = 800,
    fallback_to_full_frame: bool = True,
) -> DetectionResult:
    """
    Full Module 1 pipeline: detect the document boundary and produce a
    perspective-corrected, top-down image.

    If fallback_to_full_frame is True and no 4-point contour is found,
    the whole image is used (so downstream modules still get an input) —
    this keeps the pipeline robust (non-functional requirement: reliability).
    """
    if image is None or image.size == 0:
        raise DocumentNotFoundError("Input image is empty or could not be read.")

    original_shape = image.shape[:2]
    ratio = image.shape[0] / float(resize_height)
    resized = cv2.resize(image, (int(image.shape[1] / ratio), resize_height))

    contour = find_document_contour(resized)

    if contour is None:
        logger.warning("No 4-point document contour found.")
        if not fallback_to_full_frame:
            raise DocumentNotFoundError(
                "Could not locate a document boundary in the image."
            )
        h, w = original_shape
        corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype="float32")
        warped = image.copy()
        return DetectionResult(warped=warped, corners=corners, original_shape=original_shape)

    # Scale contour back up to original image resolution
    full_res_corners = contour * ratio
    warped = _four_point_transform(image, full_res_corners)

    logger.info("Document contour found; perspective correction applied.")
    return DetectionResult(
        warped=warped, corners=full_res_corners, original_shape=original_shape
    )
