import os
from reportlab.pdfgen import canvas

from book.utils import register_fonts, PAGE_W, PAGE_H, BASE_DIR
from book.pages import page_cover, page_intro, page_posture, page_parts


def build(output_path=None):
    output_path = output_path or os.path.join(BASE_DIR, "output", "soroban_book.pdf")
    register_fonts()

    c = canvas.Canvas(output_path, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("الحساب الذهني باستخدام السوروبان")

    for page_fn in (page_cover, page_intro, page_posture, page_parts):
        page_fn(c)
        c.showPage()

    c.save()
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    build()
