# Novelty search, paper E

Paper E asks whether tuberculosis (TB) case finding and treatment fell in 2025 in countries that lost
United States funding, using the notifications and treatment counts national programmes reported to WHO.
As for papers C and D, **Section 1 (protocol) is committed before any search in Section 2 is run**, so
the inclusion criteria cannot be shaped by what the searches return.

---

## 1. Protocol (declared 15 November 2026, before searching)

### 1.1 Questions

**E (primary).** Has any published study measured, from reported (not modelled or projected) programme
data, the change in TB case notifications, testing or treatment initiation between 2024 and 2025 in
countries exposed to the 2025 reductions in US foreign assistance, either across two or more countries
or by comparing exposed with unexposed countries?

**E-data (secondary).** Has any published study measured whether the completeness or timeliness of TB
surveillance reporting changed after the 2025 reductions in US foreign assistance?

### 1.2 Sources

- PubMed via NCBI E-utilities and Europe PMC REST (includes preprints), run by
  `docs/run_novelty_search_E.py`.
- The records already retrieved on 15 November 2026 by query C1 (`docs/novelty_hits.json`), which
  covers TB and the 2025 US reductions, re-screened against question E.
- WHO, *Global tuberculosis report 2026*, read in full for any analysis of 2025 notifications or
  treatment by exposure to the funding reductions. WHO is the most likely source of such an analysis, as
  it holds the same data.

### 1.3 Queries (run as written; any later change is logged in Section 2 with its reason)

E1. `tuberculosis AND (USAID OR PEPFAR OR "foreign aid" OR "foreign assistance" OR "US funding" OR "funding cut*" OR "aid cut*" OR "donor funding") AND (notification* OR "case finding" OR "case detection" OR "case notification*" OR testing OR diagnos* OR "treatment initiation" OR "service delivery" OR "service disruption*" OR disruption*)` — 2025 onwards.

E2. `tuberculosis AND (surveillance OR "health information system*" OR "data quality" OR "data system*" OR reporting OR DHIS2) AND (USAID OR PEPFAR OR "foreign assistance" OR "foreign aid" OR "funding cut*" OR "aid cut*")` — 2025 onwards.

### 1.4 Inclusion and verdict rules

A record **refutes** paper E's novelty if it reports, from reported programme data, the 2024–2025 change
in TB notifications, testing or treatment initiation for two or more countries in relation to exposure
to the US reductions. It **narrows** the claim if it does so for one country, uses modelled or survey
data (for example, rapid assessments of service disruption), covers only part of 2025, or reports only
global or regional aggregates without relating them to exposure. Everything else is context. The same
rules apply to question E-data with "completeness or timeliness of reporting" in place of the outcomes.

Verdicts: **STANDS**, **NEEDS NARROWING** (the claim is restated to exclude what narrowing records
cover), **REFUTED** (the paper is reconsidered).

Every refuting or narrowing record is read in full (abstract at minimum, full text where open) before a
verdict is recorded.

---

## 2. Searches run (15 November 2026)

Queries E1 and E2 were run exactly as written by `docs/run_novelty_search_E.py`. Raw results:
`docs/novelty_hits_E.json`. Europe PMC returned 1,119 records for E1, of which the first 1,000 by
relevance were retrieved (cursor paging stopped at the declared cap), and all 786 for E2. Unique records:
1,161 (E1) and 839 (E2). Titles were screened by `docs/screen_E.py` (rule in its docstring), with the C1
records re-screened: 31 unique titles screened in (`docs/screen_titles_E.txt`). A second screen for
titles on notifications or case finding found no record relating them to the 2025 reductions.

### Records read

| Record | What it does | Classification |
|---|---|---|
| WHO, *Global tuberculosis report 2026*, section 3 (Fig. 30–31 and footnote) | For the 23 countries that were US bilateral priorities in 2024 and received Global Fund grants, classifies the 2024–2025 change in total and US bilateral funding into five patterns, and compares the relative change in total funding with relative changes in six programmatic indicators (notifications, TB preventive treatment, ART, rapid testing, bacteriological confirmation, rifampicin-resistance testing). Concludes that in most of the 10 countries reporting reductions there was "no clear-cut impact" in 2025; Cambodia's notifications fell 11% | **Refutes** the primary claim: reported data, 2024–2025, two or more countries, related to exposure |
| Boffa et al., IJTLD Open 2025 (South Africa, PMC11984525) | Survey of 24 organisations; projected fewer people tested and treated; notes the USAID-funded EDR Web system for RR-TB reporting lost support | Narrows (one country; survey; also bears on E-data) |
| IJTLD Open 2026 (South Africa, PMC13657024) | Modelled long-term TB and HIV impacts under stakeholder-informed scenarios | Context (modelled) |
| BMJ Public Health 2026 (Colombia, Kenya, Nepal; PMID 42516717) | Rapid mixed-methods assessment, February–March 2025 | Narrows (survey, early 2025) |
| Ferguson et al., BMC Public Health 2026 (Kenya) | Routine HIV and TB-screening service data with interviews | Narrows (one country) |
| Health Affairs Scholar 2026 (IeDEA, 32 countries) | Rapid survey of HIV service disruption | Context (HIV, survey) |
| NEJM 2026, TB cases and deaths averted by PEPFAR | Modelled contribution of PEPFAR | Context (modelled) |
| Lancet 2025 and Lancet Glob Health 2026 comments; J Travel Med 2025 (Cambodia) | Commentary | Context |

## 3. Verdict

**Paper E: REFUTED as framed.** WHO's own report already relates 2024–2025 funding changes to six
programmatic indicators, including notifications, in the exposed countries, and reports no clear-cut
impact in most. A comparison group, a placebo year and effect sizes would add rigour to a question WHO
has already answered descriptively with a null finding; that is not enough for a paper. Not pursued.

**E-data: STANDS but thin.** No study measures change in reporting completeness or timeliness; the only
evidence is the South African report of the EDR Web system losing support. Kept as a possible section of
other work, not a paper on its own.

**Consequences for papers C and D (recorded here because this search found them):**

- Paper C: the WHO report's five-pattern classification of the same 23 countries anticipates Paper C's
  descriptive core. Paper C cites the report (ref 10) only as the reporting source and does not
  acknowledge or differentiate from that analysis; its novelty search (Section 2 of
  `novelty_search.md`) did not read the report.
- Paper D: the WHO notifications file carries `dr_6m_tx` (people started on a 6-month regimen for
  MDR/RR-TB or pre-XDR-TB), reported by 90 countries for 2024 and 101 for 2025. Paper D's statements
  that BPaL/BPaLM starts were not counted for 2024, that the replacement count does not distinguish the
  6-month regimen, and that WHO should restore a regimen-specific count, are wrong.
