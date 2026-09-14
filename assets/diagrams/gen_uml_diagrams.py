"""Generate simplified UML diagrams: Use Case, Class, Sequence."""
import graphviz

# ---------------- Use Case Diagram ----------------
uc = graphviz.Digraph("usecase", format="png")
uc.attr(rankdir="LR", bgcolor="white", fontname="Helvetica", pad="0.4")
uc.node("actor", "Student /\nEvaluator", shape="plaintext", fontname="Helvetica", fontsize="12")
uc.attr("node", shape="ellipse", style="filled", fillcolor="#E6F1FB", color="#185FA5",
        fontname="Helvetica", fontsize="11", width="2.4")

uc.node("uc1", "Scan document image\nvia CLI")
uc.node("uc2", "Correct perspective /\nde-skew document")
uc.node("uc3", "Enhance & binarize\nimage")
uc.node("uc4", "Extract text via OCR")
uc.node("uc5", "View structured\noutput (JSON/txt)")
uc.node("uc6", "Review logs for\nerrors/diagnostics")

for uc_node in ["uc1", "uc2", "uc3", "uc4", "uc5", "uc6"]:
    uc.edge("actor", uc_node)

uc.render("use_case_diagram", cleanup=True)

# ---------------- Class Diagram ----------------
cls = graphviz.Digraph("classdiagram", format="png")
cls.attr(rankdir="TB", bgcolor="white", fontname="Helvetica", pad="0.4")
cls.attr("node", shape="record", fontname="Helvetica", fontsize="10", style="filled", fillcolor="#F7F7F5")

cls.node("detector", "{DocumentDetector (module)|"
          "+ find_document_contour(image): ndarray|"
          "+ detect_and_warp(image): DetectionResult}")
cls.node("detresult", "{DetectionResult|"
          "+ warped: ndarray|+ corners: ndarray|+ original_shape: tuple}")
cls.node("enhancer", "{Enhancer (module)|"
          "+ enhance_document(image): ndarray|+ sharpen(image): ndarray}")
cls.node("ocr", "{OCRExtractor (module)|"
          "+ extract_text(image, lang): OCRResult}")
cls.node("ocrresult", "{OCRResult|"
          "+ text: str|+ mean_confidence: float|+ word_count: int|+ words: list|"
          "+ to_json(): str}")
cls.node("cli", "{CLI (main.py)|"
          "+ build_arg_parser(): ArgumentParser|+ run_pipeline(args): int}")
cls.node("utils", "{utils (module)|"
          "+ setup_logging()|+ ensure_dir(path)|+ is_supported_image(path): bool}")

cls.edge("cli", "detector", label="uses")
cls.edge("cli", "enhancer", label="uses")
cls.edge("cli", "ocr", label="uses")
cls.edge("cli", "utils", label="uses")
cls.edge("detector", "detresult", label="produces", style="dashed")
cls.edge("ocr", "ocrresult", label="produces", style="dashed")

cls.render("class_diagram", cleanup=True)

# ---------------- Sequence Diagram ----------------
seq = graphviz.Digraph("sequence", format="png")
seq.attr(rankdir="LR", bgcolor="white", fontname="Helvetica", pad="0.4", nodesep="0.8")
seq.attr("node", shape="box", style="filled", fillcolor="#F1EFE8", fontname="Helvetica", fontsize="11")

# Using a simple left-to-right chain to represent the call sequence
seq.node("user", "User\n(CLI)")
seq.node("main", "main.py")
seq.node("mod1", "document_\ndetector")
seq.node("mod2", "enhancer")
seq.node("mod3", "ocr_\nextractor")
seq.node("fs", "File System\n(outputs)")

seq.edge("user", "main", label="1: run --input img.jpg")
seq.edge("main", "mod1", label="2: detect_and_warp(img)")
seq.edge("mod1", "main", label="3: DetectionResult", style="dashed")
seq.edge("main", "mod2", label="4: enhance_document(warped)")
seq.edge("mod2", "main", label="5: binarized image", style="dashed")
seq.edge("main", "mod3", label="6: extract_text(enhanced)")
seq.edge("mod3", "main", label="7: OCRResult", style="dashed")
seq.edge("main", "fs", label="8: write images/txt/json")
seq.edge("main", "user", label="9: print summary", style="dashed")

seq.render("sequence_diagram", cleanup=True)

print("UML diagrams generated.")
