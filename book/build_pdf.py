import os
from reportlab.pdfgen import canvas

from book.utils import register_fonts, PAGE_W, PAGE_H, BASE_DIR
from book.pages import (
    page_cover, page_intro, page_parts, page_sitting, page_posture,
    page_levels_intro, page_level, draw_page_number,
)


def build(output_path=None):
    output_path = output_path or os.path.join(BASE_DIR, "output", "soroban_book.pdf")
    register_fonts()

    c = canvas.Canvas(output_path, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("الحساب الذهني باستخدام السوروبان")

    pages = [
        page_cover,
        page_intro,
        page_parts,
        page_sitting,
        page_posture,
        page_levels_intro,
        lambda cv: page_level(cv, 0),
        lambda cv: page_level(cv, 1),
        lambda cv: page_level(cv, 2),
    ]
    page_num = 1
    for i, page_fn in enumerate(pages):
        page_fn(c)
        if i > 0:  # no footer number on the cover
            draw_page_number(c, page_num)
            page_num += 1
        c.showPage()

    c.save()
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    build()
