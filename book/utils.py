"""Shared helpers: Arabic shaping, fonts, colors, rounded cards."""
import os
import unicodedata
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(BASE_DIR, "assets", "fonts")
IMAGE_DIR = os.path.join(BASE_DIR, "assets", "images")

# Design system
TEAL = HexColor("#2C9B8A")
CORAL = HexColor("#E8614A")
GOLD = HexColor("#F4A623")
DARK = HexColor("#1A1A2E")
BG = HexColor("#FFFDF9")
WHITE = HexColor("#FFFFFF")

PAGE_W, PAGE_H = 595.27, 841.89  # A4 in points

_reshaper = arabic_reshaper.ArabicReshaper(
    {
        "delete_harakat": True,
        "support_ligatures": True,
        "language": "Arabic",
    }
)


_font_cmap = None


def _get_cmap():
    global _font_cmap
    if _font_cmap is None:
        from fontTools.ttLib import TTFont as FTFont
        f = FTFont(os.path.join(FONT_DIR, "Cairo-Regular.ttf"))
        _font_cmap = set(f.getBestCmap().keys())
    return _font_cmap


def _fallback_missing_glyphs(s):
    """Cairo's static instance is missing isolated-form presentation glyphs
    (e.g. U+FE8F). Those are visually identical to the base letter, so fall
    back to the NFKC-normalized base codepoint when the shaped glyph is absent."""
    cmap = _get_cmap()
    return "".join(
        ch if ord(ch) in cmap else unicodedata.normalize("NFKC", ch)
        for ch in s
    )


def ar(text):
    """Reshape + apply bidi algorithm so Arabic renders connected & RTL in reportlab."""
    reshaped = _reshaper.reshape(text)
    reshaped = _fallback_missing_glyphs(reshaped)
    return get_display(reshaped)


def register_fonts():
    fonts = {
        "Cairo": "Cairo-Regular.ttf",
        "Cairo-SemiBold": "Cairo-SemiBold.ttf",
        "Cairo-Bold": "Cairo-Bold.ttf",
        "Cairo-Black": "Cairo-Black.ttf",
    }
    for name, filename in fonts.items():
        path = os.path.join(FONT_DIR, filename)
        pdfmetrics.registerFont(TTFont(name, path))


def rounded_card(c, x, y, w, h, radius=14, fill=WHITE, stroke=None, stroke_width=1):
    """Draw a rounded-rect card. (x, y) = bottom-left corner."""
    c.saveState()
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(stroke_width)
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, radius, stroke=1 if stroke else 0, fill=1)
    c.restoreState()
