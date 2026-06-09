# Algorithms Revision Site
**Dr. Mahmoud Wahdan — Revision Sheet**

Interactive exam website generated from the revision sheet PDF.

## Files

| File | Purpose |
|------|---------|
| `index.html` | The full site — open directly in browser or deploy to GitHub Pages |
| `1_parse_pdf.py` | Parses all 266 MCQ questions from the PDF (detects bold = correct answer, handles inline options) |
| `2_generate_site.py` | Generates `index.html` from the parsed JSON data |

## Features
- **262 MCQ questions** extracted from the PDF with correct answers (bold-detected)
- **27 questions** with embedded figures from the PDF
- **Per-question Check Answer** button + global Submit All
- Collapsible explanations
- Search + filter (All / Answered / Unanswered)
- **37 Open-ended questions** with text boxes
- **Cheat Sheet** — sorting, searching, AVL, BFS/DFS, hashing, D&C recurrences
- **Analytics** tab with accuracy stats and chart
- 45-minute countdown timer

## Regenerating the site

```bash
pip install PyMuPDF pdfplumber
python3 1_parse_pdf.py          # requires: general Revision Sheet.pdf in same dir
python3 2_generate_site.py      # reads /tmp/mcq_final.json, outputs index.html
```

## Deploy to GitHub Pages
1. Create a repo, push `index.html` as the only file
2. Settings → Pages → Deploy from branch → main / root
3. Done — no server needed, fully static
