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

## 2. Searches run

(To be completed after this protocol is committed.)
