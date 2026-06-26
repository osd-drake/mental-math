"""Vector illustrations: soroban abacus + posture diagrams, built from primitive shapes."""
import math
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle, Ellipse, PolyLine, Group, String
from reportlab.lib.colors import HexColor

WOOD = HexColor("#C98A4B")
WOOD_DARK = HexColor("#8B5A2B")
DECK = HexColor("#FBEBD6")
BEAD_GOLD = HexColor("#C68A3E")   # amber heaven beads (warm wood tone)
BEAD_NAVY = HexColor("#1C3D5F")   # navy earth beads (brand color)
BEAD_TEAL = HexColor("#2C9B8A")   # legacy alias (kept for compatibility)
ROD_COLOR = HexColor("#7A4A23")

# navy / silver / cream palette
NAVY = HexColor("#1C3D5F")
NAVY_DARK = HexColor("#142C45")
SILVER = HexColor("#AEB8C2")
CREAM = HexColor("#F3ECDE")
SAND = HexColor("#E7DCC6")

CORAL = HexColor("#D8593F")
TEAL = HexColor("#2E8B7F")
WHITE = HexColor("#FFFFFF")


def soroban_geometry(width, height, rods=7):
    """Shared layout math so the drawing and the labeled-diagram leader lines agree."""
    frame_margin = 6
    fx, fy = frame_margin, frame_margin
    fw, fh = width - 2 * frame_margin, height - 2 * frame_margin
    inset = 10
    ix, iy = fx + inset, fy + inset
    iw, ih = fw - 2 * inset, fh - 2 * inset
    beam_y = iy + ih * 0.68
    rod_margin = iw * 0.08
    usable_w = iw - 2 * rod_margin
    spacing = usable_w / (rods - 1) if rods > 1 else 0
    return dict(fx=fx, fy=fy, fw=fw, fh=fh, ix=ix, iy=iy, iw=iw, ih=ih,
                beam_y=beam_y, rod_margin=rod_margin, spacing=spacing)


def get_anchor_points(width, height, rods=7, label_rod=2):
    """Page coordinates (relative to the drawing's own origin) for leader lines."""
    g = soroban_geometry(width, height, rods)
    rod_x = g["ix"] + g["rod_margin"] + label_rod * g["spacing"]
    bead_ry = g["spacing"] * 0.30 * 1.0
    return {
        "frame": (g["fx"] + 6, g["fy"] + g["fh"] - 10),
        "rod": (rod_x, g["iy"] + g["ih"] * 0.40),
        "beam": (g["ix"] + g["iw"] * 0.62, g["beam_y"]),
        "heaven": (rod_x, g["iy"] + g["ih"] - 10 - 7.5),
        "earth": (rod_x, g["iy"] + 8 + 7.5),
    }


def make_soroban_drawing(width=300, height=190, rods=7, active_rod=4, active_value=6):
    """A simplified, decorative soroban: frame, beam, rods, beads.
    active_rod/active_value purely decorative (which rod shows beads pulled to beam)."""
    d = Drawing(width, height)
    g = soroban_geometry(width, height, rods)
    fx, fy, fw, fh = g["fx"], g["fy"], g["fw"], g["fh"]
    ix, iy, iw, ih = g["ix"], g["iy"], g["iw"], g["ih"]
    beam_y = g["beam_y"]

    # outer wooden frame
    d.add(Rect(fx, fy, fw, fh, rx=14, ry=14, fillColor=WOOD, strokeColor=WOOD_DARK, strokeWidth=2))

    # inner deck (cream)
    d.add(Rect(ix, iy, iw, ih, rx=8, ry=8, fillColor=DECK, strokeColor=None))

    # the horizontal beam (separates heaven/5-beads from earth/1-beads), positioned ~32% from top
    beam_h = 7
    d.add(Rect(ix, beam_y - beam_h / 2, iw, beam_h, fillColor=WOOD_DARK, strokeColor=None))

    rod_margin, spacing = g["rod_margin"], g["spacing"]
    bead_rx, bead_ry = spacing * 0.30, 7.5

    for i in range(rods):
        rod_x = ix + rod_margin + i * spacing
        d.add(Line(rod_x, iy + 4, rod_x, iy + ih - 4, strokeColor=ROD_COLOR, strokeWidth=1.6))

        is_active = (i == active_rod)

        # heaven bead (1 bead, value 5) -- rests at top normally, slides down to beam if active
        heaven_top = iy + ih - 10
        if is_active and active_value >= 5:
            heaven_y = beam_y - bead_ry - 3
        else:
            heaven_y = heaven_top - bead_ry
        d.add(Ellipse(rod_x, heaven_y, bead_rx, bead_ry, fillColor=BEAD_GOLD, strokeColor=WOOD_DARK, strokeWidth=0.8))

        # earth beads (4 beads, value 1 each) -- rest at bottom, slide up to beam if active
        n_active_earth = active_value % 5 if is_active else 0
        earth_bottom = iy + 8
        gap = bead_ry * 1.9
        for j in range(4):
            if j < n_active_earth:
                # pulled up to beam, stacked closest-first
                ey = beam_y + bead_ry + 3 + (n_active_earth - 1 - j) * gap
            else:
                ey = earth_bottom + bead_ry + j * gap
            d.add(Ellipse(rod_x, ey, bead_rx, bead_ry, fillColor=BEAD_NAVY, strokeColor=WOOD_DARK, strokeWidth=0.8))

    return d


