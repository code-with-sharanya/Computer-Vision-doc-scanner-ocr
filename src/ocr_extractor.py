"""
ocr_extractor.py
-----------------
Module 3: OCR Text Extraction & Structured Output.

Responsible for:
    * Running Tesseract OCR over the enhanced/binarized document image
    * Computing basic confidence statistics
    * Emitting structured output (plain text + JSON with per-word metadata)

This module has a single external dependency boundary (pytesseract) so it
can be swapped out (e.g., for a cloud OCR API) without touching Modules 1/2 —
a deliberate modularity / maintainability decision.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

import numpy as np
import pytesseract
from pytesseract import Output

logger = logging.getLogger("doc_scanner.ocr")


@dataclass
class OCRResult:
    text: str
    mean_confidence: float
    word_count: int
    words: list = field(default_factory=list)  # list of dicts: text, conf, bbox

    def to_json(self) -> str:
        return json.dumps(
            {
                "text": self.text,
                "mean_confidence": round(self.mean_confidence, 2),
                "word_count": self.word_count,
                "words": self.words,
            },
            indent=2,
            ensure_ascii=False,
        )


def extract_text(image: np.ndarray, lang: str = "eng", min_confidence: int = 0) -> OCRResult:
    """
    Run OCR on a (preferably binarized) image and return structured results.
    """
    if image is None or image.size == 0:
        raise ValueError("extract_text received an empty image.")

    raw_text = pytesseract.image_to_string(image, lang=lang).strip()

    data = pytesseract.image_to_data(image, lang=lang, output_type=Output.DICT)

    words = []
    confidences = []
    n = len(data["text"])
    for i in range(n):
        word = data["text"][i].strip()
        conf = float(data["conf"][i])
        if not word or conf < 0:
            continue
        if conf < min_confidence:
            continue
        words.append(
            {
                "text": word,
                "confidence": conf,
                "bbox": {
                    "x": data["left"][i],
                    "y": data["top"][i],
                    "w": data["width"][i],
                    "h": data["height"][i],
                },
            }
        )
        confidences.append(conf)

    mean_conf = sum(confidences) / len(confidences) if confidences else 0.0

    logger.info(
        "OCR complete: %d words extracted, mean confidence %.1f%%",
        len(words),
        mean_conf,
    )

    return OCRResult(
        text=raw_text,
        mean_confidence=mean_conf,
        word_count=len(words),
        words=words,
    )
