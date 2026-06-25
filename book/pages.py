"""Canvas drawing routines for each page of the book (navy / silver / cream)."""
import os
from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

from book.utils import (
    NAVY, NAVY_DARK, NAVY_LIGHT, SILVER, AMBER, CREAM, SAND, WHITE,
    NAVY_TINT, AMBER_TINT, PAGE_W, PAGE_H, rounded_card, ar, IMAGE_DIR,
)
from book.text import draw_ar_right, draw_ar_center, wrap_arabic
from book.drawings import (
    make_soroban_drawing, make_mascot_drawing, make_posture_drawing,
    make_digit_drawing, get_anchor_points,
)
from book import content as C

MARGIN = 42
RIGHT = PAGE_W - MARGIN
LEFT = MARGIN
CONTENT_W = PAGE_W - 2 * MARGIN

GRAY = HexColor("#5B5B6B")
INK = NAVY_DARK
CORRECT_GREEN = HexColor("#2E8B7F")
INCORRECT_RED = HexColor("#D8593F")


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------
def _img(name):
    return os.path.join(IMAGE_DIR, name)


def draw_image_fitted(c, path, x, y, w, h, pad=10, card=True,
                      card_fill=WHITE, stroke=SAND, radius=14):
    """Draw an image fitted (aspect-preserving, centered) inside a box, optionally
    on a rounded card."""
    if card:
        rounded_card(c, x, y, w, h, radius=radius, fill=card_fill, stroke=stroke, stroke_width=1.2)
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
    """Cream page with soft tinted corner accents, used on every interior page.
    Uses pre-blended light colors (not alpha) so the accents stay subtle and never
    obscure the header text."""
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(NAVY_TINT)
    c.circle(PAGE_W + 30, PAGE_H + 30, 140, stroke=0, fill=1)
    c.setFillColor(AMBER_TINT)
    c.circle(-30, -20, 130, stroke=0, fill=1)


def _page_header(c, title_text, accent=NAVY):
    y = PAGE_H - 56
    draw_ar_right(c, title_text, RIGHT, y, "Cairo-Black", 21, NAVY)
    c.setStrokeColor(accent)
    c.setLineWidth(3)
    c.line(LEFT, y - 12, RIGHT, y - 12)
    _diamond(c, RIGHT, y - 11, 4, AMBER)
    return y - 40


def _badge(c, x_center, y_center, text, color, w=110, h=30, text_color=WHITE, font="Cairo-Bold", size=12):
    c.saveState()
    c.setFillColor(color)
    c.roundRect(x_center - w / 2, y_center - h / 2, w, h, h / 2, stroke=0, fill=1)
    c.setFillColor(text_color)
    c.setFont(font, size)
    c.drawCentredString(x_center, y_center - size * 0.34, ar(text))
    c.restoreState()


# ---------------------------------------------------------------------------
# credential icons (small navy line icons)
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


# ---------------------------------------------------------------------------
# COVER
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
    hero_w, hero_h = 360, 165
    hero_x = (PAGE_W - hero_w) / 2
    hero_y = y - hero_h
    draw_image_fitted(c, _img("soroban_photo.jpg"), hero_x, hero_y, hero_w, hero_h,
                      pad=10, card=True, card_fill=WHITE, stroke=SAND, radius=16)
    y = hero_y - 26

    # ---- level cards (RTL: level 1 on the right) ----
    gap = 12
    card_w = (CONTENT_W - 2 * gap) / 3
    card_h = 122
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
        mini = make_soroban_drawing(card_w - 30, 26, rods=5)
        renderPDF.draw(mini, c, cx0 + 15, card_y + 8)
        # "..." connector between cards
        if i < 2:
            c.setFillColor(SILVER)
            for k in range(3):
                c.circle(cx0 - gap / 2 - 4 + k * 4, card_y + card_h / 2, 1.3, stroke=0, fill=1)
    y = card_y - 30

    # ---- author block ----
    draw_ar_center(c, C.AUTHOR_PREFIX, PAGE_W / 2, y, "Cairo-SemiBold", 13, AMBER)
    y -= 26
    draw_ar_center(c, C.AUTHOR_NAME, PAGE_W / 2, y, "Cairo-Bold", 18, NAVY)
    y -= 30

    icons = [_icon_medal, _icon_globe, _icon_people]
    for i, cred in enumerate(C.AUTHOR_CREDENTIALS):
        line_w = pdf_string_w(cred, "Cairo-SemiBold", 12)
        # center the icon + text group
        total = line_w + 22
        start_right = PAGE_W / 2 + total / 2
        draw_ar_right(c, cred, start_right, y - 4, "Cairo-SemiBold", 12, NAVY_DARK)
        icons[i](c, start_right - line_w - 12, y, AMBER)
        y -= 25

    # ---- footer band ----
    band_h = 64
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


