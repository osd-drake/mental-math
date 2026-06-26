"""Word (.docx) export — plain logical Arabic text (Word shapes Arabic itself),
with RTL paragraph direction set explicitly on every paragraph via raw OOXML.

Mirrors the PDF design: the cover keeps the full navy/silver/cream styling
(plus student identity fields), every interior page is black-text-on-white to
keep print cost down, and numbers replace color as the legend mechanism on
the parts table and level headings. Every interior page gets a
'-----* N *-----' footer (page 1 = the first page after the cover); the
cover itself stays unnumbered via a distinct first-page footer."""
import os

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from book.utils import BASE_DIR, IMAGE_DIR
from book.drawings import make_soroban_drawing, make_posture_drawing, make_digit_drawing
from book.raster import drawing_to_png
from book.pages import PART_NUMBER, NAME_TO_KEY
from book import content as C

NAVY = RGBColor(0x1C, 0x3D, 0x5F)
AMBER = RGBColor(0xC6, 0x8A, 0x3E)
TEAL = RGBColor(0x2E, 0x8B, 0x7F)
CORAL = RGBColor(0xD8, 0x59, 0x3F)
SILVER = RGBColor(0xAE, 0xB8, 0xC2)
BLACK = RGBColor(0x00, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xC8, 0xD0, 0xD8)

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


def cell_bottom_border(cell, hex_color="AEB8C2", size=8):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:color"), hex_color)
    borders.append(bottom)
    tcPr.append(borders)


def add_image_centered(container, png_path, width_cm):
    p = container.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(png_path, width=Cm(width_cm))
    return p


def add_identity_field(container, label, blank_width_cm=10.5):
    """A label + an empty, bottom-bordered cell standing in for a fill-in-by-hand
    blank line (used on the cover for student name / class / school)."""
    t = container.add_table(rows=1, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    blank_cell, label_cell = t.cell(0, 0), t.cell(0, 1)
    blank_cell.width = Cm(blank_width_cm)
    p = label_cell.paragraphs[0]
    run = p.add_run(label + "  ")
    _set_run_font(run, size=11.5, bold=True, color=WHITE)
    set_paragraph_rtl(p, align=WD_ALIGN_PARAGRAPH.RIGHT)
    cell_bottom_border(blank_cell)
    return t


_SECTPR_ORDER = [
    "w:headerReference", "w:footerReference", "w:footnotePr", "w:endnotePr",
    "w:type", "w:pgSz", "w:pgMar", "w:paperSrc", "w:pgBorders", "w:lnNumType",
    "w:pgNumType", "w:cols", "w:formProt", "w:vAlign", "w:noEndnote",
    "w:titlePg", "w:textDirection", "w:bidi", "w:rtlGutter", "w:docGrid",
    "w:printerSettings", "w:sectPrChange",
]


def insert_in_sectpr_order(sectPr, new_elm, tag):
    """python-docx's CT_SectPr only knows the insertion order for a few of its
    own child elements (pgSz/pgMar/titlePg/...); it has no descriptor for
    pgNumType or bidi. A bare append() would land them after w:docGrid, which
    violates the CT_SectPr schema sequence and risks a 'needs repair' prompt
    in Word. Insert before the first existing child that the schema says must
    come after `tag`, mirroring python-docx's own ZeroOrOne(successors=...)."""
    idx = _SECTPR_ORDER.index(tag)
    for successor_tag in _SECTPR_ORDER[idx + 1:]:
        successor = sectPr.find(qn(successor_tag))
        if successor is not None:
            successor.addprevious(new_elm)
            return
    sectPr.append(new_elm)


def build_page_number_footer(footer):
    """Literal '-----* ' + a live PAGE field + ' *-----', centered."""
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def _field_part(*children):
        r = p.add_run()
        rPr = r._r.get_or_add_rPr()
        rFonts = OxmlElement("w:rFonts")
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rFonts.set(qn(attr), "Cairo-SemiBold")
        rPr.append(rFonts)
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), "20")
        rPr.append(sz)
        for child in children:
            r._r.append(child)
        return r

    lead = p.add_run("-----* ")
    _set_run_font(lead, name="Cairo-SemiBold", size=10, color=BLACK)

    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    fld_text = OxmlElement("w:t")
    fld_text.text = "1"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")

    _field_part(fld_begin)
    _field_part(instr)
    _field_part(fld_sep)
    _field_part(fld_text)
    _field_part(fld_end)

    tail = p.add_run(" *-----")
    _set_run_font(tail, name="Cairo-SemiBold", size=10, color=BLACK)


