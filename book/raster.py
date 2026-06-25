"""Rasterize reportlab vector Drawings to PNG (for embedding in docx) via a
one-shot single-drawing PDF + poppler's pdftoppm, since renderPM needs an
extra native backend (rlPyCairo) that isn't installed in this environment."""
import os
import subprocess
import tempfile
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF


def drawing_to_png(drawing, out_path, dpi=200):
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = os.path.join(tmp, "d.pdf")
        c = canvas.Canvas(pdf_path, pagesize=(drawing.width, drawing.height))
        renderPDF.draw(drawing, c, 0, 0)
        c.showPage()
        c.save()

        out_base = out_path[:-4] if out_path.lower().endswith(".png") else out_path
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(dpi), "-singlefile", pdf_path, out_base],
            check=True,
        )
    return out_path
