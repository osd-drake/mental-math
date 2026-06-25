"""Vector illustrations: soroban abacus + mascot, built from primitive shapes."""
import math
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle, Ellipse, PolyLine, Group
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
DARK = HexColor("#1A1A2E")
SKIN = HexColor("#F2CBA3")
HAIR = HexColor("#5A3B22")
SHIRT = HexColor("#3E6488")
CHAIR_COLOR = HexColor("#9AA5AF")
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


def make_mascot_drawing(width=160, height=180, body_color=None, cheek_color=None):
    """A friendly round bead-creature mascot: body, eyes, smile, cheeks, little arms/feet."""
    body_color = body_color or HexColor("#2C9B8A")
    cheek_color = cheek_color or HexColor("#E8614A")
    d = Drawing(width, height)
    cx, cy = width / 2, height / 2 - 8

    # feet
    d.add(Ellipse(cx - 22, cy - 48, 14, 8, fillColor=body_color, strokeColor=None))
    d.add(Ellipse(cx + 22, cy - 48, 14, 8, fillColor=body_color, strokeColor=None))

    # arms
    d.add(Ellipse(cx - 46, cy - 5, 11, 6, fillColor=body_color, strokeColor=None))
    d.add(Ellipse(cx + 46, cy - 5, 11, 6, fillColor=body_color, strokeColor=None))

    # body (round bead shape)
    d.add(Circle(cx, cy, 46, fillColor=body_color, strokeColor=HexColor("#1A1A2E"), strokeWidth=1.4))

    # cheeks
    d.add(Circle(cx - 22, cy - 6, 7, fillColor=cheek_color, strokeColor=None))
    d.add(Circle(cx + 22, cy - 6, 7, fillColor=cheek_color, strokeColor=None))

    # eyes (white + pupil)
    for ex in (-16, 16):
        d.add(Circle(cx + ex, cy + 10, 11, fillColor=HexColor("#FFFFFF"), strokeColor=HexColor("#1A1A2E"), strokeWidth=1))
        d.add(Circle(cx + ex + 2, cy + 8, 5, fillColor=HexColor("#1A1A2E"), strokeColor=None))

    # smile (arc approximated as a polyline)
    smile_pts = []
    for deg in range(200, 341, 10):
        rad = math.radians(deg)
        smile_pts.extend([cx + 16 * math.cos(rad), cy - 6 + 16 * math.sin(rad)])
    d.add(PolyLine(smile_pts, strokeColor=HexColor("#1A1A2E"), strokeWidth=2.4, strokeLineCap=1))

    # little antenna with star tip
    d.add(Line(cx, cy + 46, cx, cy + 60, strokeColor=HexColor("#1A1A2E"), strokeWidth=2))
    d.add(Circle(cx, cy + 64, 5, fillColor=HexColor("#F4A623"), strokeColor=None))

    return d


