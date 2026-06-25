"""RTL paragraph wrapping for reportlab canvas drawing."""
from reportlab.pdfbase import pdfmetrics
from book.utils import ar


def wrap_arabic(text, font, size, max_width):
    """Word-wrap *logical-order* Arabic text to fit max_width, measuring the
    shaped+bidi width of each candidate line (shaping changes glyph widths)."""
    words = text.split(" ")
    lines = []
    current = []
    for word in words:
        trial = current + [word]
        width = pdfmetrics.stringWidth(ar(" ".join(trial)), font, size)
        if width <= max_width or not current:
            current = trial
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_ar_right(c, text, x_right, y, font, size, color=None):
    """Draw a single line of Arabic, right-aligned at x_right."""
    if color is not None:
        c.setFillColor(color)
    c.setFont(font, size)
    c.drawRightString(x_right, y, ar(text))


def draw_ar_center(c, text, x_center, y, font, size, color=None):
    if color is not None:
        c.setFillColor(color)
    c.setFont(font, size)
    c.drawCentredString(x_center, y, ar(text))


def draw_ar_paragraph(c, text, x_right, y_top, max_width, font, size, leading, color=None):
    """Draw a right-aligned RTL paragraph; returns the y position after the last line."""
    lines = wrap_arabic(text, font, size, max_width)
    y = y_top
    for line in lines:
        draw_ar_right(c, line, x_right, y, font, size, color)
        y -= leading
    return y
