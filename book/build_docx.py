"""Word (.docx) export — plain logical Arabic text (Word shapes Arabic itself),
with RTL paragraph direction set explicitly on every paragraph via raw OOXML."""
import os

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from book.utils import BASE_DIR
from book.drawings import make_soroban_drawing, make_mascot_drawing
from book.raster import drawing_to_png
from book import content as C

TEAL = RGBColor(0x2C, 0x9B, 0x8A)
CORAL = RGBColor(0xE8, 0x61, 0x4A)
GOLD = RGBColor(0xF4, 0xA6, 0x23)
DARK = RGBColor(0x1A, 0x1A, 0x2E)
GRAY = RGBColor(0x5B, 0x5B, 0x6B)

FONT = "Cairo"


def set_paragraph_rtl(paragraph, align=WD_ALIGN_PARAGRAPH.RIGHT):
    """Mark a paragraph (and its runs) as right-to-left/bidi at the XML level —
    python-docx has no high-level API for this."""
    paragraph.alignment = align
    pPr = paragraph._p.get_or_add_pPr()
    bidi = OxmlElement("w:bidi")
    pPr.append(bidi)
    for run in paragraph.runs:
        rPr = run._r.get_or_add_rPr()
        rtl = OxmlElement("w:rtl")
        rPr.append(rtl)


def _set_run_font(run, name=FONT, size=12, bold=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), name)


def add_paragraph(doc, text, size=12, bold=False, color=None, align=WD_ALIGN_PARAGRAPH.RIGHT,
                   space_after=6, space_before=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    run = p.add_run(text)
    _set_run_font(run, size=size, bold=bold, color=color)
    set_paragraph_rtl(p, align=align)
    return p


def shade_cell(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_image_centered(doc, png_path, width_cm):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(png_path, width=Cm(width_cm))
    return p


def build(output_path=None):
    output_path = output_path or os.path.join(BASE_DIR, "output", "soroban_book.docx")
    tmp_dir = os.path.join(BASE_DIR, "output", "_docx_assets")
    os.makedirs(tmp_dir, exist_ok=True)

    soroban_png = drawing_to_png(make_soroban_drawing(380, 230), os.path.join(tmp_dir, "soroban.png"))
    soroban_png_big = drawing_to_png(make_soroban_drawing(500, 300, active_rod=2, active_value=6),
                                      os.path.join(tmp_dir, "soroban_big.png"))
    mascot_png = drawing_to_png(make_mascot_drawing(160, 180), os.path.join(tmp_dir, "mascot.png"))

    doc = Document()
    section = doc.sections[0]
    section.page_height, section.page_width = Cm(29.7), Cm(21.0)  # A4
    for attr in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(section, attr, Cm(1.8))

    # set document-level base font
    style = doc.styles["Normal"]
    style.font.name = FONT
    style.font.size = Pt(12)

    # ---------------- Cover -------------------------------------------------
    add_paragraph(doc, C.TITLE, size=26, bold=True, color=DARK,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=10)
    add_paragraph(doc, C.SUBTITLE, size=14, bold=True, color=TEAL,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    add_paragraph(doc, f"تأليف: {C.AUTHOR_NAME}", size=12, color=GRAY,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    add_image_centered(doc, soroban_png, width_cm=11)

    badge_table = doc.add_table(rows=1, cols=3)
    badge_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    badge_colors = ["F4A623", "E8614A", "2C9B8A"]
    for i, level in enumerate(C.LEVELS):
        cell = badge_table.cell(0, i)
        shade_cell(cell, badge_colors[i])
        cp = cell.paragraphs[0]
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = cp.add_run(level)
        _set_run_font(run, size=13, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
        set_paragraph_rtl(cp, align=WD_ALIGN_PARAGRAPH.CENTER)

    doc.add_page_break()

    # ---------------- Introduction -------------------------------------------
    add_paragraph(doc, C.INTRO_TITLE, size=20, bold=True, color=DARK, space_after=12)
    add_paragraph(doc, C.INTRO_TEXT, size=12.5, color=DARK, space_after=14)

    add_image_centered(doc, soroban_png, width_cm=9)
    add_paragraph(doc, C.INTRO_IMAGE_CAPTION, size=10.5, color=GRAY,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)

    add_paragraph(doc, C.BENEFITS_TITLE, size=15, bold=True, color=CORAL, space_after=8)
    for benefit in C.BENEFITS:
        add_paragraph(doc, f"• {benefit}", size=12, color=DARK, space_after=6)

    doc.add_page_break()

    # ---------------- Posture -------------------------------------------------
    add_paragraph(doc, C.POSTURE_TITLE, size=20, bold=True, color=DARK, space_after=10)
    add_image_centered(doc, mascot_png, width_cm=4.5)
    add_paragraph(doc, C.MASCOT_SPEECH, size=12.5, bold=True, color=TEAL,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    for i, (step_title, step_desc) in enumerate(C.POSTURE_STEPS, start=1):
        add_paragraph(doc, f"{i}. {step_title}", size=13.5, bold=True, color=TEAL, space_after=2)
        add_paragraph(doc, step_desc, size=11.5, color=GRAY, space_after=12)

    doc.add_page_break()

    # ---------------- Parts -------------------------------------------------
    add_paragraph(doc, C.PARTS_TITLE, size=20, bold=True, color=DARK, space_after=12)
    add_image_centered(doc, soroban_png_big, width_cm=13)
    doc.add_paragraph()

    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    shade_cell(hdr[0], "2C9B8A")
    shade_cell(hdr[1], "2C9B8A")
    headers = ["الوصف", "الجزء"]
    for cell, text in zip(hdr, headers):
        cp = cell.paragraphs[0]
        run = cp.add_run(text)
        _set_run_font(run, size=12, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
        set_paragraph_rtl(cp, align=WD_ALIGN_PARAGRAPH.CENTER)

    for name, desc in C.PARTS:
        row = table.add_row().cells
        cp_desc = row[0].paragraphs[0]
        run = cp_desc.add_run(desc)
        _set_run_font(run, size=11.5, color=DARK)
        set_paragraph_rtl(cp_desc, align=WD_ALIGN_PARAGRAPH.RIGHT)

        cp_name = row[1].paragraphs[0]
        run = cp_name.add_run(name)
        _set_run_font(run, size=12, bold=True, color=TEAL)
        set_paragraph_rtl(cp_name, align=WD_ALIGN_PARAGRAPH.RIGHT)

    # set the whole document's default text direction (table grid order, etc.)
    sectPr = section._sectPr
    bidi_sect = OxmlElement("w:bidi")
    sectPr.append(bidi_sect)

    doc.save(output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    build()
