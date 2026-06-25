"""Word (.docx) export — plain logical Arabic text (Word shapes Arabic itself),
with RTL paragraph direction set explicitly on every paragraph via raw OOXML."""
import os

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from book.utils import BASE_DIR, IMAGE_DIR
from book.drawings import (
    make_soroban_drawing, make_mascot_drawing, make_posture_drawing, make_digit_drawing,
    NAVY as DRAW_NAVY,
)
from book.raster import drawing_to_png
from book import content as C

NAVY = RGBColor(0x1C, 0x3D, 0x5F)
NAVY_LIGHT = RGBColor(0x3E, 0x64, 0x88)
AMBER = RGBColor(0xC6, 0x8A, 0x3E)
TEAL = RGBColor(0x2E, 0x8B, 0x7F)
CORAL = RGBColor(0xD8, 0x59, 0x3F)
SILVER = RGBColor(0x8A, 0x95, 0xA0)
DARK = NAVY
GRAY = RGBColor(0x5B, 0x5B, 0x6B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xC8, 0xD0, 0xD8)

NAVY_HEX = "1C3D5F"
LEVEL_HEX = ["C68A3E", "2E8B7F", "1C3D5F"]

FONT = "Cairo"


def _img(name):
    return os.path.join(IMAGE_DIR, name)


def _arabic_num(n):
    mapping = {"0": "٠", "1": "١", "2": "٢", "3": "٣", "4": "٤",
               "5": "٥", "6": "٦", "7": "٧", "8": "٨", "9": "٩"}
    return "".join(mapping.get(ch, ch) for ch in str(n))


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


def add_paragraph(container, text, size=12, bold=False, color=None, align=WD_ALIGN_PARAGRAPH.RIGHT,
                   space_after=6, space_before=0):
    p = container.add_paragraph()
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


def add_image_centered(container, png_path, width_cm):
    p = container.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(png_path, width=Cm(width_cm))
    return p