def pdf_string_w(text, font, size):
    from reportlab.pdfbase import pdfmetrics
    return pdfmetrics.stringWidth(ar(text), font, size)


# ---------------------------------------------------------------------------
# INTRODUCTION
# ---------------------------------------------------------------------------
def page_intro(c):
    _background(c)
    y = _page_header(c, C.INTRO_TITLE, accent=NAVY)

    # paragraph card
    pad = 20
    text_size, leading = 13.5, 22
    wrapped = wrap_arabic(C.INTRO_TEXT, "Cairo", text_size, CONTENT_W - 2 * pad)
    card_h = pad * 2 + leading * len(wrapped) - (leading - text_size)
    card_y = y - card_h
    rounded_card(c, LEFT, card_y, CONTENT_W, card_h, radius=14, fill=WHITE, stroke=SAND, stroke_width=1.2)
    # accent bar on the right edge of the card
    c.setFillColor(AMBER)
    c.roundRect(RIGHT - 6, card_y + 10, 4, card_h - 20, 2, stroke=0, fill=1)
    ty = y - pad - text_size
    for line in wrapped:
        draw_ar_right(c, line, RIGHT - pad - 6, ty, "Cairo", text_size, NAVY_DARK)
        ty -= leading

    # natural soroban photo + caption
    img_y_top = card_y - 24
    img_w, img_h = 330, 185
    img_x = (PAGE_W - img_w) / 2
    img_y = img_y_top - img_h
    draw_image_fitted(c, _img("soroban_desk.jpg"), img_x, img_y, img_w, img_h,
                      pad=8, card=True, card_fill=WHITE, stroke=SAND, radius=14)
    draw_ar_center(c, C.INTRO_IMAGE_CAPTION, PAGE_W / 2, img_y - 18, "Cairo", 10.5, GRAY)

    # benefits
    bt_y = img_y - 48
    draw_ar_right(c, C.BENEFITS_TITLE, RIGHT, bt_y, "Cairo-Bold", 15.5, AMBER)
    _diamond(c, RIGHT - pdf_string_w(C.BENEFITS_TITLE, "Cairo-Bold", 15.5) - 12, bt_y + 4, 4, NAVY)
    row_y = bt_y - 30
    row_h = 30
    for benefit in C.BENEFITS:
        rounded_card(c, LEFT, row_y - row_h + 8, CONTENT_W, row_h, radius=11, fill=WHITE, stroke=SAND, stroke_width=1.1)
        c.setFillColor(NAVY)
        c.circle(RIGHT - 16, row_y - row_h / 2 + 8, 5, stroke=0, fill=1)
        draw_ar_right(c, benefit, RIGHT - 32, row_y - row_h / 2 + 4, "Cairo-SemiBold", 12, NAVY_DARK)
        row_y -= row_h + 7


