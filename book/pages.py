"""Canvas drawing routines for each page of the book.

Cover keeps the full navy/silver/cream design. Every interior page is a
plain white background with black text and thin black structure lines —
print ink (and therefore cost) stays low, and color is reserved only for
the universal green-check / red-X correct/incorrect marks on the sitting
page. Where the old design used color to distinguish items (parts legend,
level identity), numbers are used instead.
"""
import os
from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

from book.utils import (
    NAVY, NAVY_DARK, NAVY_LIGHT, SILVER, AMBER, CREAM, SAND, WHITE, BLACK,
    NAVY_TINT, AMBER_TINT, PAGE_W, PAGE_H, rounded_card, ar, IMAGE_DIR,
)
from book.text import draw_ar_right, draw_ar_center, wrap_arabic
from book.drawings import (
    make_soroban_drawing, make_posture_drawing,
    make_digit_drawing, get_anchor_points,
)
from book import content as C

MARGIN = 42
RIGHT = PAGE_W - MARGIN
LEFT = MARGIN
CONTENT_W = PAGE_W - 2 * MARGIN

CORRECT_GREEN = HexColor("#2E8B7F")
INCORRECT_RED = HexColor("#D8593F")


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------
def _img(name):
    return os.path.join(IMAGE_DIR, name)


def draw_image_fitted(c, path, x, y, w, h, pad=10, card=True,
                      card_fill=WHITE, stroke=BLACK, radius=14):
    """Draw an image fitted (aspect-preserving, centered) inside a box, optionally
    on a rounded card."""
    if card:
        rounded_card(c, x, y, w, h, radius=radius, fill=card_fill, stroke=stroke, stroke_width=1)
    ir = ImageReader(path)
    iw, ih = ir.getSize()
    aw, ah = w - 2 * pad, h - 2 * pad
    scale = min(aw / iw, ah / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(ir, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh, mask="auto")


def _diamond(c, cx, cy, r, color):
    c.saveState()
    c.setFillColor(color)
    p = c.beginPath()
    p.moveTo(cx - r, cy)
    p.lineTo(cx, cy + r)
    p.lineTo(cx + r, cy)
    p.lineTo(cx, cy - r)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()


def _diamond_pattern(c, color, alpha=0.05, spacing=46):
    c.saveState()
    c.setStrokeColor(color)
    c.setStrokeAlpha(alpha)
    c.setLineWidth(1)
    size = spacing * 0.30
    row = 0
    y = -spacing
    while y < PAGE_H + spacing:
        offset = (spacing / 2) if row % 2 else 0
        x = -spacing + offset
        while x < PAGE_W + spacing:
            p = c.beginPath()
            p.moveTo(x - size, y)
            p.lineTo(x, y + size)
            p.lineTo(x + size, y)
            p.lineTo(x, y - size)
            p.close()
            c.drawPath(p, stroke=1, fill=0)
            x += spacing
        y += spacing * 0.5
        row += 1
    c.restoreState()


def _background(c):
    """Plain white interior page — keeps printed ink coverage, and cost, low."""
    c.setFillColor(WHITE)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)


def _page_header(c, title_text):
    y = PAGE_H - 56
    draw_ar_right(c, title_text, RIGHT, y, "Cairo-Black", 21, BLACK)
    c.setStrokeColor(BLACK)
    c.setLineWidth(1.3)
    c.line(LEFT, y - 12, RIGHT, y - 12)
    return y - 40


def draw_page_number(c, n):
    """Footer page number in the exact requested format, on every interior page."""
    c.setFillColor(BLACK)
    c.setFont("Cairo-SemiBold", 10)
    c.drawCentredString(PAGE_W / 2, 26, f"-----* {n} *-----")


# ---------------------------------------------------------------------------
# credential icons (small navy line icons — cover only)
# ---------------------------------------------------------------------------
def _icon_medal(c, cx, cy, color):
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.6)
    c.line(cx - 4, cy + 2, cx - 6, cy + 9)
    c.line(cx + 4, cy + 2, cx + 6, cy + 9)
    c.circle(cx, cy - 2, 6, stroke=1, fill=0)
    c.circle(cx, cy - 2, 2, stroke=0, fill=1)
    c.restoreState()


def _icon_globe(c, cx, cy, color):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(1.5)
    c.circle(cx, cy, 7, stroke=1, fill=0)
    c.ellipse(cx - 3, cy - 7, cx + 3, cy + 7, stroke=1, fill=0)
    c.line(cx - 7, cy, cx + 7, cy)
    c.restoreState()