def build(output_path=None):
    output_path = output_path or os.path.join(BASE_DIR, "output", "soroban_book.docx")
    tmp_dir = os.path.join(BASE_DIR, "output", "_docx_assets")
    os.makedirs(tmp_dir, exist_ok=True)

    soroban_png_big = drawing_to_png(make_soroban_drawing(500, 300, active_rod=2, active_value=6),
                                      os.path.join(tmp_dir, "soroban_big.png"))
    mascot_png = drawing_to_png(make_mascot_drawing(160, 180, body_color=DRAW_NAVY),
                                os.path.join(tmp_dir, "mascot.png"))
    posture_ok_png = drawing_to_png(make_posture_drawing(240, 250, correct=True),
                                     os.path.join(tmp_dir, "posture_ok.png"))
    posture_bad_png = drawing_to_png(make_posture_drawing(240, 250, correct=False),
                                      os.path.join(tmp_dir, "posture_bad.png"))
    soroban_photo = _img("soroban_photo.jpg")
    soroban_desk = _img("soroban_desk.jpg")

    doc = Document()
    section = doc.sections[0]
    section.page_height, section.page_width = Cm(29.7), Cm(21.0)  # A4
    for attr in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(section, attr, Cm(1.8))

    # set document-level base font
    style = doc.styles["Normal"]
    style.font.name = FONT
    style.font.size = Pt(12)

    # ---------------- Cover (dark, dense — mirrors the PDF cover) -----------
    cover_table = doc.add_table(rows=1, cols=1)
    cover_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cover_cell = cover_table.cell(0, 0)
    shade_cell(cover_cell, "1A1A2E")
    tcPr = cover_cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for side in ("top", "bottom", "start", "end"):
        node = OxmlElement(f"w:{side}")
        node.set(qn("w:w"), "300")
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)

    add_paragraph(cover_cell, C.COVER_KICKER, size=12, bold=True, color=AMBER,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=6)
    add_paragraph(cover_cell, C.COVER_LINE_1, size=28, bold=True, color=WHITE,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_paragraph(cover_cell, C.COVER_LINE_2, size=15, bold=True, color=RGBColor(0x9F, 0xB6, 0xCC),
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_paragraph(cover_cell, C.COVER_LINE_3, size=28, bold=True, color=WHITE,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_image_centered(cover_cell, soroban_photo, width_cm=12)
    cover_cell.paragraphs[-1].paragraph_format.space_after = Pt(14)

    badge_table = cover_cell.add_table(rows=1, cols=3)
    badge_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # RTL: level 1 on the right
    for slot, i in enumerate([2, 1, 0]):
        cell = badge_table.cell(0, slot)
        shade_cell(cell, LEVEL_HEX[i])
        add_paragraph(cell, C.LEVEL_ORDINALS[i], size=10, bold=True,
                      color=WHITE, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
        add_paragraph(cell, C.LEVEL_DESCRIPTIONS[i], size=8.5, bold=False,
                      color=WHITE, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)

    cover_cell.add_paragraph().paragraph_format.space_after = Pt(6)
    add_paragraph(cover_cell, C.AUTHOR_PREFIX, size=11, bold=True, color=AMBER,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=2)
    add_paragraph(cover_cell, C.AUTHOR_NAME, size=15, bold=True, color=WHITE,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    for cred in C.AUTHOR_CREDENTIALS:
        add_paragraph(cover_cell, cred, size=10.5, color=LIGHT_GRAY,
                      align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)

    doc.add_page_break()

    # ---------------- Introduction -------------------------------------------
    add_paragraph(doc, C.INTRO_TITLE, size=20, bold=True, color=NAVY, space_after=12)
    add_paragraph(doc, C.INTRO_TEXT, size=12.5, color=DARK, space_after=14)

    add_image_centered(doc, soroban_desk, width_cm=12)
    add_paragraph(doc, C.INTRO_IMAGE_CAPTION, size=10.5, color=GRAY,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)

    add_paragraph(doc, C.BENEFITS_TITLE, size=15, bold=True, color=AMBER, space_after=8)
    for benefit in C.BENEFITS:
        add_paragraph(doc, f"• {benefit}", size=12, color=DARK, space_after=6)

    doc.add_page_break()

    # ---------------- Sitting posture (correct vs. incorrect) ----------------
    add_paragraph(doc, C.SITTING_TITLE, size=20, bold=True, color=DARK, space_after=8)
    add_paragraph(doc, C.SITTING_INTRO, size=12.5, color=GRAY, space_after=14)

    posture_table = doc.add_table(rows=1, cols=2)
    posture_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    posture_specs = [
        (posture_bad_png, C.INCORRECT_LABEL, C.INCORRECT_POINTS, "D8593F"),
        (posture_ok_png, C.CORRECT_LABEL, C.CORRECT_POINTS, "2E8B7F"),
    ]
    for col, (png_path, label, points, hex_color) in enumerate(posture_specs):
        cell = posture_table.cell(0, col)
        add_paragraph(cell, label, size=13, bold=True, color=RGBColor(
            int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)),
            align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
        add_image_centered(cell, png_path, width_cm=5)
        for point in points:
            add_paragraph(cell, f"• {point}", size=10.5, color=DARK,
                          align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)

    doc.add_page_break()

    # ---------------- Usage steps --------------------------------------------
    add_paragraph(doc, C.USAGE_TITLE, size=20, bold=True, color=AMBER, space_after=10)
    add_image_centered(doc, mascot_png, width_cm=4.5)
    add_paragraph(doc, C.MASCOT_SPEECH, size=12.5, bold=True, color=NAVY,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    for i, (step_title, step_desc) in enumerate(C.POSTURE_STEPS, start=1):
        add_paragraph(doc, f"{i}. {step_title}", size=13.5, bold=True, color=NAVY, space_after=2)
        add_paragraph(doc, step_desc, size=11.5, color=GRAY, space_after=12)

    add_paragraph(doc, C.USAGE_TIP, size=11.5, bold=True, color=AMBER,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=8)

    doc.add_page_break()

    # ---------------- Parts -------------------------------------------------
    add_paragraph(doc, C.PARTS_TITLE, size=20, bold=True, color=AMBER, space_after=12)
    add_image_centered(doc, soroban_png_big, width_cm=13)
    doc.add_paragraph()

    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    shade_cell(hdr[0], NAVY_HEX)
    shade_cell(hdr[1], NAVY_HEX)
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
        _set_run_font(run, size=12, bold=True, color=NAVY)
        set_paragraph_rtl(cp_name, align=WD_ALIGN_PARAGRAPH.RIGHT)

    doc.add_page_break()

    # ---------------- Levels / curriculum ------------------------------------
    add_paragraph(doc, C.LEVELS_INTRO_TITLE, size=20, bold=True, color=NAVY, space_after=10)
    add_paragraph(doc, C.LEVELS_INTRO_TEXT, size=12.5, color=DARK, space_after=14)

    for idx, lp in enumerate(C.LEVEL_PAGES):
        accent_hex = LEVEL_HEX[idx]
        accent = RGBColor(int(accent_hex[0:2], 16), int(accent_hex[2:4], 16), int(accent_hex[4:6], 16))
        add_paragraph(doc, f"{lp['ordinal']} — {lp['name']} ({lp['range']})",
                      size=15, bold=True, color=accent, space_before=8, space_after=4)
        add_paragraph(doc, lp["objective"], size=11.5, color=DARK, space_after=6)
        for skill in lp["skills"]:
            add_paragraph(doc, f"◆ {skill}", size=11, color=DARK, space_after=3)

        # digit -> soroban exercise as a simple table
        add_paragraph(doc, lp["exercise_title"], size=11.5, bold=True, color=accent,
                      space_before=8, space_after=6)
        digs = lp["exercise_digits"]
        ex_table = doc.add_table(rows=2, cols=len(digs))
        ex_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for col, dv in enumerate(digs):
            dpng = drawing_to_png(make_digit_drawing(dv, 50, 130),
                                  os.path.join(tmp_dir, f"d_{idx}_{dv}.png"))
            top = ex_table.cell(0, col)
            tp = top.paragraphs[0]
            tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            tp.add_run().add_picture(dpng, width=Cm(1.5))
            bot = ex_table.cell(1, col)
            bp = bot.paragraphs[0]
            bp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = bp.add_run(_arabic_num(dv))
            _set_run_font(run, size=16, bold=True, color=NAVY)
        if idx < 2:
            doc.add_paragraph()

    # set the whole document's default text direction (table grid order, etc.)
    sectPr = section._sectPr
    bidi_sect = OxmlElement("w:bidi")
    sectPr.append(bidi_sect)

    doc.save(output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    build()
