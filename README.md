# الحساب الذهني باستخدام السوروبان

A children's Arabic mental-math book (ages 6-10) about the soroban abacus,
generated as both PDF and Word documents from a single source of content.

## Pages

1. Cover — title, author, 3 level badges, soroban illustration
2. Introduction — what a soroban is, benefits list, captioned illustration
3. Correct posture — mascot character + step cards (sitting, pencil grip, hand position, focus)
4. Parts of the soroban — labeled diagram (frame, rods, beam, heaven/earth beads)

## Setup

```bash
pip install -r requirements.txt
```

Cairo font static instances are committed under `assets/fonts/` (built once
via `fonttools varLib.instancer` from the variable font in Google's
`google/fonts` GitHub repo, since `fonts.google.com` itself isn't reachable
from every network).

## Build

```bash
python3 -m book.build_pdf    # -> output/soroban_book.pdf
python3 -m book.build_docx   # -> output/soroban_book.docx
```

## Customizing content

All Arabic copy lives in `book/content.py`, including `AUTHOR_NAME` (currently
a placeholder) and `INTRO_TEXT` (currently placeholder copy — replace with the
author-supplied introduction text).

## Project structure

- `book/utils.py` — Arabic reshaping/bidi (`ar()`), font registration, design-system colors
- `book/drawings.py` — vector soroban + mascot illustrations (reportlab shapes)
- `book/text.py` — RTL paragraph wrapping for canvas drawing
- `book/pages.py` — the 4 PDF pages
- `book/build_pdf.py` — PDF entry point
- `book/build_docx.py` — Word entry point (RTL via raw OOXML `w:bidi`)
- `book/raster.py` — rasterizes the vector drawings to PNG for docx embedding
