const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, ImageRun,
  Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType,
  PageBreak, BorderStyle, Numbering, LevelFormat, convertInchesToTwip
} = require("docx");
const fs = require("fs");

const PAGE_W = 12240, PAGE_H = 15840; // US Letter

function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } });
}
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 160 } });
}
function bullet(text) {
  return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 80 } });
}
function image(path, width, height, caption) {
  const buf = fs.readFileSync(path);
  const maxW = 560; // pts-ish scaling within page margins
  const maxH = 620; // keep every image within one page's usable height
  const scale = Math.min(1, maxW / width, maxH / height);
  const children = [
    new Paragraph({
      children: [new ImageRun({ data: buf, transformation: { width: width * scale, height: height * scale }, type: path.endsWith(".png") ? "png" : "jpg" })],
      alignment: AlignmentType.CENTER,
      spacing: { before: 120, after: 60 },
    }),
  ];
  if (caption) {
    children.push(new Paragraph({
      children: [new TextRun({ text: caption, italics: true, size: 18 })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 },
    }));
  }
  return children;
}
function codeBlock(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: "Consolas", size: 18 })],
    shading: { type: ShadingType.CLEAR, fill: "F1EFE8" },
    spacing: { after: 200 },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: "D3D1C7" }, bottom: { style: BorderStyle.SINGLE, size: 2, color: "D3D1C7" }, left: { style: BorderStyle.SINGLE, size: 2, color: "D3D1C7" }, right: { style: BorderStyle.SINGLE, size: 2, color: "D3D1C7" } },
  });
}
function simpleTable(headers, rows) {
  const colWidth = Math.floor((PAGE_W - convertInchesToTwip(2)) / headers.length);
  const mkCell = (text, bold) => new TableCell({
    width: { size: colWidth, type: WidthType.DXA },
    shading: bold ? { type: ShadingType.CLEAR, fill: "E6F1FB" } : undefined,
    children: [new Paragraph({ children: [new TextRun({ text: String(text), bold: !!bold })] })],
  });
  return new Table({
    columnWidths: headers.map(() => colWidth),
    width: { size: headers.length * colWidth, type: WidthType.DXA },
    rows: [
      new TableRow({ children: headers.map(hd => mkCell(hd, true)) }),
      ...rows.map(r => new TableRow({ children: r.map(c => mkCell(c, false)) })),
    ],
  });
}

const sections = [];