def make_digit_drawing(value, width=54, height=150, frame=True):
    """A single soroban rod showing one digit (0-9): one heaven bead (value 5)
    above the beam, four earth beads (value 1 each) below. Beads pulled toward
    the beam are 'active'. Used for the level matching exercises."""
    d = Drawing(width, height)
    cx = width / 2

    pad = 6
    inner_top = height - pad
    inner_bot = pad
    if frame:
        d.add(Rect(2, 2, width - 4, height - 4, rx=8, ry=8,
                   fillColor=CREAM, strokeColor=SILVER, strokeWidth=1.4))
        pad = 12
        inner_top = height - pad
        inner_bot = pad

    beam_y = inner_bot + (inner_top - inner_bot) * 0.62
    bead_rx = width * 0.30
    bead_ry = (inner_top - inner_bot) * 0.075

    # rod
    d.add(Line(cx, inner_bot + 2, cx, inner_top - 2, strokeColor=SILVER, strokeWidth=1.6))
    # beam
    d.add(Rect(pad - 2, beam_y - 3, width - 2 * (pad - 2), 6, fillColor=NAVY_DARK, strokeColor=None))

    # heaven bead: down to beam if value>=5, else resting up top
    if value >= 5:
        hy = beam_y + bead_ry + 3
    else:
        hy = inner_top - bead_ry - 2
    d.add(Ellipse(cx, hy, bead_rx, bead_ry, fillColor=BEAD_GOLD, strokeColor=WOOD_DARK, strokeWidth=0.8))

    # earth beads: (value % 5) pulled up to beam, rest resting at bottom
    n_active = value % 5
    gap = bead_ry * 2.05
    for j in range(4):
        if j < n_active:
            ey = beam_y - bead_ry - 3 - (n_active - 1 - j) * gap
        else:
            ey = inner_bot + bead_ry + 2 + (3 - j) * gap
        d.add(Ellipse(cx, ey, bead_rx, bead_ry, fillColor=BEAD_NAVY, strokeColor=WOOD_DARK, strokeWidth=0.8))

    return d


