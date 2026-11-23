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

## 11. Post hoc extension after an editorial decision (24 November 2026; written before computing anything below)

**Status.** Everything in this section is post hoc. The letter was declined without review on 21 November
2026; the editor judged the amount of new information small. The analyses below were chosen after that
decision, and after the results in Sections 9 and 10 were known, to describe the fall in more detail. They
are labelled post hoc wherever they are reported. No new data source is added; the WHO files, the balanced
panels, the minimum count of 20 patients started, the 99th-percentile rule and the deflator are those of
Sections 3, 4 and 9.

**Correction of a description.** WHO's data dictionary defines `exp_cpp_mdr` as the "average cost of drugs
spent per person starting second-line treatment for MDR-TB, excluding buffer stock". Outcome 2 is therefore
a reported drug cost per patient, not total spending per patient, and is described as such from now on. Both
outcomes measure drugs. Spending on everything else is read from `exp_mdrmgt` ("actual expenditure on
programme costs to treat drug-resistant TB").

**Common definitions.**

- *Panels:* for each outcome, the balanced panel of Section 9 (`d_regimen.balanced`): countries with the
  outcome in both 2019 and 2024 after the rules of Section 4.
- *Real change:* the 2024/2019 ratio multiplied by the deflator ratio used in Section 9 (US GDP deflator
  from WHO's processed file, 2024 dollars), minus 1.
- *Missing values:* the public file prints 0 for some missing amounts, so a reported 0 for `exp_sld` or
  `exp_mdrmgt` is treated as missing, as for the outcomes already.

**(a) Distribution and subgroups.** For each outcome, the per-country real change: median, interquartile
range (quartiles by the inclusive method), and the share of countries falling, in real and in current
dollars. Breakdowns by WHO region (`g_whoregion`, expenditure file) and by World Bank income group
(`g_income` for 2024 in WHO's processed finance file, whose source archive is verified against its recorded
digest; the file holds only low- and middle-income countries, so high-income countries are absent).
Countries without an income group are reported as unclassified. Subgroups are described, not tested;
those with fewer than 5 countries are reported but not interpreted.

**(b) Composition.** Composition panel: countries in the outcome 1 panel that also report `exp_mdrmgt`
above 0 in both 2019 and 2024. A country is excluded if its programme spending per patient started in
either year exceeds the 99th percentile of that ratio pooled over 2017-2024 (the Section 4 rule). Reported:

- the median drug share of drug-resistant TB spending, `exp_sld / (exp_sld + exp_mdrmgt)`, in 2019 and 2024;
- the median real change per patient started in drug spending, in programme spending and in their sum;
- a pooled decomposition: total drug and programme spending divided by total patients started, across the
  panel, in 2019 and 2024 (real); the share of the change in the pooled total per patient that comes from
  drugs. The fall is called "mostly drugs" if that share exceeds one half.
- As a consistency check, the rank correlation between the per-country changes in the two drug measures
  (outcome 1 and outcome 2) where both are available.

**(c) Treated numbers and total spending ("reinvestment").** In each outcome panel: the total number of
people started on RR-TB treatment in 2019 and 2024, total real second-line drug spending (outcome 1 panel)
and, in the composition panel, total real drug plus programme spending; the pooled spending per patient;
the per-country change in log patients started against the change in log real spending per patient (rank
correlation, and counts in the four quadrants of rise and fall). Wording is fixed in advance:

- total real spending fell and the total started did not rise: "savings not visibly reinvested";
- total real spending fell and the total started rose: "numbers treated rose by x% while total spending
  fell by y%";
- total real spending rose: reported as such.

Caveats to be stated with any of these: the treatment-count definition changed in 2020 (Section 9 join
ratio 0.88); COVID-19 reduced case finding in 2020-2021; spending through other channels (for example
drugs donated or procured outside the programme budget) is not visible; numbers treated depend on
detection, not only on money. Sensitivity: the same totals and per-country comparison from 2020 to 2024,
when the treatment-count definition was constant, in panels built by the same rules for 2020 and 2024.

**(d) Timing.** In addition to the share of the 2019-2024 fall in the panel median present by 2021
(Section 9), the share present by 2022, the last year before the December 2022 BPaLM recommendation could
affect a full year of spending, and the year with the largest single-year fall in the panel median.

**What these analyses will not claim.** No cause for any change; no comparison of regions or income groups
beyond description; no statement about patients' outcomes or costs. The analyses are descriptive and were
chosen after the results were known; their findings are hypotheses for the prospective test of Section 10.
