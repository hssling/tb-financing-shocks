# TB financing shocks: what replaced US funding in 2025, and what happened to spending per RR-TB patient

Reproducible analyses of tuberculosis (TB) financing data reported to the World Health Organization,
behind two manuscripts by Siddalingaiah H S:

- **Paper C — Who replaced US funding for tuberculosis in 2025?** Country by country, how much of the
  2024–2025 fall in USAID funding for national TB programmes was offset by domestic, Global Fund and other
  funding (`src/c_usaid.py`).
- **Paper D — Spending per patient treated for rifampicin-resistant TB, 2017–2024.** Whether spending per
  RR-TB patient fell more where the 6-month BPaL/BPaLM regimen was adopted, and how it changed overall
  (`src/d_regimen.py`).

The manuscripts themselves are not in this repository while they are under review; they will be added on
acceptance.

## What is here

| Path | Content |
|---|---|
| `docs/novelty_search.md` | Pre-registered literature search: protocol committed before any search ran, then results and verdicts |
| `docs/analysis_plan_C.md`, `docs/analysis_plan_D.md` | Analysis plans committed before country-level results were computed, with dated deviation logs |
| `docs/journal_targets.md` | Target journals, checked against their own author guidelines |
| `src/` | The analyses, standard-library Python only |
| `manuscript/make_*.py`, `manuscript/tables_c.md`, `manuscript/figure_*.png` | Tables and figures, rendered from the analyses |
| `verification/` | Checks that each manuscript's tables and quoted numbers match the code, and a text-overlap screen |

## Reproducing

The analyses read WHO's public data and WHO's report-repository files from the companion repository,
[provenance-weighted-priority-setting](https://github.com/hssling/provenance-weighted-priority-setting),
which must be cloned beside this one. Every input is verified against a recorded SHA-256 digest before use.

```bash
git clone https://github.com/hssling/provenance-weighted-priority-setting
git clone https://github.com/hssling/tb-financing-shocks
cd provenance-weighted-priority-setting
python -I tools/fetch_vintages.py          # WHO report-repository files, pinned commits
Rscript tools/convert_vintages.R           # R data to CSV, unchanged
cd ../tb-financing-shocks
python -I src/c_usaid.py
python -I src/d_regimen.py
python manuscript/make_c_figure.py         # figures need matplotlib
python manuscript/make_d_figure.py
```

WHO's report-repository files carry no licence and are not redistributed here or in the companion
repository; the fetch script downloads them from fixed commits.

## Findings at a glance

**Paper C.** Among 12 countries with USAID TB funding in 2024 and complete reported data for 2024 and
2025, USAID funding fell from US$ 111.8 million to US$ 70.4 million and Global Fund funding from US$ 286.2
million to US$ 227.8 million, while domestic funding rose from US$ 580.4 million to US$ 898.0 million.
Five countries fully offset the fall in USAID funding, one partly and three not at all; those that did
not lost Global Fund funding in the same year.

**Paper D.** The pre-specified comparison of BPaL/BPaLM adopters and non-adopters could not be made:
WHO counted BPaL/BPaLM starts only for 2022 and 2023, and few high adopters also reported spending. In the
same 66 countries, spending per RR-TB patient fell by about half in real terms between 2019 and 2024, and
much of the fall preceded WHO's December 2022 recommendation of BPaLM.

## Licence

Code: MIT (see `LICENSE`). Analysis plans, search records and figures: CC BY 4.0.

## Citation

See `CITATION.cff`. Archived at Zenodo with a DOI for each release.
