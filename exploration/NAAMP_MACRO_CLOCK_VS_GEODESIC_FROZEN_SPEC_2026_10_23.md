# Frozen follow-up protocol — NAAMP all-taxon acoustic turnover, physical separation versus **actual recorded stop time**

**2026-10-23, created after observing a positive real-geographic-distance association from the previous study.** This is a post-hoc robustness test, *not* a pre-registered independent discovery. No literature review; uses only pinned original NAAMP + validated NWI sources.

## Biological question
Does higher frog community Sorensen dissimilarity between physically distant wetlands persist after controlling for **actual recorded minutes separating the two visits on the same standardized 10-stop route-night**, beyond stop-index separation, wetland context and recorded richness?

## Valid source and clock rules fixed before this analysis
- Use same 7,848 standardized NAAMP runs / 6,236 10-stop NWI-complete environmental runs; NWI coordinate artifact source run 39450277196.
- Observed fields in original `Stops.csv`: `RunID`, `StopNumber`, `StartTime`, `TimeOut`. `StartTime` contains `HH:MM`; `TimeOut` is **binary (0/1)**, **not** minutes elapsed and cannot serve as clock. Original clock schema-only QA: 78,480 rows, ~83.66% contain a colon; literal string `NULL` is **missing**, not midnight.
- Parse only `^([01]?\\d|2[0-3]):[0-5]\\d$` with leading/trailing whitespace trimmed. A pair of visits at stop j>i has elapsed `(start_j-start_i) modulo 1440` minutes, allowing midnight crossover. Reject negative out-of-order readings that would generate implausible modulo gaps, and exclude pairs with elapsed time **>360 min**. If one clock missing, omit the pair **without imputing** or tuning time windows.
- Never modify the acoustic taxon calls used in previous route-night model. Primary any-call 1–3, secondary strong 2–3. Both sites must have ≥1 calling taxon. Preserve the original ≥2 mapped PEM / ≥2 mapped non-PEM station gate and ≥10 valid station pairs, ≥2 cross and ≥2 same per run.
- Use original verified `State,RouteNumber,SiteID` 250m NWI site coordinates and corresponding physical SiteID per specific `RunID,StopNumber`.

## Primary estimand
Within-survey-run demean station-pair Sørensen dissimilarity and seven frozen predictors:
1. difference in mapped NWI PEM overlap (binary);
2. absolute ordinal stop gap/9;
3. absolute total NWI wetland cover difference ×10 (prior standardization);
4. absolute detected-taxon richness difference;
5. mean detected-taxon richness;
6. `log(1+physical_geodesic_km)` from verified coordinates;
7. **`log(1+actual_elapsed_minutes)`**, based on recorded stop start clock (NOT the flag TimeOut).

Full model cluster sandwich SE and t(df=routes−1). Physical distance estimate is primary; duration estimate is conditional association only. Compare against **six-predictor geodesic model refitted on exactly the SAME clock-complete matched station-pair population** — never compare across different populations as a mechanistic difference.

Frozen contrasts: physical distance 1→10 km `beta_km×(ln(11)−ln(2))`; elapsed time 10→60 min `beta_time×(ln(61)−ln(11))`. No new cutpoints for selecting subsamples.

## Robustness and decision criteria
- Two deterministic geographic route folds A/B; geographic whole-State leave-one-out for the positive effect (>=80% sign stability), strict richness-matched |rich_i−rich_j|<=1, route-equal weighting (same clock coverage). Require main >=100 independent routes and at least 20,000 paired observations or classify `time_coverage_underpowered`.
- If full model physical-distance 95% route-cluster CI excludes zero positively, both folds positive, >=80% LOSO positive and richness-matched positive, label `exploratory_distance_after_clock_supported`. Otherwise `nonconfirmatory`. **All of this remains observational** and cannot infer dispersal, vegetation-induced biological interactions or point-process synchrony.
- Report Pearson correlation between clock and geo predictors and ordinal stop gap, so residual confounding/collinearity is visible. Do not use nominal P from one model to assert absence from another without appropriate direct contrast.
- Some states/years lack clock fields; preserve geographic coverage and absence denominators, do not fill missing times or allow time-availability selection to alter the frozen biological treatment definitions.
- Complete original JAE RC6 paper, SI and main remain untouched.