def _icon_people(c, cx, cy, color):
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.5)
    for dx in (-4, 4):
        c.circle(cx + dx, cy + 4, 3, stroke=0, fill=1)
        p = c.beginPath()
        p.moveTo(cx + dx - 4, cy - 6)
        p.curveTo(cx + dx - 4, cy + 1, cx + dx + 4, cy + 1, cx + dx + 4, cy - 6)
        c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


def pdf_string_w(text, font, size):
    from reportlab.pdfbase import pdfmetrics
    return pdfmetrics.stringWidth(ar(text), font, size)


# ---------------------------------------------------------------------------
# COVER (kept as designed — navy/silver/cream — plus student identity fields)
# ---------------------------------------------------------------------------
def page_cover(c):
    # cream base + faint pattern
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    _diamond_pattern(c, NAVY, alpha=0.04, spacing=50)

    # navy diagonal corner accent (top-left) and footer band (bottom)
    c.saveState()
    c.setFillColor(NAVY)
    p = c.beginPath()
    p.moveTo(0, PAGE_H)
    p.lineTo(190, PAGE_H)
    p.lineTo(0, PAGE_H - 150)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(NAVY_DARK)
    p = c.beginPath()
    p.moveTo(0, PAGE_H)
    p.lineTo(120, PAGE_H)
    p.lineTo(0, PAGE_H - 95)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()

    # ---- title block ----
    y = PAGE_H - 74
    draw_ar_center(c, C.COVER_KICKER, PAGE_W / 2, y, "Cairo-SemiBold", 17, AMBER)
    y -= 34
    draw_ar_center(c, C.COVER_LINE_1, PAGE_W / 2, y, "Cairo-Black", 33, NAVY)
    y -= 26
    # divider with diamond
    c.setStrokeColor(SILVER)
    c.setLineWidth(1.4)
    c.line(PAGE_W / 2 - 80, y, PAGE_W / 2 - 12, y)
    c.line(PAGE_W / 2 + 12, y, PAGE_W / 2 + 80, y)
    _diamond(c, PAGE_W / 2, y, 5, AMBER)
    y -= 26
    draw_ar_center(c, C.COVER_LINE_2, PAGE_W / 2, y, "Cairo-SemiBold", 18, NAVY_LIGHT)
    y -= 34
    draw_ar_center(c, C.COVER_LINE_3, PAGE_W / 2, y, "Cairo-Black", 33, NAVY)
    y -= 22

    # ---- hero soroban photo ----
    hero_w, hero_h = 360, 150
    hero_x = (PAGE_W - hero_w) / 2
    hero_y = y - hero_h
    draw_image_fitted(c, _img("soroban_photo.jpg"), hero_x, hero_y, hero_w, hero_h,
                      pad=10, card=True, card_fill=WHITE, stroke=SAND, radius=16)
    y = hero_y - 22

    # ---- level cards (RTL: level 1 on the right) ----
    gap = 12
    card_w = (CONTENT_W - 2 * gap) / 3
    card_h = 116
    card_y = y - card_h
    for i in range(3):
        # right-to-left placement
        cx0 = RIGHT - (i + 1) * card_w - i * gap
        rounded_card(c, cx0, card_y, card_w, card_h, radius=12, fill=WHITE, stroke=SAND, stroke_width=1.2)
        # navy header strip
        c.setFillColor(NAVY)
        c.roundRect(cx0, card_y + card_h - 26, card_w, 26, 8, stroke=0, fill=1)
        c.setFillColor(NAVY)
        c.rect(cx0, card_y + card_h - 26, card_w, 13, stroke=0, fill=1)
        draw_ar_center(c, C.LEVEL_ORDINALS[i], cx0 + card_w / 2, card_y + card_h - 18, "Cairo-Bold", 10.5, WHITE)
        # description
        desc_lines = wrap_arabic(C.LEVEL_DESCRIPTIONS[i], "Cairo-SemiBold", 8.6, card_w - 16)
        ty = card_y + card_h - 40
        for line in desc_lines[:3]:
            draw_ar_center(c, line, cx0 + card_w / 2, ty, "Cairo-SemiBold", 8.6, NAVY)
            ty -= 12
        # mini soroban at the bottom
        mini = make_soroban_drawing(card_w - 30, 24, rods=5)
        renderPDF.draw(mini, c, cx0 + 15, card_y + 7)
        # "..." connector between cards
        if i < 2:
            c.setFillColor(SILVER)
            for k in range(3):
                c.circle(cx0 - gap / 2 - 4 + k * 4, card_y + card_h / 2, 1.3, stroke=0, fill=1)
    y = card_y - 24

    # ---- author block ----
    draw_ar_center(c, C.AUTHOR_PREFIX, PAGE_W / 2, y, "Cairo-SemiBold", 12, AMBER)
    y -= 22
    draw_ar_center(c, C.AUTHOR_NAME, PAGE_W / 2, y, "Cairo-Bold", 16, NAVY)
    y -= 24

    icons = [_icon_medal, _icon_globe, _icon_people]
    for i, cred in enumerate(C.AUTHOR_CREDENTIALS):
        line_w = pdf_string_w(cred, "Cairo-SemiBold", 10.5)
        # center the icon + text group
        total = line_w + 20
        start_right = PAGE_W / 2 + total / 2
        draw_ar_right(c, cred, start_right, y - 3, "Cairo-SemiBold", 10.5, NAVY_DARK)
        icons[i](c, start_right - line_w - 11, y, AMBER)
        y -= 20

    # ---- student identity fields (this is a student workbook) ----
    y -= 8
    c.setStrokeColor(SILVER)
    c.setLineWidth(1)
    c.line(LEFT + 24, y, RIGHT - 24, y)
    y -= 22

    label_font, label_size = "Cairo-Bold", 11.5
    draw_ar_right(c, C.IDENTITY_NAME_LABEL + ":", RIGHT - 24, y, label_font, label_size, NAVY)
    name_w = pdf_string_w(C.IDENTITY_NAME_LABEL + ":", label_font, label_size)
    c.setStrokeColor(SILVER)
    c.setLineWidth(1.1)
    c.line(RIGHT - 24 - name_w - 8, y - 3, LEFT + 24, y - 3)
    y -= 26

    half_w = (CONTENT_W - 48 - 16) / 2
    draw_ar_right(c, C.IDENTITY_CLASS_LABEL + ":", RIGHT - 24, y, label_font, label_size, NAVY)
    class_w = pdf_string_w(C.IDENTITY_CLASS_LABEL + ":", label_font, label_size)
    c.line(RIGHT - 24 - class_w - 8, y - 3, RIGHT - 24 - half_w, y - 3)

    school_x = RIGHT - 24 - half_w - 16
    draw_ar_right(c, C.IDENTITY_SCHOOL_LABEL + ":", school_x, y, label_font, label_size, NAVY)
    school_w = pdf_string_w(C.IDENTITY_SCHOOL_LABEL + ":", label_font, label_size)
    c.line(school_x - school_w - 8, y - 3, LEFT + 24, y - 3)

    # ---- footer band ----
    band_h = 56
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, band_h, stroke=0, fill=1)
    c.setFillColor(NAVY_DARK)
    p = c.beginPath()
    p.moveTo(PAGE_W, band_h)
    p.lineTo(PAGE_W - 150, band_h)
    p.lineTo(PAGE_W, band_h + 70)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    draw_ar_center(c, C.COVER_TAGLINE + " • سلسلة الحساب الذهني", PAGE_W / 2, band_h / 2 - 5,
                   "Cairo-SemiBold", 12, WHITE)


