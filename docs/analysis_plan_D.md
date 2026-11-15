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

## 9. Results of the pre-specified analysis, and a post-hoc check (15 November 2026)

**The primary analysis is uninformative.** At the 25% threshold only 2 countries (outcome 1) and 4
(outcome 2) were high adopters of BPaL/BPaLM in 2022–2023; no country reached 50%. Outcome 1 gave a
difference of +1.40 log points (permutation p = 0.044), driven by two countries whose spending rose; at
the 10% threshold it vanished (+0.003, p = 0.99), and the placebo period showed no difference. Outcome 2
gave −0.26 (p = 0.48; −0.51, p = 0.22 at 10%). Rank correlations with adoption intensity were −0.05 and
−0.19. The pre-specified design cannot attribute any change in spending to BPaL: adoption by 2023 was too
limited, and the BPaL count was not collected for 2024.

The join of the RR-TB treatment definitions (2019 vs 2020) gave a median ratio of 0.88 across 102
countries: a moderate break, consistent with the 2020 change in definition and COVID-19.

**Post-hoc, labelled as such:** in a balanced panel of the same 66 countries in 2019 and 2024, median
second-line drug expenditure per patient started fell by 35% (46% in constant dollars) and reported
expenditure per MDR-TB patient by 40% (51%), falling in about three quarters of countries, in adopters and
non-adopters alike. This is descriptive and cannot be attributed to any cause in these data.

## 10. Correction and deviation (15 November 2026, after submission; written before computing anything new)

**Correction.** Section 9 says the BPaL count "was not collected for 2024". That is wrong in substance.
From the 2024 return WHO replaced `mdrxdr_bpalm_tx` with `dr_6m_tx`, the number of people started on a
6-month regimen (BPaLM or BDLLfxC) for MDR/RR-TB or pre-XDR-TB, reported by 90 countries for 2024 and 101
for 2025. The analysis did not read the full data dictionary and missed it. The submitted letter
(IJTLD-11-26-0773) repeated the error and recommended that WHO restore a regimen-specific count.

**Deviation (labelled post hoc).** The pre-specified comparison is repeated with the 2024 count as the
exposure. Everything else in Sections 3-5 is unchanged:

- Exposure: share of people starting RR-TB treatment in 2024 who started a 6-month regimen,
  `dr_6m_tx / started(2024)`, capped at 1. A country with `dr_6m_used = 0` or `dr_6m_tx = 0` is a
  non-adopter; high adoption is a share of 25% or more, as pre-specified.
- Outcomes, windows, minimum counts, outlier rule, permutation test (10 000 permutations, seed
  20261115) and rank correlation: as in Sections 3-5.
- Sensitivity: the 10% threshold and the 2017-2018 placebo window, as pre-specified.

**Known weakness, stated before the result is seen.** The exposure year 2024 lies inside the outcome
window 2023-2024, so the comparison is concurrent rather than prospective, and countries whose spending
was already falling may have adopted faster. A difference in either direction is an association, not an
effect of the regimen. The letter will report the result whatever its direction.
