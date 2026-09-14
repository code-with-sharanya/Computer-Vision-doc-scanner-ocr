# Document Scanner + OCR Pipeline

A command-line computer vision pipeline that turns a photo of a document
(receipt, page, note, form) into a clean, perspective-corrected scan and
extracts its text via OCR — no GUI required.

Built for CSE3010 (Computer Vision), VIT Bhopal — "Build Your Own Project."

## Features

- **Document detection & perspective correction** — locates the document's
  boundary in a photo (even at an angle) using Canny edge detection and
  contour analysis, then applies a homography warp to produce a flat,
  top-down view.
- **Image enhancement & binarization** — CLAHE contrast equalization,
  denoising, and adaptive thresholding to turn the warped photo into a
  clean, scanner-quality black-and-white page.
- **OCR text extraction** — runs Tesseract OCR over the enhanced image and
  outputs both plain text and structured JSON (per-word text, confidence,
  and bounding box).
- Robust fallback behaviour, structured logging (console + file), and a
  fully modular codebase (`src/`) with unit tests (`tests/`).

## Project Structure

```
doc-scanner-ocr/
├── src/
│   ├── document_detector.py   # Module 1: detection + perspective correction
│   ├── enhancer.py            # Module 2: enhancement + binarization
│   ├── ocr_extractor.py       # Module 3: OCR + structured output
│   ├── utils.py                # logging & shared helpers
│   └── main.py                 # CLI entry point
├── tests/
│   └── test_pipeline.py        # unit tests for all 3 modules
├── assets/diagrams/            # architecture / workflow / UML diagrams
├── sample_images/               # example input image(s)
├── requirements.txt
├── README.md
└── statement.md
```

## Technologies / Tools Used

- Python 3.10+
- OpenCV (`opencv-python-headless`) — image processing, contour detection,
  perspective transforms
- NumPy — array operations
- Tesseract OCR + `pytesseract` — text extraction
- `pytest` — unit testing

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/<github-username>/doc-scanner-ocr.git
   cd doc-scanner-ocr
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install the Tesseract OCR engine** (system dependency, not a Python
   package):
   - **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`
   - **macOS (Homebrew):** `brew install tesseract`
   - **Windows:** install from the
     [UB-Mannheim Tesseract build](https://github.com/UB-Mannheim/tesseract/wiki)
     and ensure `tesseract.exe` is on your `PATH`.

5. **Verify installation**
   ```bash
   tesseract --version
   ```

## Running the Project

```bash
python3 -m src.main --input sample_images/sample_receipt.jpg --output-dir output/
```

### CLI Options

| Flag | Description | Default |
|---|---|---|
| `--input`, `-i` | Path to the input image (required) | — |
| `--output-dir`, `-o` | Directory to write results to | `output` |
| `--lang` | Tesseract language code | `eng` |
| `--no-clahe` | Disable CLAHE contrast enhancement | off |
| `--min-confidence` | Minimum per-word OCR confidence (0–100) to keep | `0` |
| `--verbose`, `-v` | Enable debug-level logging | off |

### Example

```bash
python3 -m src.main -i sample_images/sample_receipt.jpg -o output/ -v
```

This produces, inside `output/`:
- `1_warped.jpg` — perspective-corrected document
- `2_enhanced.jpg` — enhanced, binarized scan
- `3_text.txt` — extracted plain text
- `3_result.json` — structured OCR output (text, confidence, per-word boxes)

A run summary (word count, mean OCR confidence, elapsed time) is printed to
the terminal, and a full log is written to `scanner.log`.

## Testing

```bash
python3 -m pytest tests/ -v
```

The test suite generates synthetic document images on the fly (a skewed
page with printed text against a dark background) so it needs no external
sample files, and validates all three modules independently plus their
error-handling paths.

## Screenshots

See `assets/diagrams/` for architecture and workflow diagrams, and
`output_demo/` (generated after running the CLI) for example output images.
