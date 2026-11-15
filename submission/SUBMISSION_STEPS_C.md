# Paper C — submission steps (Bulletin of the World Health Organization)

Portal: <http://submit.bwho.org>. Article type: **Research**. No author fees.

## Before uploading

```bash
cd "D:/onehealth amr meta nma/tb_financing_shocks" && python -I verification/check_c.py
```

```bash
cd "D:/onehealth amr meta nma/tb_financing_shocks" && python -I verification/check_self_similarity.py
```

```bash
cd "D:/onehealth amr meta nma/tb_financing_shocks" && python -I submission/build_c.py
```

## Upload (from `submission/paper_c/`)

| File | Portal item |
|---|---|
| `02_cover_letter.docx` | Cover letter (carries the two required paragraphs on what is known and what the paper adds) |
| `01_title_page.docx` | Title page |
| `04_manuscript.docx` | Manuscript (with author details) |
| `03_manuscript_blinded.docx` | Upload instead of 04 only if the portal asks for an anonymised manuscript |
| `06_Figure_1.png` | Figure 1 (400 dpi) |
| `05_RECORD_checklist.docx` | Reporting checklist |

Portal fields: title, running title, abstract (paste from the manuscript), keywords from the title page;
funding none; competing interests none; AI use as on the title page.

## Author-only

- The Bulletin asks for the two "what this adds" paragraphs; they are in the cover letter. If the portal
  has dedicated boxes, paste them there too.
- Code, plans and checks are public: https://github.com/hssling/tb-financing-shocks, archived at Zenodo doi:10.5281/zenodo.24245803 (v1.0.0, 15 Nov 2026).
  Add the manuscript to the repository on acceptance and cut a new release.
- Read the PDF the portal builds before approving: tables, references 1–15, figure, and that the blinded copy withholds the archive DOI.
