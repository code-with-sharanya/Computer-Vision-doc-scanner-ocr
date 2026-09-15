# Problem Statement

## Background

Optical document capture has moved almost entirely from flatbed scanners to
phone cameras. A flatbed scanner guarantees a fixed, orthogonal viewpoint and
controlled, even lighting; a phone photo guarantees neither. The result is a
predictable set of defects in every "photo of a document":

- **Perspective distortion** — the camera is rarely held exactly parallel to
  the page, so the document appears as a skewed quadrilateral rather than a
  rectangle, and text lines that are straight on paper appear to converge or
  diverge in the image.
- **Uneven illumination** — ambient light, shadows from the phone or the
  user's hand, and glare from glossy paper create local brightness gradients
  that defeat a single global brightness/contrast setting.
- **Sensor and compression noise** — especially in low light, phone camera
  sensors introduce visible noise that both looks unprofessional in a
  "scanned" image and actively hurts OCR accuracy, since OCR engines are
  trained primarily on clean, high-contrast text.

Because of this, a raw phone photo fed directly into an OCR engine typically
produces poor and inconsistent results — broken words, garbled characters,
and low per-word confidence scores — even when the text itself is
perfectly legible to a human. Existing solutions either require a
proprietary mobile app (which does not integrate into an automated or
scriptable workflow) or a paid cloud OCR API (which requires network access,
raises data-privacy questions for sensitive documents, and adds latency and
cost per call).

## Problem Statement

There is a need for a **lightweight, fully local, command-line tool** that
takes a single raw photo of a document as input and produces:

1. A geometrically corrected, "flattened" image of the document as if it had
   been captured by a flatbed scanner, regardless of the angle it was
   photographed at.
2. A visually clean, high-contrast, denoised rendition of that document,
   robust to the uneven lighting typical of handheld photography.
3. An accurate, structured, machine-readable transcription of the document's
   text — not just a flat string, but per-word confidence and position data
   that downstream systems can use for validation or further processing.

The tool must run entirely offline (no cloud dependency), be operable from a
terminal with no graphical interface, and be built from modular,
independently testable components so that any one stage (geometry
correction, enhancement, or OCR) can be understood, evaluated, and replaced
on its own.

## Scope of the Project

**In scope:**

- Single-image input (one photographed document per invocation), in JPEG,
  PNG, BMP, or TIFF format.
- Document boundary detection under moderate perspective skew (the four
  edges of the document are visible in the frame, even if not axis-aligned).
- Contrast/lighting correction sufficient for printed (not handwritten) text.
- English-language OCR by default, with the language configurable via a
  command-line flag since Tesseract supports 100+ languages out of the box.
- Structured (JSON) as well as plain-text output.
- Command-line operation only — every feature is reachable via flags, with
  no GUI or web interface required.

**Out of scope (explicitly, and noted as future work in Section 13 of the
report):**

- Multi-page or batch document processing in a single invocation.
- Handwriting recognition (Tesseract's LSTM models are tuned for printed
  text; handwriting requires a materially different model class).
- Automatic 90°/180° rotation correction (the current pipeline assumes the
  document is already roughly "upright" in the frame, modulo perspective
  skew — see Limitations in the report).
- A graphical user interface of any kind, per the assignment's CLI
  requirement.

## Target Users

- **Students and researchers** who need to quickly digitize lecture notes,
  printed handouts, or scanned forms into searchable text without a
  dedicated scanning app.
- **Anyone building a larger automation pipeline** (e.g. an expense-tracking
  script, a note-taking workflow, a document-archival job) who needs a
  scriptable, dependency-light OCR stage they can call from a shell script
  or cron job, without a cloud API key or network dependency.
- **Evaluators/graders** of this assignment, who need to run the tool
  end-to-end from a terminal with a single, well-documented command and
  verify its output against the stated functional and non-functional
  requirements.

## High-Level Features

- **Robust document boundary detection** using Canny edge detection and
  polygonal contour approximation, with a safe fallback to the full frame
  when no clean four-point boundary can be found — so the pipeline never
  hard-fails on an imperfect photo.
- **Homography-based perspective correction** that maps the detected
  (possibly skewed) quadrilateral onto a proper rectangle, correctly sized
  to preserve the document's aspect ratio based on its longest measured
  edges.
- **Lighting-robust enhancement** combining CLAHE (contrast-limited adaptive
  histogram equalization), non-local-means denoising, and adaptive Gaussian
  thresholding — chosen specifically because each addresses a distinct,
  named failure mode of naive global-threshold binarization.
- **Structured OCR output**: alongside a human-readable `.txt` transcript,
  every word is emitted with its confidence score and bounding box in JSON,
  enabling downstream filtering (e.g. "flag anything under 60% confidence
  for manual review") that a flat text file cannot support.
- **Defensive engineering throughout**: every module validates its inputs
  and raises specific, named exceptions; the CLI catches and logs these
  instead of surfacing raw stack traces; every run is logged with
  timestamps to both the console and a persistent log file.
- **A fully modular, unit-tested codebase** — three independently testable
  modules connected through explicit, typed data classes
  (`DetectionResult`, `OCRResult`), so each stage's correctness can be
  verified in isolation from the others.