# ---------------------------------------------------------------------------
# INTRODUCTION
# ---------------------------------------------------------------------------
def page_intro(c):
    _background(c)
    y = _page_header(c, C.INTRO_TITLE)

    # paragraph card
    pad = 20
    text_size, leading = 13.5, 22
    wrapped = wrap_arabic(C.INTRO_TEXT, "Cairo", text_size, CONTENT_W - 2 * pad)
    card_h = pad * 2 + leading * len(wrapped) - (leading - text_size)
    card_y = y - card_h
    rounded_card(c, LEFT, card_y, CONTENT_W, card_h, radius=14, fill=WHITE, stroke=BLACK, stroke_width=1)
    ty = y - pad - text_size
    for line in wrapped:
        draw_ar_right(c, line, RIGHT - pad, ty, "Cairo", text_size, BLACK)
        ty -= leading

    # real soroban photo + caption
    img_y_top = card_y - 24
    img_w, img_h = 330, 175
    img_x = (PAGE_W - img_w) / 2
    img_y = img_y_top - img_h
    draw_image_fitted(c, _img("soroban_intro.jpg"), img_x, img_y, img_w, img_h,
                      pad=8, card=True, card_fill=WHITE, stroke=BLACK, radius=14)
    draw_ar_center(c, C.INTRO_IMAGE_CAPTION, PAGE_W / 2, img_y - 18, "Cairo", 10.5, BLACK)

    # benefits
    bt_y = img_y - 46
    draw_ar_right(c, C.BENEFITS_TITLE, RIGHT, bt_y, "Cairo-Bold", 15, BLACK)
    row_y = bt_y - 28
    row_h = 28
    for benefit in C.BENEFITS:
        rounded_card(c, LEFT, row_y - row_h + 7, CONTENT_W, row_h - 2, radius=10, fill=WHITE, stroke=BLACK, stroke_width=0.8)
        c.setFillColor(BLACK)
        c.circle(RIGHT - 16, row_y - row_h / 2 + 7, 3, stroke=0, fill=1)
        draw_ar_right(c, benefit, RIGHT - 32, row_y - row_h / 2 + 3, "Cairo-SemiBold", 11.5, BLACK)
        row_y -= row_h + 6


