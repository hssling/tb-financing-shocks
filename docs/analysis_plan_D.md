# Analysis plan, paper D: did shorter all-oral regimens lower spending per RR-TB patient?

Written and committed 15 November 2026, before any cost outcome was computed against adoption. Section 7
records what was seen before the plan was fixed (variable coverage only).

## 1. Question

Across countries, did spending per person treated for rifampicin-resistant TB (RR-TB) fall more where
the 6-month all-oral BPaL/BPaLM regimen was adopted at scale than where it was not, between a
pre-adoption baseline (2019–2021) and the adoption period (2023–2024)?

## 2. Data

WHO Global TB Programme public data, release of 25 August 2026 (expenditure and utilisation; notifications),
verified against recorded digests. Country-reported values only.

## 3. Variables

**Patients started on RR-TB treatment** (denominator), by year:
2017–2019 `conf_rrmdr_tx` + `unconf_rrmdr_tx`; 2020–2024 `conf_rr_nfqr_tx` + `unconf_rr_nfqr_tx` +
`conf_rr_fqr_tx`. The definition changed in 2020 (fluoroquinolone resistance split out); the join is
tested by comparing 2019 and 2020 totals across countries and reported.

**Outcome 1 (primary): second-line drug expenditure per patient started** = `exp_sld` / patients started,
current US dollars. Both parts are counted values.

**Outcome 2: reported expenditure per MDR-TB patient treated** = `exp_cpp_mdr`, as countries report it.

**Exposure: BPaL/BPaLM adoption intensity** = `mdrxdr_bpalm_tx` / patients started, mean of 2022 and
2023 (the only years the count exists). Countries are classed *high adoption* (≥ 25%), *low adoption*
(> 0 and < 25%) and *non-adopters* (reported zero, or `mdrxdr_bpalm_used` = 0). Countries with no BPaL
data in either year are excluded from exposure-based analyses.

**Secondary exposure: all-oral shorter regimen share** = `mdr_alloral_short_tx` / patients started,
2022–2023.

## 4. Population

Countries with at least 20 patients started on RR-TB treatment in every year used, outcome 1 or 2
reported in at least two baseline years (2019–2021) and at least one adoption-period year (2023–2024),
and an exposure class. Ratios above the 99th percentile of the pooled distribution are flagged and
excluded as implausible (for example a near-zero denominator), with the list reported.

## 5. Analysis

1. **Descriptive:** median outcome by year 2017–2024, overall and by adoption class.
2. **Difference in changes (primary):** for each country, change in log outcome from the baseline mean
   (2019–2021) to the adoption-period mean (2023–2024); compare high-adopters with non-adopters by the
   difference in medians, with a permutation test of exposure labels (10,000 permutations, seed fixed).
   Global price changes (for example in bedaquiline and pretomanid procured through the Global Drug
   Facility) affect all countries and difference out.
3. **Dose-response:** rank correlation between adoption intensity and change in log outcome.
4. **Placebo:** the same comparison for the change from 2017–2018 to 2019–2021, before BPaL existed;
   a difference there indicates pre-existing divergence, not a regimen effect.

## 6. Sensitivity analyses

1. Excluding countries that procure second-line drugs largely outside the Global Drug Facility (China,
   India, the Russian Federation, South Africa), whose price changes may not be shared.
2. Constant US dollars (US GDP deflator from WHO's processed file).
3. Excluding outcome values identical to the country's previous year (possible restatement).
4. Adoption threshold of 10% and 50% in place of 25%.

## 7. Seen before this plan was written

Coverage counts only: `exp_cpp_mdr` reported by about 90 countries a year in 2017–2024; `exp_sld` by
77–102 a year in 2017–2025; `mdrxdr_bpalm_tx` by 39 countries in 2022 and 52 in 2023 and absent in other
years; `mdr_alloral_short_tx` 2020–2023; the RR-TB treatment variables as in Section 3, with 2025 too
sparse to use (22 countries). No outcome has been computed by adoption class.

## 8. What the paper will not claim

That BPaL caused any country's spending change (the design is observational); anything about clinical
outcomes; anything about patient costs, which these data do not record; anything for 2025.
