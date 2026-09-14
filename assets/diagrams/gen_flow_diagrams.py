"""Generate System Architecture and Process Flow diagrams with Graphviz."""
import graphviz

# ---------------- System Architecture Diagram ----------------
arch = graphviz.Digraph("architecture", format="png")
arch.attr(rankdir="LR", bgcolor="white", fontname="Helvetica", pad="0.4")
arch.attr("node", shape="box", style="rounded,filled", fontname="Helvetica",
          fontsize="12", margin="0.25,0.15")
arch.attr("edge", fontname="Helvetica", fontsize="10")

arch.node("cli", "CLI\n(main.py)", fillcolor="#E6F1FB", color="#185FA5")
arch.node("m1", "Module 1\nDocument Detector\n(document_detector.py)", fillcolor="#EEEDFE", color="#534AB7")
arch.node("m2", "Module 2\nEnhancer\n(enhancer.py)", fillcolor="#E1F5EE", color="#0F6E56")
arch.node("m3", "Module 3\nOCR Extractor\n(ocr_extractor.py)", fillcolor="#FAECE7", color="#993C1D")
arch.node("util", "utils.py\n(logging, I/O helpers)", fillcolor="#F1EFE8", color="#5F5E5A")
arch.node("out", "Outputs\nwarped.jpg / enhanced.jpg\ntext.txt / result.json\nscanner.log", shape="note",
          fillcolor="white", color="#5F5E5A")

arch.edge("cli", "m1", label="input image")
arch.edge("m1", "m2", label="warped image")
arch.edge("m2", "m3", label="binarized image")
arch.edge("m3", "out", label="text + JSON")
arch.edge("util", "cli", style="dashed", dir="none")
arch.edge("util", "m1", style="dashed", dir="none")
arch.edge("util", "m2", style="dashed", dir="none")
arch.edge("util", "m3", style="dashed", dir="none")

arch.render("system_architecture", cleanup=True)

# ---------------- Process Flow / Workflow Diagram ----------------
flow = graphviz.Digraph("workflow", format="png")
flow.attr(rankdir="TB", bgcolor="white", fontname="Helvetica", pad="0.4")
flow.attr("node", shape="box", style="rounded,filled", fontname="Helvetica",
          fontsize="12", margin="0.25,0.15")

flow.node("start", "User runs CLI\nwith --input image", shape="ellipse", fillcolor="#F1EFE8", color="#5F5E5A")
flow.node("read", "Read image\n(OpenCV imread)", fillcolor="#E6F1FB", color="#185FA5")
flow.node("detect", "Detect document contour\n(Canny + contour approx)", fillcolor="#EEEDFE", color="#534AB7")
flow.node("found", "Contour found?", shape="diamond", fillcolor="#FAEEDA", color="#854F0B")
flow.node("warp", "Perspective warp\n(homography)", fillcolor="#EEEDFE", color="#534AB7")
flow.node("fallback", "Fallback: use\nfull frame", fillcolor="#FCEBEB", color="#A32D2D")
flow.node("enhance", "Grayscale + CLAHE +\ndenoise + adaptive threshold", fillcolor="#E1F5EE", color="#0F6E56")
flow.node("ocr", "Run Tesseract OCR\n(text + word confidences)", fillcolor="#FAECE7", color="#993C1D")
flow.node("write", "Write outputs\n(images, .txt, .json, log)", fillcolor="#F1EFE8", color="#5F5E5A")
flow.node("end", "Print summary,\nexit", shape="ellipse", fillcolor="#F1EFE8", color="#5F5E5A")

flow.edge("start", "read")
flow.edge("read", "detect")
flow.edge("detect", "found")
flow.edge("found", "warp", label="yes")
flow.edge("found", "fallback", label="no")
flow.edge("warp", "enhance")
flow.edge("fallback", "enhance")
flow.edge("enhance", "ocr")
flow.edge("ocr", "write")
flow.edge("write", "end")

flow.render("process_flow", cleanup=True)

print("Diagrams generated.")