# ---------------------------------------------------------------------------
# SITTING POSTURE — three panels: two correct, one incorrect; advice below image
# ---------------------------------------------------------------------------
def _sitting_panel(c, x, y_top, w, panel, drawing_w, drawing_h):
    pad = 13
    bullet_size, bullet_leading = 10, 13.6
    points = panel["points"]
    wrapped_per_point = [wrap_arabic(pt, "Cairo", bullet_size, w - 2 * pad - 12) for pt in points]
    n_lines = sum(len(wl) for wl in wrapped_per_point)

    label_h = 22
    img_block_h = drawing_h + 8
    bullets_h = n_lines * bullet_leading + (len(points) - 1) * 4
    card_h = pad * 2 + label_h + img_block_h + bullets_h

    card_y = y_top - card_h
    accent = CORRECT_GREEN if panel["kind"] == "correct" else INCORRECT_RED
    rounded_card(c, x, card_y, w, card_h, radius=14, fill=WHITE, stroke=accent, stroke_width=1.4)

    ty = y_top - pad - 11
    draw_ar_center(c, panel["label"], x + w / 2, ty, "Cairo-Bold", 13, accent)
    ty -= label_h

    drawing = make_posture_drawing(drawing_w, drawing_h, variant=panel["variant"])
    renderPDF.draw(drawing, c, x + (w - drawing_w) / 2, ty - drawing_h)
    ty -= img_block_h

    for i, pt in enumerate(points):
        for li, line in enumerate(wrapped_per_point[i]):
            prefix = "• " if li == 0 else "  "
            draw_ar_right(c, prefix + line, x + w - pad, ty, "Cairo", bullet_size, BLACK)
            ty -= bullet_leading
        ty -= 4

    return card_y


def page_sitting(c):
    _background(c)
    y = _page_header(c, C.SITTING_TITLE)
    draw_ar_center(c, C.SITTING_INTRO, PAGE_W / 2, y, "Cairo-SemiBold", 12, BLACK)
    y -= 22

    gap = 14
    top_w = (CONTENT_W - gap) / 2
    p1, p2, p3 = C.SITTING_PANELS
    bottom1 = _sitting_panel(c, RIGHT - top_w, y, top_w, p1, drawing_w=140, drawing_h=160)
    bottom2 = _sitting_panel(c, LEFT, y, top_w, p2, drawing_w=140, drawing_h=160)
    y2 = min(bottom1, bottom2) - 16

    _sitting_panel(c, LEFT, y2, CONTENT_W, p3, drawing_w=170, drawing_h=175)


# ---------------------------------------------------------------------------
# USAGE STEPS (mascot and pencil-holding step removed)
# ---------------------------------------------------------------------------
def _step_icon(c, kind, cx, cy, color):
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(2.2)
    if kind == "sit":
        c.circle(cx, cy + 10, 6, stroke=1, fill=0)
        c.line(cx, cy + 4, cx, cy - 10)
        c.line(cx, cy - 10, cx - 8, cy - 18)
        c.line(cx, cy - 10, cx + 8, cy - 18)
        c.line(cx, cy - 2, cx - 9, cy - 6)
        c.line(cx, cy - 2, cx + 9, cy - 6)
    elif kind == "hands":
        c.ellipse(cx - 16, cy - 8, cx - 2, cy + 8, stroke=1, fill=0)
        c.ellipse(cx + 2, cy - 8, cx + 16, cy + 8, stroke=1, fill=0)
    elif kind == "focus":
        c.ellipse(cx - 16, cy - 9, cx + 16, cy + 9, stroke=1, fill=0)
        c.circle(cx, cy, 5, stroke=0, fill=1)
    c.restoreState()


