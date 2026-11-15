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

## 2. Searches run (15 November 2026)

Queries C1, C2, D1 and D2 were run exactly as written by `docs/run_novelty_search.py` (PubMed via
E-utilities; Europe PMC REST). Raw results: `docs/novelty_hits.json`. Europe PMC searches full text and
returned its 300-record page cap for C1, C2 and D1, so all records were title-screened
(`docs/screen_titles.txt`): 50 (C1), 42 (C2), 23 (D1) and 27 (D2) records screened in.

### Paper C — records read

| Record | What it does | Classification |
|---|---|---|
| Wells et al. 2026, PLOS Glob Public Health (PMID 42213766) | Projects whether health-budget growth *could* compensate for full donor withdrawal in high-burden countries | Context: capacity projection, not observed replacement |
| Mandal et al. 2025, PLOS Glob Public Health (PMID 40929049) | Models TB cases and deaths from US funding cuts in 26 high-burden countries | Context: modelled |
| Clark et al. 2025 / medRxiv, Lancet Glob Health (PMIDs 40659023, 40313294); Lancet Glob Health 2025 (40975076) | Model the impact of donor reductions | Context: modelled |
| Limula et al. 2026, BMJ Public Health (PMID 42568929) | Domestic and donor spending vs TB outcomes in Africa, 1990–2022 | Context: ends before 2025 |
| Ferguson et al. 2026, BMC Public Health (PMID 42989235) | Immediate impacts of US cuts in Kenya, qualitative and service data | Context: one country, not financing replacement |
| Sriram 2026, Front Health Serv (PMID 42688228) | Policy brief; states most recipient governments have not reprioritised budgets | Context: assertion without TB country data, which paper C tests |
| Sfeir 2026, Lancet Glob Health (PMID 41386238) | Comment | Context |

No record reports, from reported financing data, country-level replacement of the 2025 US reductions for
TB. **Verdict, paper C: STANDS.** The claim is stated narrowly: the first country-level account of what
replaced US government TB funding in 2025, using WHO's reported 2025 data; Wells et al. are cited as the
capacity estimate that paper C tests against observed behaviour.

### Paper D — records read (titles and abstracts)

All screened records are single-setting cost-effectiveness analyses, trial-based economic evaluations or
budget-impact models of BPaL/BPaLM or shorter regimens (e.g. TB-PRACTECAL sites, Lancet Glob Health 2025;
STREAM stage 2, Lancet Glob Health 2023; South Africa and the Philippines, IJTLD Open 2025; India, Int J
Technol Assess Health Care 2025; China CDC Weekly 2026; Moldova, PLoS Med 2024), or single-programme
costings. None estimates change in programme expenditure per patient across countries from reported
expenditure. **Verdict, paper D: STANDS**, stated as: the first cross-country analysis of reported
programme expenditure per RR-TB patient around the adoption of shorter all-oral regimens. The trial and
modelled evaluations are the expectations it tests.