def build(output_path=None):
    output_path = output_path or os.path.join(BASE_DIR, "output", "soroban_book.docx")
    tmp_dir = os.path.join(BASE_DIR, "output", "_docx_assets")
    os.makedirs(tmp_dir, exist_ok=True)

    soroban_png_big = drawing_to_png(make_soroban_drawing(500, 300, active_rod=2, active_value=6),
                                      os.path.join(tmp_dir, "soroban_big.png"))
    posture_pngs = {
        variant: drawing_to_png(make_posture_drawing(240, 270, variant=variant),
                                 os.path.join(tmp_dir, f"posture_{variant}.png"))
        for variant in ("correct1", "correct2", "incorrect")
    }
    soroban_photo = _img("soroban_photo.jpg")
    soroban_intro = _img("soroban_intro.jpg")

    doc = Document()
    section = doc.sections[0]
    section.page_height, section.page_width = Cm(29.7), Cm(21.0)  # A4
    for attr in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(section, attr, Cm(1.8))

    # set document-level base font
    style = doc.styles["Normal"]
    style.font.name = FONT
    style.font.size = Pt(12)

    # page numbering: cover is page 1 with its own (blank) first-page footer;
    # every page after it uses the default footer and is numbered starting at 1
    section.different_first_page_header_footer = True
    # Accessing .paragraphs forces python-docx to materialize the first-page
    # footer's XML part/relationship (a bare property access is a no-op);
    # this keeps the cover page footer empty/unnumbered.
    _ = section.first_page_footer.paragraphs
    build_page_number_footer(section.footer)
    sectPr = section._sectPr
    pg_num_type = OxmlElement("w:pgNumType")
    pg_num_type.set(qn("w:start"), "0")
    insert_in_sectpr_order(sectPr, pg_num_type, "w:pgNumType")

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

    # ---- student identity fields (this is a student workbook) ----
    cover_cell.add_paragraph().paragraph_format.space_after = Pt(4)
    add_identity_field(cover_cell, C.IDENTITY_NAME_LABEL + ":", blank_width_cm=10.5)
    add_identity_field(cover_cell, C.IDENTITY_CLASS_LABEL + ":", blank_width_cm=5)
    add_identity_field(cover_cell, C.IDENTITY_SCHOOL_LABEL + ":", blank_width_cm=5)

    doc.add_page_break()

    # ---------------- Introduction -------------------------------------------
    add_paragraph(doc, C.INTRO_TITLE, size=20, bold=True, color=BLACK, space_after=12)
    add_paragraph(doc, C.INTRO_TEXT, size=12.5, color=BLACK, space_after=14)

    add_image_centered(doc, soroban_intro, width_cm=12)
    add_paragraph(doc, C.INTRO_IMAGE_CAPTION, size=10.5, color=BLACK,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)

    add_paragraph(doc, C.BENEFITS_TITLE, size=15, bold=True, color=BLACK, space_after=8)
    for benefit in C.BENEFITS:
        add_paragraph(doc, f"• {benefit}", size=12, color=BLACK, space_after=6)

    doc.add_page_break()

    # ---------------- Sitting posture (three panels: 2 correct, 1 incorrect) -
    add_paragraph(doc, C.SITTING_TITLE, size=20, bold=True, color=BLACK, space_after=8)
    add_paragraph(doc, C.SITTING_INTRO, size=12.5, color=BLACK,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    p1, p2, p3 = C.SITTING_PANELS

    top_table = doc.add_table(rows=1, cols=2)
    top_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # RTL: panel 1 on the right (col 1), panel 2 on the left (col 0)
    for col, panel in ((1, p1), (0, p2)):
        cell = top_table.cell(0, col)
        accent = TEAL if panel["kind"] == "correct" else CORAL
        add_paragraph(cell, panel["label"], size=13, bold=True, color=accent,
                      align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
        add_image_centered(cell, posture_pngs[panel["variant"]], width_cm=5.5)
        for point in panel["points"]:
            add_paragraph(cell, f"• {point}", size=10, color=BLACK,
                          align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)

    doc.add_paragraph()

    accent3 = CORAL
    add_paragraph(doc, p3["label"], size=13.5, bold=True, color=accent3,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    add_image_centered(doc, posture_pngs[p3["variant"]], width_cm=6.5)
    for point in p3["points"]:
        add_paragraph(doc, f"• {point}", size=11, color=BLACK,
                      align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)

    doc.add_page_break()

    # ---------------- Usage steps --------------------------------------------
    add_paragraph(doc, C.USAGE_TITLE, size=20, bold=True, color=BLACK, space_after=14)

    for i, (step_title, step_desc) in enumerate(C.POSTURE_STEPS, start=1):
        add_paragraph(doc, f"{i}. {step_title}", size=13.5, bold=True, color=BLACK, space_after=2)
        add_paragraph(doc, step_desc, size=11.5, color=BLACK, space_after=12)

    add_paragraph(doc, C.USAGE_TIP, size=11.5, bold=True, color=BLACK,
                  align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=8)

    doc.add_page_break()

    # ---------------- Parts (numbered legend, not color-coded) --------------
    add_paragraph(doc, C.PARTS_TITLE, size=20, bold=True, color=BLACK, space_after=12)
    add_image_centered(doc, soroban_png_big, width_cm=13)
    doc.add_paragraph()

    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    headers = ["الوصف", "الجزء", "الرقم"]
    for cell, text in zip(hdr, headers):
        cp = cell.paragraphs[0]
        run = cp.add_run(text)
        _set_run_font(run, size=12, bold=True, color=BLACK)
        set_paragraph_rtl(cp, align=WD_ALIGN_PARAGRAPH.CENTER)

    for name, desc in C.PARTS:
        row = table.add_row().cells
        cp_desc = row[0].paragraphs[0]
        run = cp_desc.add_run(desc)
        _set_run_font(run, size=11.5, color=BLACK)
        set_paragraph_rtl(cp_desc, align=WD_ALIGN_PARAGRAPH.RIGHT)

        cp_name = row[1].paragraphs[0]
        run = cp_name.add_run(name)
        _set_run_font(run, size=12, bold=True, color=BLACK)
        set_paragraph_rtl(cp_name, align=WD_ALIGN_PARAGRAPH.RIGHT)

        cp_num = row[2].paragraphs[0]
        run = cp_num.add_run(_arabic_num(PART_NUMBER[NAME_TO_KEY[name]]))
        _set_run_font(run, size=12, bold=True, color=BLACK)
        set_paragraph_rtl(cp_num, align=WD_ALIGN_PARAGRAPH.CENTER)

    doc.add_page_break()

    # ---------------- Levels / curriculum ------------------------------------
    add_paragraph(doc, C.LEVELS_INTRO_TITLE, size=20, bold=True, color=BLACK, space_after=10)
    add_paragraph(doc, C.LEVELS_INTRO_TEXT, size=12.5, color=BLACK, space_after=14)

    for idx, lp in enumerate(C.LEVEL_PAGES):
        add_paragraph(doc, f"{_arabic_num(idx + 1)}. {lp['ordinal']} — {lp['name']} ({lp['range']})",
                      size=15, bold=True, color=BLACK, space_before=8, space_after=4)
        add_paragraph(doc, lp["objective"], size=11.5, color=BLACK, space_after=6)
        for skill in lp["skills"]:
            add_paragraph(doc, f"◆ {skill}", size=11, color=BLACK, space_after=3)

        # digit -> soroban exercise as a simple table
        add_paragraph(doc, lp["exercise_title"], size=11.5, bold=True, color=BLACK,
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
            _set_run_font(run, size=16, bold=True, color=BLACK)
        if idx < 2:
            doc.add_paragraph()

    # set the whole document's default text direction (table grid order, etc.)
    bidi_sect = OxmlElement("w:bidi")
    insert_in_sectpr_order(sectPr, bidi_sect, "w:bidi")

    doc.save(output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    build()
