"""
main.py
-------
Command-line entry point for the Document Scanner + OCR pipeline.

Workflow (matches the report's Process Flow diagram):
    input image
        -> Module 1: document_detector.detect_and_warp()
        -> Module 2: enhancer.enhance_document()
        -> Module 3: ocr_extractor.extract_text()
        -> outputs: warped.jpg, enhanced.jpg, text.txt, result.json

Usage:
    python -m src.main --input path/to/photo.jpg --output-dir results/
    python -m src.main --input path/to/photo.jpg --lang eng --no-clahe
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import cv2

from src import document_detector, enhancer, ocr_extractor, utils

logger = logging.getLogger("doc_scanner.main")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="doc-scanner-ocr",
        description="Scan a photographed document: detect boundary, "
        "correct perspective, enhance, and extract text via OCR.",
    )
    parser.add_argument("--input", "-i", required=True, help="Path to the input image.")
    parser.add_argument(
        "--output-dir", "-o", default="output", help="Directory to write results to."
    )
    parser.add_argument(
        "--lang", default="eng", help="Tesseract language code (default: eng)."
    )
    parser.add_argument(
        "--no-clahe", action="store_true", help="Disable CLAHE contrast enhancement."
    )
    parser.add_argument(
        "--min-confidence",
        type=int,
        default=0,
        help="Minimum per-word OCR confidence (0-100) to keep in structured output.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable debug-level logging."
    )
    return parser


def run_pipeline(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error("Input file does not exist: %s", input_path)
        return 1
    if not utils.is_supported_image(str(input_path)):
        logger.error("Unsupported file type: %s", input_path.suffix)
        return 1

    out_dir = utils.ensure_dir(args.output_dir)

    image = cv2.imread(str(input_path))
    if image is None:
        logger.error("Failed to read image (corrupt file or unsupported codec).")
        return 1

    start = time.time()

    # ---- Module 1: Document Detection & Perspective Correction ----
    try:
        detection = document_detector.detect_and_warp(image)
    except document_detector.DocumentNotFoundError as exc:
        logger.error("Document detection failed: %s", exc)
        return 1

    warped_path = out_dir / "1_warped.jpg"
    cv2.imwrite(str(warped_path), detection.warped)
    logger.info("Module 1 done -> %s", warped_path)

    # ---- Module 2: Image Enhancement & Binarization ----
    enhanced = enhancer.enhance_document(detection.warped, apply_clahe=not args.no_clahe)
    enhanced_path = out_dir / "2_enhanced.jpg"
    cv2.imwrite(str(enhanced_path), enhanced)
    logger.info("Module 2 done -> %s", enhanced_path)

    # ---- Module 3: OCR Text Extraction ----
    try:
        result = ocr_extractor.extract_text(
            enhanced, lang=args.lang, min_confidence=args.min_confidence
        )
    except Exception as exc:  # pytesseract / tesseract runtime errors
        logger.error("OCR extraction failed: %s", exc)
        return 1

    text_path = out_dir / "3_text.txt"
    json_path = out_dir / "3_result.json"
    text_path.write_text(result.text, encoding="utf-8")
    json_path.write_text(result.to_json(), encoding="utf-8")
    logger.info("Module 3 done -> %s, %s", text_path, json_path)

    elapsed = time.time() - start
    print("\n===== Document Scanner + OCR — Summary =====")
    print(f"Input:              {input_path}")
    print(f"Words extracted:    {result.word_count}")
    print(f"Mean OCR confidence:{result.mean_confidence:.1f}%")
    print(f"Time elapsed:       {elapsed:.2f}s")
    print(f"Outputs written to: {out_dir.resolve()}")
    print("=============================================\n")

    return 0


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    utils.setup_logging(verbose=args.verbose)
    sys.exit(run_pipeline(args))


if __name__ == "__main__":
    main()
