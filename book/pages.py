"""Canvas drawing routines for each page of the book."""
from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor

from book.utils import TEAL, CORAL, GOLD, DARK, BG, WHITE, PAGE_W, PAGE_H, rounded_card, ar
from book.text import draw_ar_right, draw_ar_center, draw_ar_paragraph, wrap_arabic
from book.drawings import make_soroban_drawing, make_mascot_drawing, get_anchor_points
from book import content as C

MARGIN = 42
RIGHT = PAGE_W - MARGIN
LEFT = MARGIN
CONTENT_W = PAGE_W - 2 * MARGIN

GRAY = HexColor("#5B5B6B")


def _background(c):
    c.setFillColor(BG)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)


def _badge(c, x_center, y_center, text, color, w=110, h=34):
    c.saveState()
    c.setFillColor(color)
    c.roundRect(x_center - w / 2, y_center - h / 2, w, h, h / 2, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("Cairo-Bold", 13)
    c.drawCentredString(x_center, y_center - 4.5, ar(text))
    c.restoreState()


# ---------------------------------------------------------------------------
def page_cover(c):
    _background(c)

    # decorative corner blobs (2 accents: teal + gold)
    c.saveState()
    c.setFillAlpha(0.12)
    c.setFillColor(TEAL)
    c.circle(PAGE_W - 30, PAGE_H - 20, 130, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.circle(10, 60, 110, stroke=0, fill=1)
    c.restoreState()

    # soroban illustration card
    card_w, card_h = 340, 220
    card_x = (PAGE_W - card_w) / 2
    card_y = PAGE_H - 90 - card_h
    rounded_card(c, card_x, card_y, card_w, card_h, radius=16, fill=WHITE, stroke=HexColor("#EFE6D8"))
    drawing = make_soroban_drawing(card_w - 40, card_h - 40, rods=7)
    renderPDF.draw(drawing, c, card_x + 20, card_y + 20)

    # title
    title_y = card_y - 46
    lines = wrap_arabic(C.TITLE, "Cairo-Black", 27, CONTENT_W - 20)
    c.setFillColor(DARK)
    for line in lines:
        draw_ar_center(c, line, PAGE_W / 2, title_y, "Cairo-Black", 27, DARK)
        title_y -= 34

    # subtitle
    subtitle_y = title_y - 12
    draw_ar_center(c, C.SUBTITLE, PAGE_W / 2, subtitle_y, "Cairo-SemiBold", 14, TEAL)

    # author
    author_y = subtitle_y - 26
    draw_ar_center(c, f"تأليف: {C.AUTHOR_NAME}", PAGE_W / 2, author_y, "Cairo", 12.5, GRAY)

    # level badges
    badge_y = 96
    spacing = 130
    colors = [GOLD, CORAL, TEAL]
    start_x = PAGE_W / 2 - spacing
    for i, level in enumerate(C.LEVELS):
        _badge(c, start_x + i * spacing, badge_y, level, colors[i])

    c.setFillColor(GRAY)
    c.setFont("Cairo", 9.5)
    c.drawCentredString(PAGE_W / 2, 46, ar("السوروبان للأطفال • سلسلة الحساب الذهني"))


# ---------------------------------------------------------------------------
def _page_header(c, title_text, accent=TEAL):
    y = PAGE_H - 56
    draw_ar_right(c, title_text, RIGHT, y, "Cairo-Black", 21, DARK)
    c.setStrokeColor(accent)
    c.setLineWidth(3)
    c.line(LEFT, y - 12, RIGHT, y - 12)
    return y - 40


def page_intro(c):
    _background(c)
    y = _page_header(c, C.INTRO_TITLE, accent=TEAL)

    # paragraph card
    pad = 20
    text_size, leading = 13.5, 21
    wrapped = wrap_arabic(C.INTRO_TEXT, "Cairo", text_size, CONTENT_W - 2 * pad)
    card_h = pad * 2 + leading * len(wrapped) - (leading - text_size)
    card_y = y - card_h
    rounded_card(c, LEFT, card_y, CONTENT_W, card_h, radius=14, fill=WHITE, stroke=HexColor("#EFE6D8"))
    ty = y - pad - text_size
    for line in wrapped:
        draw_ar_right(c, line, RIGHT - pad, ty, "Cairo", text_size, DARK)
        ty -= leading

    # soroban image + caption
    img_y_top = card_y - 26
    img_w, img_h = 230, 145
    img_x = (PAGE_W - img_w) / 2
    img_y = img_y_top - img_h
    rounded_card(c, img_x, img_y, img_w, img_h, radius=14, fill=WHITE, stroke=HexColor("#EFE6D8"))
    drawing = make_soroban_drawing(img_w - 24, img_h - 24, rods=6)
    renderPDF.draw(drawing, c, img_x + 12, img_y + 12)
    draw_ar_center(c, C.INTRO_IMAGE_CAPTION, PAGE_W / 2, img_y - 18, "Cairo", 10.5, GRAY)

    # benefits section
    bt_y = img_y - 50
    draw_ar_right(c, C.BENEFITS_TITLE, RIGHT, bt_y, "Cairo-Bold", 15.5, CORAL)
    row_y = bt_y - 30
    row_h = 30
    for benefit in C.BENEFITS:
        rounded_card(c, LEFT, row_y - row_h + 8, CONTENT_W, row_h, radius=12, fill=WHITE, stroke=HexColor("#EFE6D8"))
        c.setFillColor(TEAL)
        c.circle(RIGHT - 16, row_y - row_h / 2 + 8, 5, stroke=0, fill=1)
        draw_ar_right(c, benefit, RIGHT - 32, row_y - row_h / 2 + 8 - 4, "Cairo-SemiBold", 12, DARK)
        row_y -= row_h + 7


# ---------------------------------------------------------------------------
def _step_icon(c, kind, cx, cy, color):
    """Tiny vector icon for a posture step, centered at (cx, cy)."""
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
    y = _page_header(c, C.POSTURE_TITLE, accent=CORAL)

    # mascot + speech bubble
    mascot_w, mascot_h = 110, 130
    mascot_x = LEFT
    mascot_y = y - mascot_h + 10
    drawing = make_mascot_drawing(mascot_w, mascot_h)
    renderPDF.draw(drawing, c, mascot_x, mascot_y)

    bubble_x = mascot_x + mascot_w + 14
    bubble_w = CONTENT_W - mascot_w - 14
    bubble_h = 56
    bubble_y = mascot_y + mascot_h - bubble_h - 10
    rounded_card(c, bubble_x, bubble_y, bubble_w, bubble_h, radius=14, fill=WHITE, stroke=HexColor("#EFE6D8"))
    wrapped = wrap_arabic(C.MASCOT_SPEECH, "Cairo-SemiBold", 13, bubble_w - 28)
    ty = bubble_y + bubble_h / 2 + (len(wrapped) - 1) * 9
    for line in wrapped:
        draw_ar_center(c, line, bubble_x + bubble_w / 2, ty, "Cairo-SemiBold", 13, DARK)
        ty -= 18

    grid_top = mascot_y - 24
    card_w = (CONTENT_W - 16) / 2
    card_h = 118
    gap_x, gap_y = 16, 16
    icons = ["sit", "pencil", "hands", "focus"]
    colors = [TEAL, CORAL, TEAL, CORAL]

    for idx, (step_title, step_desc) in enumerate(C.POSTURE_STEPS):
        col = idx % 2
        row = idx // 2
        cx0 = LEFT + col * (card_w + gap_x)
        cy0 = grid_top - row * (card_h + gap_y) - card_h
        rounded_card(c, cx0, cy0, card_w, card_h, radius=14, fill=WHITE, stroke=HexColor("#EFE6D8"))

        # step number badge
        c.setFillColor(colors[idx])
        c.circle(cx0 + card_w - 22, cy0 + card_h - 22, 14, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Cairo-Bold", 13)
        c.drawCentredString(cx0 + card_w - 22, cy0 + card_h - 26.5, str(idx + 1))

        _step_icon(c, icons[idx], cx0 + 26, cy0 + card_h - 24, colors[idx])

        draw_ar_right(c, step_title, cx0 + card_w - 16, cy0 + card_h - 48, "Cairo-Bold", 13.5, DARK)
        wrapped_desc = wrap_arabic(step_desc, "Cairo", 10.8, card_w - 32)
        ty = cy0 + card_h - 66
        for line in wrapped_desc:
            draw_ar_right(c, line, cx0 + card_w - 16, ty, "Cairo", 10.8, GRAY)
            ty -= 15


# ---------------------------------------------------------------------------
def page_parts(c):
    _background(c)
    y = _page_header(c, C.PARTS_TITLE, accent=GOLD)

    diagram_w, diagram_h = 380, 230
    diagram_x = (PAGE_W - diagram_w) / 2
    diagram_y = y - diagram_h - 70

    card_pad = 16
    rounded_card(
        c, diagram_x - card_pad, diagram_y - card_pad, diagram_w + 2 * card_pad, diagram_h + 2 * card_pad,
        radius=16, fill=WHITE, stroke=HexColor("#EFE6D8"),
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
    dot_colors = {"frame": GOLD, "heaven": GOLD, "beam": DARK, "rod": TEAL, "earth": TEAL}

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

    # part list (with descriptions) below the diagram
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
        rounded_card(c, LEFT, ry - row_h + 10, CONTENT_W, row_h - 6, radius=10, fill=WHITE, stroke=HexColor("#EFE6D8"))
        c.setFillColor(dot_colors[name_to_key[name]])
        c.circle(RIGHT - 14, ry - row_h / 2 + 9, 4.5, stroke=0, fill=1)
        draw_ar_right(c, name, RIGHT - 28, ry - row_h / 2 + 4, "Cairo-Bold", 12, DARK)
        wrapped_desc = wrap_arabic(desc, "Cairo", 10.5, CONTENT_W - 170)
        draw_ar_right(c, wrapped_desc[0], RIGHT - 150, ry - row_h / 2 + 4, "Cairo", 10.5, GRAY)
