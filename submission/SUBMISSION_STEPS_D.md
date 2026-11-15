# Paper D — submission steps (IJTLD, Letter)

Portal: <http://mc.manuscriptcentral.com/ijtld>. Article type: **Letter** (1,100 words, 1 figure, 15
references, no abstract, no text headings, starts "Dear Editor"). No fee within length; do **not** upload
supplementary material (hosting costs EUR 350 per 10 pages).

Before uploading (build first: `check_d.py` also inspects the built Word file):

```bash
cd "D:/onehealth amr meta nma/tb_financing_shocks" && python -I submission/build_d.py && python -I verification/check_d.py && python -I verification/check_self_similarity.py
```

Upload from `submission/paper_d/`:

| File | Portal item |
|---|---|
| `03_letter.docx` | Main document: title page, letter, references, figure legend and the embedded figure, as IJTLD's single-Word-document rule asks; 1.5 spacing, continuous line numbers |
| `04_Figure_1.tif` | Figure (600 dpi), only if the portal requires a separate figure file |
| `02_cover_letter.docx` | Cover letter |

Portal fields: title, running head and keywords from the title page; funding none; conflicts none.
IJTLD also asks for its electronic copyright form at submission.

IJTLD form, checked automatically by `check_d.py`: superscript citations; title of at most 110 characters
without abbreviations; running head of at most 45 characters; 3–5 keywords not in the title; first author
and "et al." for more than three authors; no DOIs on journal references; an ethics statement; figure embedded
and lines numbered in the built file; the cover letter's title and counts equal the letter's.

Decide first: submit the letter now, or hold it and run the full pre-registered test on WHO's 2027
release (2025 data on regimens of 12 months or less, 127 countries). The letter states the plan exists.

Read the PDF the portal builds before approving: superscripts, line numbers, references 1–8, figure.