def page_posture(c):
    _background(c)
    y = _page_header(c, C.USAGE_TITLE)
    y -= 14

    gap_x = 14
    card_w = (CONTENT_W - 2 * gap_x) / 3
    card_h = 210
    icons = ["sit", "hands", "focus"]

    for idx, (step_title, step_desc) in enumerate(C.POSTURE_STEPS):
        cx0 = RIGHT - (idx + 1) * card_w - idx * gap_x
        cy0 = y - card_h
        rounded_card(c, cx0, cy0, card_w, card_h, radius=14, fill=WHITE, stroke=BLACK, stroke_width=1)

        c.setStrokeColor(BLACK)
        c.setFillColor(WHITE)
        c.circle(cx0 + card_w / 2, cy0 + card_h - 34, 16, stroke=1, fill=1)
        c.setFillColor(BLACK)
        c.setFont("Cairo-Bold", 14)
        c.drawCentredString(cx0 + card_w / 2, cy0 + card_h - 38.5, str(idx + 1))

        _step_icon(c, icons[idx], cx0 + card_w / 2, cy0 + card_h - 76, BLACK)

        draw_ar_center(c, step_title, cx0 + card_w / 2, cy0 + card_h - 108, "Cairo-Bold", 13, BLACK)
        wrapped_desc = wrap_arabic(step_desc, "Cairo", 10.5, card_w - 26)
        ty = cy0 + card_h - 128
        for line in wrapped_desc:
            draw_ar_center(c, line, cx0 + card_w / 2, ty, "Cairo", 10.5, BLACK)
            ty -= 15

    tip_y_top = y - card_h - 20
    tip_h = 56
    rounded_card(c, LEFT, tip_y_top - tip_h, CONTENT_W, tip_h, radius=14, fill=WHITE, stroke=BLACK, stroke_width=1.2)
    wrapped_tip = wrap_arabic(C.USAGE_TIP, "Cairo-SemiBold", 12.5, CONTENT_W - 40)
    ty = tip_y_top - tip_h / 2 + (len(wrapped_tip) - 1) * 9
    for line in wrapped_tip:
        draw_ar_center(c, line, PAGE_W / 2, ty, "Cairo-SemiBold", 12.5, BLACK)
        ty -= 18


# ---------------------------------------------------------------------------
# PARTS — numbered labels instead of color-coded dots
# ---------------------------------------------------------------------------
PART_NUMBER = {"frame": 1, "rod": 2, "beam": 3, "heaven": 4, "earth": 5}
NAME_TO_KEY = {
    "الإطار": "frame",
    "العمود": "rod",
    "الفاصل": "beam",
    "خرز السماء": "heaven",
    "خرز الأرض": "earth",
}


def _numbered_dot(c, x, y, n, r=9, font_size=10):
    c.setStrokeColor(BLACK)
    c.setFillColor(WHITE)
    c.circle(x, y, r, stroke=1, fill=1)
    c.setFillColor(BLACK)
    c.setFont("Cairo-Bold", font_size)
    c.drawCentredString(x, y - font_size * 0.36, str(n))