# ---------------------------------------------------------------------------
# SITTING POSTURE
# ---------------------------------------------------------------------------
def _posture_card(c, x, y_top, w, h, correct, label, points, accent):
    rounded_card(c, x, y_top - h, w, h, radius=16, fill=WHITE, stroke=accent, stroke_width=1.6)
    draw_ar_right(c, label, x + w - 18, y_top - 28, "Cairo-Bold", 15, accent)

    drawing_w, drawing_h = 250, h - 84
    drawing_x = x + (w - drawing_w) / 2
    drawing_y = y_top - h + 46
    drawing = make_posture_drawing(drawing_w, drawing_h, correct=correct)
    renderPDF.draw(drawing, c, drawing_x, drawing_y)

    chip_y = drawing_y - 18
    chip_h = 26
    n = len(points)
    gap = 8
    total_w = w - 32
    chip_w = (total_w - gap * (n - 1)) / n
    cx0 = x + 16
    for point in points:
        _badge(c, cx0 + chip_w / 2, chip_y, point, accent, w=chip_w, h=chip_h, size=11)
        cx0 += chip_w + gap


def page_sitting(c):
    _background(c)
    y = _page_header(c, C.SITTING_TITLE, accent=NAVY)

    # mascot + speech bubble
    mascot_w, mascot_h = 78, 90
    mascot_x = LEFT
    mascot_y = y - mascot_h + 12
    renderPDF.draw(make_mascot_drawing(mascot_w, mascot_h, body_color=NAVY), c, mascot_x, mascot_y)

    bubble_x = mascot_x + mascot_w + 14
    bubble_w = CONTENT_W - mascot_w - 14
    bubble_h = 46
    bubble_y = mascot_y + mascot_h - bubble_h - 6
    rounded_card(c, bubble_x, bubble_y, bubble_w, bubble_h, radius=14, fill=WHITE, stroke=SAND, stroke_width=1.2)
    draw_ar_center(c, C.SITTING_INTRO, bubble_x + bubble_w / 2, bubble_y + bubble_h / 2 - 4, "Cairo-SemiBold", 12.5, NAVY)

    card_top = mascot_y - 24
    card_h = 318
    _posture_card(c, LEFT, card_top, CONTENT_W, card_h, True, C.CORRECT_LABEL, C.CORRECT_POINTS, CORRECT_GREEN)

    card_top2 = card_top - card_h - 18
    card_h2 = 300
    _posture_card(c, LEFT, card_top2, CONTENT_W, card_h2, False, C.INCORRECT_LABEL, C.INCORRECT_POINTS, INCORRECT_RED)


# ---------------------------------------------------------------------------
# USAGE STEPS
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
    elif kind == "pencil":
        c.saveState()
        c.translate(cx, cy)
        c.rotate(40)
        c.rect(-4, -16, 8, 28, stroke=1, fill=0)
        c.line(-4, 12, 0, 20)
        c.line(4, 12, 0, 20)
        c.restoreState()
    elif kind == "hands":
        c.ellipse(cx - 16, cy - 8, cx - 2, cy + 8, stroke=1, fill=0)
        c.ellipse(cx + 2, cy - 8, cx + 16, cy + 8, stroke=1, fill=0)
    elif kind == "focus":
        c.ellipse(cx - 16, cy - 9, cx + 16, cy + 9, stroke=1, fill=0)
        c.circle(cx, cy, 5, stroke=0, fill=1)
    c.restoreState()