def make_posture_drawing(width=240, height=250, correct=True):
    """Flat side-view illustration of a child sitting at a desk, facing right:
    upright & relaxed (correct=True) vs. hunched over the desk (correct=False).
    A green check / red X badge marks which is which."""
    accent = TEAL if correct else CORAL
    d = Drawing(width, height)

    floor_y = 28
    hip_x = width * 0.40
    seat_top = floor_y + 66          # height of the chair seat
    hip_y = seat_top + 12            # where the body pivots

    # ground line
    d.add(Line(12, floor_y, width - 12, floor_y, strokeColor=SILVER, strokeWidth=2.4, strokeLineCap=1))

    # --- chair (behind / under the child) ---
    seat_x = hip_x - 36
    seat_w = 64
    d.add(Rect(seat_x + 6, floor_y, 6, seat_top - floor_y, fillColor=CHAIR_COLOR, strokeColor=None))
    d.add(Rect(seat_x + seat_w - 12, floor_y, 6, seat_top - floor_y, fillColor=CHAIR_COLOR, strokeColor=None))
    d.add(Rect(seat_x, seat_top, seat_w, 9, rx=3, ry=3, fillColor=CHAIR_COLOR, strokeColor=None))
    d.add(Rect(seat_x, seat_top + 9, 7, 64, rx=3, ry=3, fillColor=CHAIR_COLOR, strokeColor=None))  # backrest

    # --- desk (in front, to the right) ---
    desk_x0 = hip_x + 46
    desk_w = width - desk_x0 - 14
    desk_top = seat_top + 44
    d.add(Rect(desk_x0, floor_y, 6, desk_top - floor_y, fillColor=WOOD_DARK, strokeColor=None))
    d.add(Rect(desk_x0 + desk_w - 6, floor_y, 6, desk_top - floor_y, fillColor=WOOD_DARK, strokeColor=None))
    d.add(Rect(desk_x0 - 6, desk_top, desk_w + 12, 9, rx=3, ry=3, fillColor=WOOD, strokeColor=None))
    # a little soroban resting on the desk
    d.add(Rect(desk_x0 + 6, desk_top + 9, desk_w - 24, 7, rx=2, ry=2, fillColor=NAVY, strokeColor=None))

    PANTS = NAVY
    # --- legs (sitting): thigh on the seat, shin down to the floor ---
    knee_x = hip_x + 30
    d.add(Rect(hip_x - 8, seat_top + 9, knee_x - hip_x + 14, 13, rx=6, ry=6, fillColor=PANTS, strokeColor=None))
    if correct:
        # shin vertical, foot flat on floor
        d.add(Rect(knee_x + 0, floor_y + 3, 13, seat_top + 12 - floor_y, rx=6, ry=6, fillColor=PANTS, strokeColor=None))
        d.add(Rect(knee_x - 2, floor_y, 24, 8, rx=4, ry=4, fillColor=NAVY_DARK, strokeColor=None))
    else:
        # foot dangling / tucked back under the chair (not grounded)
        d.add(Rect(hip_x - 2, floor_y + 20, 13, seat_top - floor_y - 6, rx=6, ry=6, fillColor=PANTS, strokeColor=None))
        d.add(Rect(hip_x - 6, floor_y + 16, 22, 8, rx=4, ry=4, fillColor=NAVY_DARK, strokeColor=None))

    # --- body group (torso + head), pivots at the hip so it can hunch forward ---
    lean = 0 if correct else -34  # negative = tip forward toward the desk
    torso_h = 56
    torso = Rect(-12, 0, 24, torso_h, rx=11, ry=11, fillColor=SHIRT, strokeColor=NAVY_DARK, strokeWidth=1.2)
    collar = Rect(-9, torso_h - 8, 18, 8, rx=4, ry=4, fillColor=WHITE, strokeColor=None, fillOpacity=0.85)
    neck = Rect(-4, torso_h - 4, 9, 12, fillColor=SKIN, strokeColor=None)
    head_cy = torso_h + 22
    hair = Circle(2, head_cy + 1, 16, fillColor=HAIR, strokeColor=None)
    head = Circle(5, head_cy, 14, fillColor=SKIN, strokeColor=NAVY_DARK, strokeWidth=1.1)
    fringe = Rect(-2, head_cy + 7, 16, 7, rx=3, ry=3, fillColor=HAIR, strokeColor=None)
    eye = Circle(11, head_cy + 1, 1.8, fillColor=NAVY_DARK, strokeColor=None)
    smile = PolyLine([8, head_cy - 6, 12, head_cy - 8, 15, head_cy - 6],
                     strokeColor=NAVY_DARK, strokeWidth=1.2, strokeLineCap=1)

    g = Group(torso, collar, neck, hair, head, fringe, eye, smile)
    g.translate(hip_x, hip_y)
    g.rotate(lean)
    d.add(g)

    # --- arm: drawn in world space so it always connects shoulder -> desk ---
    sx, sy = 8, torso_h - 8           # shoulder in local body coords
    th = math.radians(lean)
    swx = hip_x + sx * math.cos(th) - sy * math.sin(th)
    swy = hip_y + sx * math.sin(th) + sy * math.cos(th)
    hand_x, hand_y = desk_x0 + 16, desk_top + 8
    d.add(Line(swx, swy, hand_x, hand_y, strokeColor=SHIRT, strokeWidth=11, strokeLineCap=1))
    d.add(Circle(hand_x, hand_y, 6, fillColor=SKIN, strokeColor=NAVY_DARK, strokeWidth=1))

    # --- check / X badge in the top corner ---
    bx, by = width - 26, height - 24
    d.add(Circle(bx, by, 16, fillColor=accent, strokeColor=WHITE, strokeWidth=2))
    if correct:
        d.add(PolyLine([bx - 7, by, bx - 2, by - 6, bx + 8, by + 7],
                       strokeColor=WHITE, strokeWidth=3, strokeLineCap=1, strokeLineJoin=1))
    else:
        d.add(Line(bx - 6, by - 6, bx + 6, by + 6, strokeColor=WHITE, strokeWidth=3, strokeLineCap=1))
        d.add(Line(bx - 6, by + 6, bx + 6, by - 6, strokeColor=WHITE, strokeWidth=3, strokeLineCap=1))

    return d
