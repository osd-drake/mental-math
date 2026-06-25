"""Vector illustrations: soroban abacus + mascot, built from primitive shapes."""
import math
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle, Ellipse, PolyLine
from reportlab.lib.colors import HexColor

WOOD = HexColor("#C98A4B")
WOOD_DARK = HexColor("#8B5A2B")
DECK = HexColor("#FBEBD6")
BEAD_GOLD = HexColor("#F4A623")
BEAD_TEAL = HexColor("#2C9B8A")
ROD_COLOR = HexColor("#7A4A23")


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
            d.add(Ellipse(rod_x, ey, bead_rx, bead_ry, fillColor=BEAD_TEAL, strokeColor=WOOD_DARK, strokeWidth=0.8))

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