def make_posture_drawing(width=230, height=270, variant="correct1"):
    """Line-art (outline-only) side-view diagram of a child at a desk, used on
    the sitting-posture page. variant:
      - 'correct1'  : back straight, elbows resting on the desk, eye-to-paper
                       distance marked (~25-45cm)
      - 'correct2'  : back resting on the chair, shoulders relaxed, arms at rest
      - 'incorrect' : hunched forward, eye-to-paper distance too short (~8-10cm)
    Drawn almost entirely with thin strokes (not flat color fills) to keep the
    printed page's ink coverage — and cost — low. Only the small correct/incorrect
    badge and the measurement callout carry color."""
    correct = variant != "incorrect"
    accent = TEAL if correct else CORAL
    d = Drawing(width, height)

    floor_y = 24
    hip_x = width * 0.42
    seat_top = floor_y + 58
    hip_y = seat_top + 10

    # ground line
    d.add(Line(10, floor_y, width - 10, floor_y, strokeColor=NAVY_DARK, strokeWidth=1.6, strokeLineCap=1))

    # --- chair: outline only ---
    seat_x = hip_x - 32
    seat_w = 58
    d.add(Line(seat_x + 5, floor_y, seat_x + 5, seat_top, strokeColor=NAVY_DARK, strokeWidth=1.3))
    d.add(Line(seat_x + seat_w - 5, floor_y, seat_x + seat_w - 5, seat_top, strokeColor=NAVY_DARK, strokeWidth=1.3))
    d.add(Rect(seat_x, seat_top, seat_w, 7, rx=3, ry=3, fillColor=WHITE, strokeColor=NAVY_DARK, strokeWidth=1.3))
    d.add(Rect(seat_x + 2, seat_top + 7, 6, 58, rx=3, ry=3, fillColor=WHITE, strokeColor=NAVY_DARK, strokeWidth=1.3))

    # --- desk: outline only; pulled in close for the incorrect posture ---
    desk_gap = 14 if variant == "incorrect" else 32
    desk_x0 = hip_x + desk_gap
    desk_w = width - desk_x0 - 12
    desk_top = seat_top + 38
    d.add(Line(desk_x0, floor_y, desk_x0, desk_top, strokeColor=NAVY_DARK, strokeWidth=1.3))
    d.add(Line(desk_x0 + desk_w, floor_y, desk_x0 + desk_w, desk_top, strokeColor=NAVY_DARK, strokeWidth=1.3))
    d.add(Rect(desk_x0 - 6, desk_top, desk_w + 12, 6, rx=2, ry=2, fillColor=WHITE, strokeColor=NAVY_DARK, strokeWidth=1.3))
    paper_x = desk_x0 + 8
    d.add(Rect(paper_x, desk_top + 6, 26, 3, fillColor=WHITE, strokeColor=NAVY_DARK, strokeWidth=0.9))

    # --- legs: thigh on the seat, shin to the floor, foot flat ---
    knee_x = hip_x + 28
    d.add(Rect(hip_x - 7, seat_top + 7, knee_x - hip_x + 12, 11, rx=5, ry=5, fillColor=WHITE, strokeColor=NAVY_DARK, strokeWidth=1.3))
    d.add(Rect(knee_x, floor_y + 2, 11, seat_top + 9 - floor_y, rx=5, ry=5, fillColor=WHITE, strokeColor=NAVY_DARK, strokeWidth=1.3))
    d.add(Rect(knee_x - 2, floor_y, 20, 7, rx=3, ry=3, fillColor=WHITE, strokeColor=NAVY_DARK, strokeWidth=1.3))

    # --- body group (torso + head), pivots at the hip so it can hunch forward ---
    lean = -32 if variant == "incorrect" else 0
    torso_h = 52
    torso = Rect(-11, 0, 22, torso_h, rx=10, ry=10, fillColor=WHITE, strokeColor=NAVY_DARK, strokeWidth=1.4)
    collar = Line(-6, torso_h - 6, 6, torso_h - 6, strokeColor=NAVY_DARK, strokeWidth=1)
    neck = Rect(-3, torso_h - 4, 6, 9, fillColor=WHITE, strokeColor=NAVY_DARK, strokeWidth=1.1)
    head_cy = torso_h + 19
    head = Circle(3, head_cy, 13, fillColor=WHITE, strokeColor=NAVY_DARK, strokeWidth=1.3)
    eye = Circle(8, head_cy + 1, 1.5, fillColor=NAVY_DARK, strokeColor=None)
    smile = PolyLine([5, head_cy - 5, 8, head_cy - 7, 11, head_cy - 5],
                     strokeColor=NAVY_DARK, strokeWidth=1.1, strokeLineCap=1)

    g = Group(torso, collar, neck, head, eye, smile)
    g.translate(hip_x, hip_y)
    g.rotate(lean)
    d.add(g)

    th = math.radians(lean)

    # --- arm: only drawn reaching the desk for 'correct1' (elbows on table) and
    # 'incorrect' (hunched over it); 'correct2' rests the arm at the side ---
    if variant != "correct2":
        sx, sy = 7, torso_h - 6
        swx = hip_x + sx * math.cos(th) - sy * math.sin(th)
        swy = hip_y + sx * math.sin(th) + sy * math.cos(th)
        hand_x, hand_y = paper_x + 14, desk_top + 9
        d.add(Line(swx, swy, hand_x, hand_y, strokeColor=NAVY_DARK, strokeWidth=4.5, strokeLineCap=1))
        d.add(Circle(hand_x, hand_y, 4, fillColor=WHITE, strokeColor=NAVY_DARK, strokeWidth=1.1))
    else:
        sx, sy = -9, torso_h - 12
        swx = hip_x + sx * math.cos(th) - sy * math.sin(th)
        swy = hip_y + sx * math.sin(th) + sy * math.cos(th)
        d.add(Line(swx, swy, swx - 3, swy - 24, strokeColor=NAVY_DARK, strokeWidth=4.5, strokeLineCap=1))

    # --- eye-to-paper measurement callout (correct1 + incorrect only) ---
    if variant in ("correct1", "incorrect"):
        ex_local, ey_local = 8, head_cy + 1
        ex = hip_x + ex_local * math.cos(th) - ey_local * math.sin(th)
        ey = hip_y + ex_local * math.sin(th) + ey_local * math.cos(th)
        tx, ty = paper_x + 13, desk_top + 9
        d.add(Line(ex, ey, tx, ty, strokeColor=accent, strokeWidth=1, strokeDashArray=[3, 2]))
        d.add(Circle(ex, ey, 2, fillColor=accent, strokeColor=None))
        d.add(Circle(tx, ty, 2, fillColor=accent, strokeColor=None))
        label = "25-45cm" if variant == "correct1" else "8-10cm"
        lx, ly = (ex + tx) / 2 + 4, (ey + ty) / 2 + 10
        d.add(String(lx, ly, label, fontName="Helvetica-Bold", fontSize=8.5, fillColor=accent, textAnchor="middle"))

    # --- check / X badge in the top corner ---
    bx, by = width - 18, height - 16
    d.add(Circle(bx, by, 12, fillColor=WHITE, strokeColor=accent, strokeWidth=2))
    if correct:
        d.add(PolyLine([bx - 5, by, bx - 1, by - 4, bx + 6, by + 5],
                       strokeColor=accent, strokeWidth=2.4, strokeLineCap=1, strokeLineJoin=1))
    else:
        d.add(Line(bx - 5, by - 5, bx + 5, by + 5, strokeColor=accent, strokeWidth=2.4, strokeLineCap=1))
        d.add(Line(bx - 5, by + 5, bx + 5, by - 5, strokeColor=accent, strokeWidth=2.4, strokeLineCap=1))

    return d
