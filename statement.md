# Problem Statement

## Problem Statement

Photos of physical documents (receipts, notes, forms, printed pages) taken
with a phone camera are typically skewed, perspective-distorted, and
unevenly lit — this makes them hard to read cleanly and unreliable to run
through OCR directly. There is a need for a lightweight, no-GUI tool that
can take a raw photo of a document and produce both a clean, flattened scan
and accurate machine-readable text from it.

## Scope of the Project

This project implements a three-stage command-line computer vision
pipeline:

1. **Document detection & perspective correction** — locate the document's
   boundary in the photo and warp it into a flat, top-down view.
2. **Image enhancement & binarization** — clean up lighting/noise and
   produce a high-contrast, scanner-quality black-and-white image.
3. **OCR text extraction** — extract the document's text and return it in
   both plain-text and structured JSON form (with per-word confidence and
   position).

The scope is limited to single-image, single-document inputs (JPEG/PNG/BMP/
TIFF) processed via the command line; it does not cover multi-page batch
scanning, handwriting recognition, or a graphical interface.

## Target Users

- Students/evaluators needing a quick way to digitize printed notes,
  receipts, or handouts.
- Anyone needing a scriptable, GUI-free document-to-text pipeline (e.g. for
  integrating into a larger automation workflow).

## High-Level Features

- Robust document boundary detection with a safe fallback when no boundary
  is found (uses the full frame instead of failing).
- CLAHE-based contrast enhancement and adaptive thresholding for clean,
  legible scans regardless of uneven lighting in the source photo.
- Structured OCR output (JSON with per-word bounding boxes and confidence
  scores), not just raw text — useful for downstream processing.
- Fully modular, independently testable codebase with unit tests and
  structured logging (console + log file).
- Command-line only — no GUI dependency, so it runs anywhere Python and
  Tesseract are installed.