def page_posture(c):
    _background(c)
    y = _page_header(c, C.USAGE_TITLE, accent=AMBER)

    mascot_w, mascot_h = 108, 128
    mascot_x = LEFT
    mascot_y = y - mascot_h + 10
    renderPDF.draw(make_mascot_drawing(mascot_w, mascot_h, body_color=NAVY), c, mascot_x, mascot_y)

    bubble_x = mascot_x + mascot_w + 14
    bubble_w = CONTENT_W - mascot_w - 14
    bubble_h = 56
    bubble_y = mascot_y + mascot_h - bubble_h - 10
    rounded_card(c, bubble_x, bubble_y, bubble_w, bubble_h, radius=14, fill=WHITE, stroke=SAND, stroke_width=1.2)
    wrapped = wrap_arabic(C.MASCOT_SPEECH, "Cairo-SemiBold", 13, bubble_w - 28)
    ty = bubble_y + bubble_h / 2 + (len(wrapped) - 1) * 9
    for line in wrapped:
        draw_ar_center(c, line, bubble_x + bubble_w / 2, ty, "Cairo-SemiBold", 13, NAVY)
        ty -= 18

    grid_top = mascot_y - 28
    card_w = (CONTENT_W - 16) / 2
    card_h = 168
    gap_x, gap_y = 16, 16
    icons = ["sit", "pencil", "hands", "focus"]
    colors = [NAVY, AMBER, NAVY, AMBER]

    for idx, (step_title, step_desc) in enumerate(C.POSTURE_STEPS):
        col = idx % 2
        row = idx // 2
        cx0 = LEFT + col * (card_w + gap_x)
        cy0 = grid_top - row * (card_h + gap_y) - card_h
        rounded_card(c, cx0, cy0, card_w, card_h, radius=14, fill=WHITE, stroke=SAND, stroke_width=1.2)

        c.setFillColor(colors[idx])
        c.circle(cx0 + card_w - 26, cy0 + card_h - 30, 16, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Cairo-Bold", 14)
        c.drawCentredString(cx0 + card_w - 26, cy0 + card_h - 34.5, str(idx + 1))

        _step_icon(c, icons[idx], cx0 + 30, cy0 + card_h - 30, colors[idx])

        draw_ar_right(c, step_title, cx0 + card_w - 18, cy0 + card_h - 68, "Cairo-Bold", 14.5, NAVY)
        wrapped_desc = wrap_arabic(step_desc, "Cairo", 11.5, card_w - 36)
        ty = cy0 + card_h - 88
        for line in wrapped_desc:
            draw_ar_right(c, line, cx0 + card_w - 18, ty, "Cairo", 11.5, GRAY)
            ty -= 17

    tip_y_top = grid_top - 2 * (card_h + gap_y) - 14
    tip_h = 70
    rounded_card(c, LEFT, tip_y_top - tip_h, CONTENT_W, tip_h, radius=14, fill=AMBER, stroke=None)
    wrapped_tip = wrap_arabic(C.USAGE_TIP, "Cairo-SemiBold", 13, CONTENT_W - 40)
    ty = tip_y_top - tip_h / 2 + (len(wrapped_tip) - 1) * 9
    for line in wrapped_tip:
        draw_ar_center(c, line, PAGE_W / 2, ty, "Cairo-SemiBold", 13, WHITE)
        ty -= 18


# ---------------------------------------------------------------------------
# PARTS
# ---------------------------------------------------------------------------
def page_parts(c):
    _background(c)
    y = _page_header(c, C.PARTS_TITLE, accent=AMBER)

    diagram_w, diagram_h = 380, 230
    diagram_x = (PAGE_W - diagram_w) / 2
    diagram_y = y - diagram_h - 70

    card_pad = 16
    rounded_card(
        c, diagram_x - card_pad, diagram_y - card_pad, diagram_w + 2 * card_pad, diagram_h + 2 * card_pad,
        radius=16, fill=WHITE, stroke=SAND, stroke_width=1.2,
    )
    drawing = make_soroban_drawing(diagram_w, diagram_h, rods=7, active_rod=2, active_value=6)
    renderPDF.draw(drawing, c, diagram_x, diagram_y)

    anchors = get_anchor_points(diagram_w, diagram_h, rods=7, label_rod=2)
    label_targets = {
        "frame": (diagram_x - card_pad - 6, diagram_y + diagram_h + 26, "left"),
        "heaven": (diagram_x - card_pad - 6, diagram_y + diagram_h - 30, "left"),
        "beam": (diagram_x + diagram_w + card_pad + 6, diagram_y + diagram_h * 0.55, "right"),
        "rod": (diagram_x + diagram_w + card_pad + 6, diagram_y + diagram_h * 0.85, "right"),
        "earth": (diagram_x - card_pad - 6, diagram_y + 18, "left"),
    }
    dot_colors = {"frame": AMBER, "heaven": AMBER, "beam": NAVY_DARK, "rod": SILVER, "earth": NAVY}

    c.setLineWidth(1)
    for key, (lx, ly, side) in label_targets.items():
        ax, ay = anchors[key]
        ax += diagram_x
        ay += diagram_y
        c.setStrokeColor(dot_colors[key])
        c.setFillColor(dot_colors[key])
        c.circle(ax, ay, 3.2, stroke=0, fill=1)
        c.line(ax, ay, lx, ly)
        c.circle(lx, ly, 2.4, stroke=0, fill=1)

    name_to_key = {
        "الإطار": "frame",
        "العمود": "rod",
        "الفاصل": "beam",
        "خرز السماء": "heaven",
        "خرز الأرض": "earth",
    }
    list_top = diagram_y - card_pad - 30
    row_h = 32
    for i, (name, desc) in enumerate(C.PARTS):
        ry = list_top - i * row_h
        rounded_card(c, LEFT, ry - row_h + 10, CONTENT_W, row_h - 6, radius=10, fill=WHITE, stroke=SAND, stroke_width=1.1)
        c.setFillColor(dot_colors[name_to_key[name]])
        c.circle(RIGHT - 14, ry - row_h / 2 + 9, 4.5, stroke=0, fill=1)
        draw_ar_right(c, name, RIGHT - 28, ry - row_h / 2 + 4, "Cairo-Bold", 12, NAVY)
        wrapped_desc = wrap_arabic(desc, "Cairo", 10.5, CONTENT_W - 170)
        draw_ar_right(c, wrapped_desc[0], RIGHT - 150, ry - row_h / 2 + 4, "Cairo", 10.5, GRAY)


# ---------------------------------------------------------------------------
# LEVELS OVERVIEW + PER-LEVEL CURRICULUM PAGES
# ---------------------------------------------------------------------------
LEVEL_ACCENTS = [AMBER, HexColor("#2E8B7F"), NAVY]


def page_levels_intro(c):
    _background(c)
    y = _page_header(c, C.LEVELS_INTRO_TITLE, accent=NAVY)

    pad = 20
    wrapped = wrap_arabic(C.LEVELS_INTRO_TEXT, "Cairo", 13, CONTENT_W - 2 * pad)
    card_h = pad * 2 + 21 * len(wrapped) - 7
    card_y = y - card_h
    rounded_card(c, LEFT, card_y, CONTENT_W, card_h, radius=14, fill=WHITE, stroke=SAND, stroke_width=1.2)
    ty = y - pad - 13
    for line in wrapped:
        draw_ar_right(c, line, RIGHT - pad, ty, "Cairo", 13, NAVY_DARK)
        ty -= 21

    # three stacked level summary cards
    top = card_y - 28
    bh = 150
    gap = 18
    for i, lp in enumerate(C.LEVEL_PAGES):
        accent = LEVEL_ACCENTS[i]
        by_top = top - i * (bh + gap)
        by = by_top - bh
        rounded_card(c, LEFT, by, CONTENT_W, bh, radius=16, fill=WHITE, stroke=SAND, stroke_width=1.2)
        # left accent block with the level number
        c.setFillColor(accent)
        c.roundRect(LEFT, by, 96, bh, 16, stroke=0, fill=1)
        c.rect(LEFT + 80, by, 16, bh, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Cairo-Black", 40)
        c.drawCentredString(LEFT + 48, by + bh / 2 - 4, str(i + 1))
        draw_ar_center(c, lp["name"], LEFT + 48, by + 20, "Cairo-Bold", 12, WHITE)

        # right side text
        tx = RIGHT - 14
        draw_ar_right(c, lp["ordinal"] + " — " + lp["range"], tx, by_top - 28, "Cairo-Bold", 15, accent)
        obj_lines = wrap_arabic(lp["objective"], "Cairo", 11, CONTENT_W - 96 - 40)
        oy = by_top - 50
        for line in obj_lines[:2]:
            draw_ar_right(c, line, tx, oy, "Cairo", 11, NAVY_DARK)
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
    accent = LEVEL_ACCENTS[idx]
    _background(c)

    # header band with level number
    y = PAGE_H - 56
    c.setFillColor(accent)
    c.circle(RIGHT - 18, y - 4, 18, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("Cairo-Black", 18)
    c.drawCentredString(RIGHT - 18, y - 10, str(idx + 1))
    draw_ar_right(c, lp["ordinal"], RIGHT - 44, y, "Cairo-Black", 21, NAVY)
    draw_ar_right(c, lp["range"], RIGHT - 44, y - 22, "Cairo-SemiBold", 13, accent)
    c.setStrokeColor(accent)
    c.setLineWidth(3)
    c.line(LEFT, y - 36, RIGHT, y - 36)
    y -= 64

    # objective card
    pad = 18
    obj_lines = wrap_arabic(lp["objective"], "Cairo", 12.5, CONTENT_W - 2 * pad)
    obj_h = pad * 2 + 20 * len(obj_lines) - 7
    obj_y = y - obj_h
    rounded_card(c, LEFT, obj_y, CONTENT_W, obj_h, radius=14, fill=WHITE, stroke=SAND, stroke_width=1.2)
    c.setFillColor(accent)
    c.roundRect(RIGHT - 6, obj_y + 10, 4, obj_h - 20, 2, stroke=0, fill=1)
    ty = y - pad - 12.5
    for line in obj_lines:
        draw_ar_right(c, line, RIGHT - pad - 6, ty, "Cairo", 12.5, NAVY_DARK)
        ty -= 20
    y = obj_y - 26

    # skills list
    draw_ar_right(c, "المهارات المستهدفة", RIGHT, y, "Cairo-Bold", 14.5, NAVY)
    y -= 26
    for skill in lp["skills"]:
        rounded_card(c, LEFT, y - 24, CONTENT_W, 30, radius=11, fill=WHITE, stroke=SAND, stroke_width=1.1)
        c.setFillColor(accent)
        _diamond(c, RIGHT - 16, y - 9, 4.5, accent)
        draw_ar_right(c, skill, RIGHT - 32, y - 13, "Cairo-SemiBold", 12, NAVY_DARK)
        y -= 36
    y -= 6

    # exercise box (number -> soroban matching, like a printable worksheet)
    ex_lines = lp["exercise_digits"]
    n = len(ex_lines)
    ex_top = y
    row_h = 70
    ex_h = 44 + n * row_h
    ex_y = ex_top - ex_h
    rounded_card(c, LEFT, ex_y, CONTENT_W, ex_h, radius=16, fill=WHITE, stroke=accent, stroke_width=1.6)
    # exercise title strip
    c.setFillColor(accent)
    c.roundRect(LEFT, ex_top - 34, CONTENT_W, 34, 16, stroke=0, fill=1)
    c.rect(LEFT, ex_top - 34, CONTENT_W, 17, stroke=0, fill=1)
    draw_ar_center(c, lp["exercise_title"], PAGE_W / 2, ex_top - 23, "Cairo-Bold", 13, WHITE)

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
        c.setFillColor(CREAM)
        c.circle(col_num_x, ry, 20, stroke=0, fill=1)
        c.setStrokeColor(accent)
        c.setLineWidth(1.4)
        c.circle(col_num_x, ry, 20, stroke=1, fill=0)
        draw_ar_center(c, _arabic_num(num), col_num_x, ry - 9, "Cairo-Black", 20, NAVY)
        # connection anchor dots
        c.setFillColor(SILVER)
        c.circle(col_num_x - 26, ry, 2.4, stroke=0, fill=1)
        c.circle(col_sor_x + 30, ry, 2.4, stroke=0, fill=1)
        # soroban (left) — shuffled so it's a real matching task
        sd = make_digit_drawing(shuffled[i], 40, 64)
        renderPDF.draw(sd, c, col_sor_x - 20, ry - 32)
        ry -= row_h


def _arabic_num(n):
    western = str(n)
    mapping = {"0": "٠", "1": "١", "2": "٢", "3": "٣", "4": "٤",
               "5": "٥", "6": "٦", "7": "٧", "8": "٨", "9": "٩"}
    return "".join(mapping.get(ch, ch) for ch in western)
