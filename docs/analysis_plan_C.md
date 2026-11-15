# Analysis plan, paper C: what replaced US government TB funding in 2025?

Written and committed 15 November 2026, before any country-level result was computed. The exploratory
counts that informed it (number of countries with USAID funding by year, totals 2023–2025) are recorded
in Section 6 so that it is clear what was seen before the plan was fixed.

## 1. Question

Among countries whose national TB programmes received US government (USAID) TB funding in 2024, how much
of the change in that funding between 2024 and 2025 was offset by changes in domestic, Global Fund and
other external funding, and how does the 2024–2025 change in domestic funding compare with (a) the same
countries' previous trend and (b) countries without USAID funding?

## 2. Data

- **Primary:** WHO Global TB Programme public expenditure and utilisation data, release of 25 August 2026
  (`TB_expenditure_utilisation_2026-08-25.csv`): funding received by source as reported by national
  programmes — `rcvd_tot_domestic`, `rcvd_tot_gf`, `rcvd_tot_usaid`, `rcvd_tot_grnt` (other grants) and
  `rcvd_tot`, current US dollars.
- **Forward-looking:** WHO's processed finance file for the 2026 report (GTB-TME/gtbreport2026, commit
  11ebd9b, fetched and digest-verified), which carries expected funding by source for 2026.
- **Provenance:** WHO's processed file labels each country-year's funding as reported, committed,
  carried from last year or imputed (`rcvd_imputation`). Only values labelled "Reported data" enter the
  primary analysis.

## 3. Population

Primary: countries with `rcvd_tot_usaid` > 0 in 2024 that report all four sources for both 2024 and 2025,
with the four sources summing to `rcvd_tot` within 1% in both years. Countries failing the identity are
listed and excluded, not repaired. Comparison group: countries reporting all four sources in both years
with `rcvd_tot_usaid` = 0 or missing in 2023, 2024 and 2025.

## 4. Measures

For each country, Δ = 2025 value − 2024 value, per source.

- **Offset ratio** = (Δdomestic + ΔGlobal Fund + Δother) / (−ΔUSAID), defined where ΔUSAID < 0.
- **Classification:** *fully offset* if Δtotal ≥ 0; *partly offset* if ΔUSAID < Δtotal < 0; *not offset*
  if Δtotal ≤ ΔUSAID (other sources also fell).
- **Domestic change beyond trend:** (domestic 2025 − domestic 2024) − (domestic 2024 − domestic 2023), in
  the same countries.
- **Difference in changes:** median proportional change in domestic funding 2024–2025, USAID countries
  versus comparison countries, with the same statistic for 2023–2024 as a placebo.
- **Expected 2026:** USAID and domestic funding expected for 2026, from WHO's processed file.

Aggregates are reported with and without India, which alone holds a large share of domestic funding.
Results are reported country by country in a table; the paper's headline numbers are sums and medians.

## 5. Sensitivity and robustness

1. Constant 2025 US dollars using WHO's deflated series, in place of current dollars.
2. Including country-years whose funding WHO labels other than "Reported data".
3. Excluding countries whose 2025 value is identical to their 2024 value for any source (possible
   restatement; the measure from the companion vintage analysis).

## 6. Seen before this plan was written

Totals of `rcvd_tot_usaid` by year in the public file (28 countries, US$ 215 million in 2023; 24, US$ 199
million in 2024; 21, US$ 154 million in 2025); in WHO's processed file, 27 countries with USAID funding in
2024 and aggregate domestic funding rising in those countries between 2024 and 2025, driven in part by
India, Indonesia and South Africa; 96.4% of 2025 funding labelled "Reported data". No country-level offset,
classification or comparison has been computed.

## 7. What the paper will not claim

That the US cuts caused any country's domestic change (the design is descriptive, with a trend and a
comparison group, not causal); anything about services or outcomes; anything about funding that does not
pass through national TB programmes (for example US funding to implementing partners off-budget).

## 8. Deviation log

**15 November 2026, after the primary analysis was run.** Twelve of the 24 countries with USAID funding
in 2024 failed the population rule. Seven of the twelve failed only because "other grants" was blank
in one year, a case the plan did not anticipate. WHO's form instructs countries to leave a field empty
only if its value is unknown, so a blank is not a zero. But where the other three sources sum to the
reported total within 1%, the total itself shows other grants were zero. A **post-hoc sensitivity
analysis** therefore admits countries whose only failure is a blank "other grants" confirmed zero in this
way. It is reported as post hoc and does not replace the primary population. Countries failing the
identity (Cameroon, Ethiopia, Uganda) or missing a whole year (Central African Republic, Micronesia,
Tajikistan's USAID value) stay excluded.

**Correction to the entry above (15 November 2026).** "Seven of the twelve failed only because 'other
grants' was blank" was miscounted. Five failed only for that reason (Kenya, Lesotho, the Philippines,
South Africa, Ukraine) and are the five admitted post hoc. Kyrgyzstan also has a blank "other grants",
but its 2025 total is printed as zero while its sources sum to US$ 18.0 million, so it fails the identity
and stays excluded. The check that caught this is verification/check_c.py.