def page_parts(c):
    _background(c)
    y = _page_header(c, C.PARTS_TITLE)

    diagram_w, diagram_h = 380, 230
    diagram_x = (PAGE_W - diagram_w) / 2
    diagram_y = y - diagram_h - 70

    card_pad = 16
    rounded_card(
        c, diagram_x - card_pad, diagram_y - card_pad, diagram_w + 2 * card_pad, diagram_h + 2 * card_pad,
        radius=16, fill=WHITE, stroke=BLACK, stroke_width=1,
    )
    drawing = make_soroban_drawing(diagram_w, diagram_h, rods=7, active_rod=2, active_value=6)
    renderPDF.draw(drawing, c, diagram_x, diagram_y)

    anchors = get_anchor_points(diagram_w, diagram_h, rods=7, label_rod=2)
    label_targets = {
        "frame": (diagram_x - card_pad - 14, diagram_y + diagram_h + 26, "left"),
        "heaven": (diagram_x - card_pad - 14, diagram_y + diagram_h - 30, "left"),
        "beam": (diagram_x + diagram_w + card_pad + 14, diagram_y + diagram_h * 0.55, "right"),
        "rod": (diagram_x + diagram_w + card_pad + 14, diagram_y + diagram_h * 0.85, "right"),
        "earth": (diagram_x - card_pad - 14, diagram_y + 18, "left"),
    }

    c.setLineWidth(1)
    for key, (lx, ly, side) in label_targets.items():
        ax, ay = anchors[key]
        ax += diagram_x
        ay += diagram_y
        c.setStrokeColor(BLACK)
        c.setFillColor(BLACK)
        c.circle(ax, ay, 2.4, stroke=0, fill=1)
        c.line(ax, ay, lx, ly)
        _numbered_dot(c, lx, ly, PART_NUMBER[key])

    list_top = diagram_y - card_pad - 30
    row_h = 32
    for i, (name, desc) in enumerate(C.PARTS):
        ry = list_top - i * row_h
        rounded_card(c, LEFT, ry - row_h + 10, CONTENT_W, row_h - 6, radius=10, fill=WHITE, stroke=BLACK, stroke_width=0.8)
        _numbered_dot(c, RIGHT - 16, ry - row_h / 2 + 9, PART_NUMBER[NAME_TO_KEY[name]])
        draw_ar_right(c, name, RIGHT - 34, ry - row_h / 2 + 4, "Cairo-Bold", 12, BLACK)
        wrapped_desc = wrap_arabic(desc, "Cairo", 10.5, CONTENT_W - 190)
        draw_ar_right(c, wrapped_desc[0], RIGHT - 170, ry - row_h / 2 + 4, "Cairo", 10.5, BLACK)


# ---------------------------------------------------------------------------
# LEVELS OVERVIEW + PER-LEVEL CURRICULUM PAGES (numbered, not color-coded)
# ---------------------------------------------------------------------------
def page_levels_intro(c):
    _background(c)
    y = _page_header(c, C.LEVELS_INTRO_TITLE)

    pad = 20
    wrapped = wrap_arabic(C.LEVELS_INTRO_TEXT, "Cairo", 13, CONTENT_W - 2 * pad)
    card_h = pad * 2 + 21 * len(wrapped) - 7
    card_y = y - card_h
    rounded_card(c, LEFT, card_y, CONTENT_W, card_h, radius=14, fill=WHITE, stroke=BLACK, stroke_width=1)
    ty = y - pad - 13
    for line in wrapped:
        draw_ar_right(c, line, RIGHT - pad, ty, "Cairo", 13, BLACK)
        ty -= 21

    # three stacked level summary cards
    top = card_y - 28
    bh = 150
    gap = 18
    for i, lp in enumerate(C.LEVEL_PAGES):
        by_top = top - i * (bh + gap)
        by = by_top - bh
        rounded_card(c, LEFT, by, CONTENT_W, bh, radius=16, fill=WHITE, stroke=BLACK, stroke_width=1)
        # left number block (outline only — number identifies the level, not color)
        c.setStrokeColor(BLACK)
        c.line(LEFT + 96, by + 10, LEFT + 96, by + bh - 10)
        _numbered_dot(c, LEFT + 48, by + bh / 2 + 8, i + 1, r=22, font_size=22)
        draw_ar_center(c, lp["name"], LEFT + 48, by + 16, "Cairo-Bold", 11.5, BLACK)

        # right side text
        tx = RIGHT - 14
        draw_ar_right(c, lp["ordinal"] + " — " + lp["range"], tx, by_top - 28, "Cairo-Bold", 15, BLACK)
        obj_lines = wrap_arabic(lp["objective"], "Cairo", 11, CONTENT_W - 96 - 40)
        oy = by_top - 50
        for line in obj_lines[:2]:
            draw_ar_right(c, line, tx, oy, "Cairo", 11, BLACK)
            oy -= 17
        # a small digit row preview
        dx = RIGHT - 14
        for k, dv in enumerate([1, 2, 3]):
            dd = make_digit_drawing(dv, 30, 60)
            renderPDF.draw(dd, c, dx - 32, by + 12)
            dx -= 36