// ---------------- COVER PAGE ----------------
sections.push(
  new Paragraph({ text: "", spacing: { before: 2000 } }),
  new Paragraph({
    children: [new TextRun({ text: "Document Scanner + OCR Pipeline", bold: true, size: 48 })],
    alignment: AlignmentType.CENTER, spacing: { after: 300 },
  }),
  new Paragraph({
    children: [new TextRun({ text: "A Computer Vision Project Report", size: 28 })],
    alignment: AlignmentType.CENTER, spacing: { after: 800 },
  }),
  new Paragraph({
    children: [new TextRun({ text: "Course: CSE3010 – Computer Vision", size: 24 })],
    alignment: AlignmentType.CENTER, spacing: { after: 120 },
  }),
  new Paragraph({
    children: [new TextRun({ text: "Assignment: Build Your Own Project (VITyarthi)", size: 24 })],
    alignment: AlignmentType.CENTER, spacing: { after: 120 },
  }),
  new Paragraph({
    children: [new TextRun({ text: "Institution: VIT Bhopal University, School of Computing Science and Engineering", size: 22 })],
    alignment: AlignmentType.CENTER, spacing: { after: 600 },
  }),
  new Paragraph({
    children: [new TextRun({ text: "Submitted by: Sharanya", size: 24 })],
    alignment: AlignmentType.CENTER, spacing: { after: 120 },
  }),
  new Paragraph({
    children: [new TextRun({ text: "[Registration Number: __________]", size: 20, italics: true, color: "5F5E5A" })],
    alignment: AlignmentType.CENTER, spacing: { after: 800 },
  }),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---------------- 1. Introduction ----------------
sections.push(h1("1. Introduction"));
sections.push(p(
  "Photographs of physical documents taken with a phone camera are almost never perfectly aligned: they are skewed, perspective-distorted, and unevenly lit. This project builds a command-line pipeline that takes such a photo and produces a clean, flattened, high-contrast scan, then extracts the document's text via Optical Character Recognition (OCR). The pipeline is organized into three independent, testable modules that map directly onto the image-processing and geometric-transform concepts covered in the CSE3010 syllabus: image formation and enhancement, homography-based perspective correction, and feature/contour-based boundary detection."
));

// ---------------- 2. Problem Statement ----------------
sections.push(h1("2. Problem Statement"));
sections.push(p(
  "There is a need for a lightweight, GUI-free tool that converts a raw photo of a document into (a) a flattened, readable scan and (b) accurate, structured machine-readable text — without relying on a phone app or cloud service. This project addresses that need with a fully local, scriptable pipeline runnable from a terminal."
));

// ---------------- 3. Functional Requirements ----------------
sections.push(h1("3. Functional Requirements"));
sections.push(p("The system implements three major functional modules, as required by the assignment brief:"));
sections.push(bullet("Module 1 – Document Detection & Perspective Correction: locates the document boundary in the input photo (Canny edge detection + contour approximation) and applies a homography-based perspective warp to produce a top-down view."));
sections.push(bullet("Module 2 – Image Enhancement & Binarization: converts the warped image to grayscale, applies CLAHE contrast equalization and denoising, then adaptive thresholding to produce a clean, scanner-quality black-and-white page."));
sections.push(bullet("Module 3 – OCR Text Extraction & Structured Output: runs Tesseract OCR on the enhanced image and emits both plain text and a structured JSON file containing per-word text, confidence score, and bounding box."));
sections.push(p("Input/output structure: the CLI accepts a single image path (--input) and an output directory (--output-dir); it writes the intermediate warped image, the enhanced/binarized image, the extracted text file, and a structured JSON result."));
sections.push(p("Workflow: read image → detect & warp → enhance & binarize → OCR extract → write outputs → print summary. See the Process Flow diagram in Section 6."));

// ---------------- 4. Non-Functional Requirements ----------------
sections.push(h1("4. Non-Functional Requirements"));
sections.push(simpleTable(
  ["Requirement", "How it is addressed"],
  [
    ["Performance", "Image is resized before contour search (fixed 800px height) to bound processing cost; full pipeline runs in well under a second for typical inputs."],
    ["Reliability", "A DocumentNotFoundError fallback path uses the full frame if no 4-point contour is found, so the pipeline degrades gracefully instead of crashing."],
    ["Usability", "Single CLI entry point with argparse, clear --help text, sensible defaults, and a printed run summary (word count, confidence, elapsed time)."],
    ["Maintainability", "Each module (detector, enhancer, OCR) is a separate file with a narrow, documented public API, so any module can be modified or swapped independently."],
    ["Error handling", "Every module validates its inputs (empty/invalid images) and raises specific exceptions; main.py catches and logs these without a raw stack trace reaching the user."],
    ["Logging / monitoring", "Centralized logging (utils.setup_logging) writes timestamped, leveled logs to both the console and scanner.log."],
    ["Resource efficiency", "Uses OpenCV's headless build (no GUI dependencies) and releases all intermediate arrays automatically via Python's garbage collector; no persistent state between runs."],
  ]
));

// ---------------- 5. System Architecture ----------------
sections.push(h1("5. System Architecture"));
sections.push(p("The CLI (main.py) orchestrates three independent modules, each with a single responsibility, plus a shared utilities module for logging and I/O helpers."));
sections.push(...image("assets/diagrams/system_architecture.png", 1865, 307, "Figure 1: System architecture — module responsibilities and data handed between them."));

// ---------------- 6. Design Diagrams ----------------
sections.push(h1("6. Design Diagrams"));

sections.push(h2("6.1 Process Flow / Workflow Diagram"));
sections.push(...image("assets/diagrams/process_flow.png", 437, 1148, "Figure 2: End-to-end processing workflow, including the contour-not-found fallback path."));

sections.push(h2("6.2 Use Case Diagram"));
sections.push(...image("assets/diagrams/use_case_diagram.png", 486, 546, "Figure 3: Use cases available to the student/evaluator running the CLI."));

sections.push(h2("6.3 Class / Component Diagram"));
sections.push(...image("assets/diagrams/class_diagram.png", 1256, 546, "Figure 4: Module-level components, their public methods, and the data classes they produce."));

sections.push(h2("6.4 Sequence Diagram"));
sections.push(...image("assets/diagrams/sequence_diagram.png", 929, 709, "Figure 5: Call sequence for a single CLI invocation, from input image to written outputs."));

sections.push(h2("6.5 Database / Storage Design"));
sections.push(p("Not applicable — this project is a stateless, file-in/file-out CLI pipeline and does not use a database. Outputs are written directly to the filesystem as image, text, and JSON files (see Section 3)."));

// ---------------- 7. Design Decisions & Rationale ----------------
sections.push(h1("7. Design Decisions & Rationale"));
sections.push(bullet("Three separate modules instead of one script: keeps each concept (geometry, image processing, OCR) independently testable and replaceable — e.g. Module 3 could be swapped for a cloud OCR API without touching Modules 1–2."));
sections.push(bullet("Fallback-to-full-frame on failed detection: chosen over hard-failing so the pipeline is robust to photos where the document fills the whole frame or has low-contrast edges."));
sections.push(bullet("Adaptive thresholding over a global threshold: documents photographed under uneven lighting have local brightness gradients that a single global threshold cannot handle well."));
sections.push(bullet("JSON structured output alongside plain text: enables downstream automation (e.g. filtering by confidence, locating specific words) rather than only a human-readable transcript."));
sections.push(bullet("CLI-only (argparse), no GUI: satisfies the assignment's command-line-executable requirement and keeps the tool scriptable/automatable."));

// ---------------- 8. Implementation Details ----------------
sections.push(h1("8. Implementation Details"));
sections.push(p("Language & libraries: Python 3, OpenCV (opencv-python-headless) for all image processing and geometric transforms, NumPy for array operations, and pytesseract as a thin wrapper around the Tesseract OCR engine."));
sections.push(h2("8.1 Module 1 — document_detector.py"));
sections.push(p("Resizes the input for fast contour search, applies Gaussian blur + Canny edge detection, finds the largest contours, and keeps the first one that approximates to a 4-point polygon (cv2.approxPolyDP). Corners are ordered (top-left, top-right, bottom-right, bottom-left) and a perspective transform matrix is computed with cv2.getPerspectiveTransform, then applied with cv2.warpPerspective."));
sections.push(h2("8.2 Module 2 — enhancer.py"));
sections.push(p("Converts to grayscale, optionally applies CLAHE (contrast-limited adaptive histogram equalization) to correct uneven lighting, denoises with cv2.fastNlMeansDenoising, and binarizes with cv2.adaptiveThreshold (Gaussian-weighted, block size 25)."));
sections.push(h2("8.3 Module 3 — ocr_extractor.py"));
sections.push(p("Calls pytesseract.image_to_string for the plain-text transcript and pytesseract.image_to_data for per-word bounding boxes and confidence scores, aggregating them into an OCRResult dataclass with a to_json() serializer."));
sections.push(h2("8.4 CLI — main.py"));
sections.push(p("Wires the three modules together behind an argparse interface, writes all intermediate and final artifacts to the chosen output directory, and prints a run summary."));

// ---------------- 9. Screenshots / Results ----------------
sections.push(h1("9. Screenshots / Results"));
sections.push(p("The pipeline was validated on a synthetically generated test document (a skewed page with printed text on a dark background, generated in tests/test_pipeline.py) to provide a deterministic, reproducible demonstration."));
sections.push(...image("output_demo/1_warped.jpg", 586, 786, "Figure 6: Module 1 output — perspective-corrected, de-skewed document."));
sections.push(...image("output_demo/2_enhanced.jpg", 586, 786, "Figure 7: Module 2 output — enhanced, binarized scan ready for OCR."));
sections.push(p("Module 3 (OCR) output on this sample:"));
sections.push(codeBlock('{\n  "text": "HELLO WORLD\\n\\nComputer Vision Test",\n  "mean_confidence": 96.0,\n  "word_count": 5,\n  "words": [ { "text": "HELLO", "confidence": 96.0, "bbox": {...} }, ... ]\n}'));
sections.push(p("Run summary printed by the CLI:"));
sections.push(codeBlock("Words extracted:     5\nMean OCR confidence: 96.0%\nTime elapsed:        0.59s"));

// ---------------- 10. Testing Approach ----------------
sections.push(h1("10. Testing Approach"));
sections.push(p("Automated unit tests (tests/test_pipeline.py, run via pytest) cover all three modules:"));
sections.push(bullet("Document Detector: verifies a valid DetectionResult is returned for a normal image, that an empty image raises DocumentNotFoundError, and that a blank/featureless image correctly falls back to using the full frame."));
sections.push(bullet("Enhancer: verifies output is strictly binary (0/255 pixel values only) and that an empty image raises ValueError."));
sections.push(bullet("OCR Extractor: verifies text is extracted from a synthetic page, mean_confidence is a float, an empty image raises ValueError, and JSON serialization includes expected fields."));
sections.push(p("All 8 tests pass. Synthetic test images are generated on the fly (no external fixture files needed), keeping the test suite fully self-contained and deterministic. The pipeline was additionally validated end-to-end via the CLI itself (Section 9)."));

// ---------------- 11. Challenges Faced ----------------
sections.push(h1("11. Challenges Faced"));
sections.push(bullet("Robust corner ordering: perspective warps break if the four detected corners aren't consistently ordered (TL/TR/BR/BL); solved using the sum/difference-of-coordinates trick."));
sections.push(bullet("Handling failed contour detection gracefully: rather than letting the pipeline crash on low-contrast or edge-filling images, a full-frame fallback path was added and unit-tested explicitly."));
sections.push(bullet("Uneven lighting in photographed documents: a plain global threshold produced patchy results; switching to adaptive Gaussian thresholding (with CLAHE beforehand) fixed this."));
sections.push(bullet("Deterministic testing without real photos: building a synthetic-document generator (skewed page + printed text) so tests don't depend on external image fixtures or manual photography."));

// ---------------- 12. Learnings & Key Takeaways ----------------
sections.push(h1("12. Learnings & Key Takeaways"));
sections.push(bullet("Practical experience applying homography/perspective-transform theory (Module 2 of the syllabus) to a real image, not just synthetic point sets."));
sections.push(bullet("Adaptive, locally-aware image processing (CLAHE, adaptive thresholding) matters far more than global operations once inputs come from uncontrolled, real-world conditions like phone photography."));
sections.push(bullet("Designing for graceful degradation (fallback paths, input validation) is as important as the 'happy path' algorithm for a tool meant to be run by someone else."));
sections.push(bullet("A clean module boundary (detector → enhancer → OCR) made independent unit testing straightforward and would make it easy to later swap any one stage (e.g. a different OCR engine) without touching the rest."));

// ---------------- 13. Future Enhancements ----------------
sections.push(h1("13. Future Enhancements"));
sections.push(bullet("Multi-page / batch processing: accept a directory of images or a PDF and process all pages in one run."));
sections.push(bullet("Automatic rotation correction: detect and correct 90°/180° rotated documents in addition to perspective skew."));
sections.push(bullet("Layout-aware OCR: group extracted words into lines/paragraphs/table cells instead of a flat word list."));
sections.push(bullet("Configurable OCR backend: abstract Module 3 behind an interface so a cloud OCR API can be swapped in for higher accuracy on handwriting."));

// ---------------- 14. References ----------------
sections.push(h1("14. References"));
sections.push(bullet("R. Szeliski, Computer Vision: Algorithms and Applications, Springer-Verlag London Limited, 2011."));
sections.push(bullet("R. Hartley and A. Zisserman, Multiple View Geometry in Computer Vision, 2nd Edition, Cambridge University Press, 2004."));
sections.push(bullet("OpenCV Documentation: https://docs.opencv.org/"));
sections.push(bullet("Tesseract OCR / pytesseract Documentation: https://github.com/tesseract-ocr/tesseract , https://github.com/madmaze/pytesseract"));
sections.push(bullet("CSE3010 Computer Vision course syllabus, VIT Bhopal."));

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: PAGE_H } } },
    children: sections,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("report/project_report.docx", buf);
  console.log("Report written.");
});
