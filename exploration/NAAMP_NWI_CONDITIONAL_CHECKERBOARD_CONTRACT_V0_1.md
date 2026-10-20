# NAAMP aquatic vegetation-conditioned checkerboard — frozen exploratory contract v0.1
Date: 2026-10-21; user-directed separate project extension, **not** an amendment to frozen JAE RC6.

## Core question and prediction

Does allowing each frog taxon a transferable, different association with mapped emergent aquatic vegetation explain the **between-taxon** checkerboard excess over the fixed species-by-stop and stop-richness margins?

The previous species-specific NWI findings (five BH-positive conditional call-placement associations among 25 eligible taxa) motivate this test; they must **not** be treated as an independently confirmed mechanism. The same underlying NAAMP programme supplied these outcomes.

## Frozen population and response

- Source: existing SHA-pinned USGS NAAMP Runs/Stops/Counts, 2001–2015.
- Plant proxy: full response-blind NWI geospatial overlay (5,147 sites/501 routes) from completed Actions run 39450277196, only sites with successful NWI API query and acceptable original coordinate geometry.
- Primary: recorded calling (CallingIndex 1–3). Strong calling (CallingIndex 2–3) is a fixed secondary endpoint, not an outcome-chosen replacement.
- For each full ten-stop survey matrix use exactly the same eligibility as `exploration/run_naamp_checkerboard_fixedfixed_v0_1.py`: ≥3 calling taxa, ≥2 with detections at ≥2 stops, ≥3 calling-positive stops, at least one feasible fixed-margin row trade.
- For strict comparison, retain only the reference `primary_run_level.csv` or `strong_run_level.csv` runs from Actions 39436588431 that have **all ten NWI-mapped SiteIDs and complete stop temperature/noise conditions**, with the original same-run C-score exactly verified.
- Do not select runs or species based on the target checkerboard score.

## Models and falsification

Condition **exactly** on each run's observed row sums (taxon detected-stop counts) and column sums (recorded taxon richness per stop), so models address allocation not gross activation.

0. **Fixed-fixed exchangeable:** previous published exploratory run-level C-score null means computed with 399 Curveball draws, at the identical retained runs.
1. **Species-specific mapped-wetland availability:** independent route-fold conditional logistic taxon weights for total NWI wetland mapped area within 250m.
2. **Species-specific mapped-wetland + emergent wetland vegetation:** independent route-fold conditional logistic weights for both total NWI wetland area and `PEM` emergent-wetland mapped area within 250m.

For each of 0→1 and 1→2 report the change in predicted C-score and residual. A positive increment 1→2 means taxon-specific emergent-wetland associations help explain observed segregation; a zero/negative change does not.

### Fold-safe weights

- Route fold A/B deterministic SHA256 of `State:RouteNumber` (never use outcome data or observed C-score for the split).
- Learn each taxon's coefficients only from **opposite-fold** survey runs, conditional on the run's total positive stops `k` and its ten mapped site fractions, using exact fixed-k conditional logistic likelihood over all \(\binom{10}{k}\) possible location subsets.
- Include all taxon units with adequate training information; train on route-runs with \(1\le k\le9\), at least 30 informative run observations with mapped predictor variation across ≥12 routes; other taxa receive zero coefficients (with exact fallback counts recorded). Do not preselect five positive taxa or condition on their BH q-values.
- Ridge penalty \(3(\beta^2)/2\), fixed coefficients constrained between −3 and +3 per +10 percentage points in the mapped cover fraction. Cover variables are continuous \(10\times\) fractions, ensuring the same unit as previous taxon-wise model.
- For each fold, report held-out conditional location log-likelihood for the wetland-only and wetland+emergent models relative to uniform fixed-k placement, and their increment. **The training model conditions on row margins; test nulls additionally preserve column margins.**

### Fixed-margin simulation

- Weighted Curveball Metropolis–Hastings proposals swap the unique site sets of two randomly selected taxon rows. Uniform random partition of their unique sites is a symmetric proposal.
- Accept with \(\min\{1,\exp[\sum_{s,j}(x'_{sj}-x_{sj})(\beta_{s,w}W_j+\beta_{s,e}E_j)]\}\). Preserve **every** row and column sum exactly; otherwise fail the run.
- 199 weighted draws per test matrix, burn-in 40 × number of detected taxa and thinning 8 × number of taxa; fixed seed 2840267, deterministic run sort.
- Original fixed-fixed null 399-draw mean is reused for exactly matched runs; exact same observed C-score (numerical tolerance 1e−8) is required.
- Report pooled observed, baseline predicted, wetland-model predicted, plant-model predicted; baseline and adjusted mean residuals; conditional simulation upper-tail P, route-clustered 95% CIs for residuals and for plant incremental gain, and A/B folds separately.
- Track feasible proposals, accepted moves, per-run C-score simulation variation, low-mixing diagnostics; no positive finding if >20% of informative matrices have inadequate moves or simulation can't explore fixed margins. In that case mark interpretation `sampling_unreliable`, not significance.

### Interpretation and decision

- **Plant-specific explanation:** augmented vegetation model increases expected C-score relative to wetland-only (route-CI lower bound >0), produces a positive cross-fitted log-score increment, and reduces unexplained C-score excess. Full explanation additionally requires adjusted residual not outside null envelope and a route-clustered CI including zero. No retuning after result readback.
- **No supported contribution:** model increment includes zero or is negative.
- **Missing mechanism:** residual remains positively outside the tested null envelope after augmentation; plant preferences alone are insufficient under this generator.

All decisions are exploratory and cannot demonstrate that aquatic plants caused calls, competition, aquatic macrophyte species, historical plant occupancy, hydroperiod or active site choice. This analysis may be biologically informative but is **not** evidence for revising the current RC6 manuscript.