def page_level(c, idx):
    """Detailed curriculum page for one level, with a digit→soroban exercise."""
    lp = C.LEVEL_PAGES[idx]
    _background(c)

    # header band with level number
    y = PAGE_H - 56
    _numbered_dot(c, RIGHT - 18, y - 4, idx + 1, r=18, font_size=16)
    draw_ar_right(c, lp["ordinal"], RIGHT - 44, y, "Cairo-Black", 21, BLACK)
    draw_ar_right(c, lp["range"], RIGHT - 44, y - 22, "Cairo-SemiBold", 13, BLACK)
    c.setStrokeColor(BLACK)
    c.setLineWidth(1.3)
    c.line(LEFT, y - 36, RIGHT, y - 36)
    y -= 64

    # objective card
    pad = 18
    obj_lines = wrap_arabic(lp["objective"], "Cairo", 12.5, CONTENT_W - 2 * pad)
    obj_h = pad * 2 + 20 * len(obj_lines) - 7
    obj_y = y - obj_h
    rounded_card(c, LEFT, obj_y, CONTENT_W, obj_h, radius=14, fill=WHITE, stroke=BLACK, stroke_width=1)
    ty = y - pad - 12.5
    for line in obj_lines:
        draw_ar_right(c, line, RIGHT - pad, ty, "Cairo", 12.5, BLACK)
        ty -= 20
    y = obj_y - 26

    # skills list
    draw_ar_right(c, "المهارات المستهدفة", RIGHT, y, "Cairo-Bold", 14.5, BLACK)
    y -= 26
    for skill in lp["skills"]:
        rounded_card(c, LEFT, y - 24, CONTENT_W, 30, radius=11, fill=WHITE, stroke=BLACK, stroke_width=0.8)
        c.setFillColor(BLACK)
        c.circle(RIGHT - 16, y - 9, 2.6, stroke=0, fill=1)
        draw_ar_right(c, skill, RIGHT - 32, y - 13, "Cairo-SemiBold", 12, BLACK)
        y -= 36
    y -= 6

    # exercise box (number -> soroban matching, like a printable worksheet)
    ex_lines = lp["exercise_digits"]
    n = len(ex_lines)
    ex_top = y
    row_h = 70
    ex_h = 44 + n * row_h
    ex_y = ex_top - ex_h
    rounded_card(c, LEFT, ex_y, CONTENT_W, ex_h, radius=16, fill=WHITE, stroke=BLACK, stroke_width=1.2)
    # exercise title strip (text + underline, no large fill — keeps ink low)
    draw_ar_center(c, lp["exercise_title"], PAGE_W / 2, ex_top - 22, "Cairo-Bold", 13, BLACK)
    c.setStrokeColor(BLACK)
    c.setLineWidth(1)
    c.line(LEFT + 40, ex_top - 32, RIGHT - 40, ex_top - 32)

    # two columns: numbers on the right, soroban on the left, dashed link in the middle
    col_num_x = RIGHT - 70
    col_sor_x = LEFT + 70
    ry = ex_top - 34 - 40
    import random
    rng = random.Random(idx + 7)
    shuffled = ex_lines[:]
    rng.shuffle(shuffled)
    for i in range(n):
        num = ex_lines[i]
        # number bubble (right)
        c.setFillColor(WHITE)
        c.setStrokeColor(BLACK)
        c.setLineWidth(1.3)
        c.circle(col_num_x, ry, 20, stroke=1, fill=1)
        draw_ar_center(c, _arabic_num(num), col_num_x, ry - 9, "Cairo-Black", 20, BLACK)
        # connection anchor dots
        c.setFillColor(BLACK)
        c.circle(col_num_x - 26, ry, 2.2, stroke=0, fill=1)
        c.circle(col_sor_x + 30, ry, 2.2, stroke=0, fill=1)
        # soroban (left) — shuffled so it's a real matching task
        sd = make_digit_drawing(shuffled[i], 40, 64)
        renderPDF.draw(sd, c, col_sor_x - 20, ry - 32)
        ry -= row_h


def _arabic_num(n):
    western = str(n)
    mapping = {"0": "٠", "1": "١", "2": "٢", "3": "٣", "4": "٤",
               "5": "٥", "6": "٦", "7": "٧", "8": "٨", "9": "٩"}
    return "".join(mapping.get(ch, ch) for ch in western)
