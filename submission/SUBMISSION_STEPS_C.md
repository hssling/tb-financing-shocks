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
| `04_manuscript.docx` | Manuscript — **upload this one**. The Bulletin is not double-blind: its guidelines (Dec 2024, section 2.4) require the manuscript's title page to give the authors' full names, institution, city, country, ORCID and the corresponding author's postal address |
| `06_Figure_1.png` | Figure 1 (400 dpi) |
| `05_RECORD_checklist.docx` | Reporting checklist |

Do **not** upload `03_manuscript_blinded.docx`; it is kept only in case an editor asks for an anonymised copy.

Portal fields: title, running title, abstract (paste from the manuscript), keywords from the title page;
funding none; competing interests none; AI use as in the manuscript and on the title page.

Author contributions go in the portal, **not** in the manuscript (guidelines, section 2.4). Paste:

> HSS is the sole author and conceived the study, wrote and pre-registered the analysis plan and the
> literature search, obtained and verified the data, carried out the analysis, prepared the tables and
> figure, interpreted the results, wrote and revised the manuscript, approved the final version, and is the
> guarantor of the work.

## Author-only

- The Bulletin asks for the two "what this adds" paragraphs; they are in the cover letter. If the portal
  has dedicated boxes, paste them there too.
- Code, plans and checks are public: https://github.com/hssling/tb-financing-shocks, archived at Zenodo doi:10.5281/zenodo.24245803 (v1.0.0, 15 Nov 2026).
  Add the manuscript to the repository on acceptance and cut a new release.
- Read the PDF the portal builds before approving: author block, tables, references 1–15, figure.
