# Novelty search, papers C and D

Each paper's novelty claim is a claim about a literature, so it is tested by a documented search rather
than asserted. **Section 1 (protocol) is committed before any search in Section 2 is run**, so the
inclusion criteria cannot be shaped by what the searches return.

---

## 1. Protocol (declared 15 November 2026, before searching)

### 1.1 Questions

**Paper C.** Has any published study measured, country by country, whether domestic or other funding
replaced United States Agency for International Development (USAID) or other US government funding for
tuberculosis after the 2025 suspension and termination of US foreign assistance, using reported
(not modelled) financing data?

**Paper D.** Has any published study estimated, across countries, the change in expenditure per patient
treated for rifampicin-resistant or multidrug-resistant TB associated with adoption of shorter all-oral
regimens (BPaL/BPaLM or other ≤12-month regimens), using programme expenditure data?

### 1.2 Sources

- PubMed via NCBI E-utilities (programmatic, reproducible).
- Europe PMC REST API (includes preprints).
- Crossref works search for titles in economics and policy journals not indexed in PubMed.

### 1.3 Queries (run as written; any later change is logged in Section 2 with its reason)

C1. `tuberculosis AND (USAID OR "foreign aid" OR "foreign assistance" OR "donor funding" OR "development assistance" OR PEPFAR) AND (cut* OR reduction* OR withdraw* OR suspension OR freeze OR termination)` — 2025 onwards.
C2. `tuberculosis AND ("domestic financing" OR "domestic funding" OR "domestic resource*") AND (donor OR USAID OR "Global Fund") AND (replace* OR substitut* OR transition OR "fill*")` — 2020 onwards.
D1. `(tuberculosis, multidrug-resistant OR rifampicin-resistant OR MDR-TB OR RR-TB) AND (BPaL OR BPaLM OR pretomanid OR "short* regimen*" OR "all-oral") AND (cost* OR expenditure* OR budget* OR "cost per patient")` — 2019 onwards.
D2. `(MDR-TB OR RR-TB) AND ("expenditure per patient" OR "cost per patient treated" OR "unit cost*") AND (country OR countries OR WHO OR "national programme")` — 2015 onwards.

### 1.4 Inclusion and verdict rules

A record **refutes** a paper's novelty if it reports, from reported (not modelled or projected) data,
country-level estimates answering that paper's question for two or more countries. It **narrows** the
claim if it answers the question for one country, or answers it with modelled data, or reports only
aggregates. Everything else is context.

Verdicts: **STANDS** (no refuting or narrowing record), **NEEDS NARROWING** (narrowing records; the
claim is restated to exclude what they cover), **REFUTED** (a refuting record; the paper is reconsidered).

Every refuting or narrowing record is read in full (abstract at minimum, full text where open) before a
verdict is recorded.

---

## 2. Searches run

(filled in after the protocol above is committed)
