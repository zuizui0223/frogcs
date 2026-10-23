# Macro follow-up: cross-route prediction of acoustic community turnover by continuous NWI wetland difference

**2026-10-23 — Post-readback follow-up.** Previous *first* boundary study has now returned a real **non-support result**: CI≥1 143,615 same-night stop pairs, 3,430 runs and 285 routes; equal-route within-run fixed-effect PEM boundary Δ Sørensen **+0.087pp**, route CI −0.380 to +0.554pp, P=.714; route signflip P=.722. CI≥2 similarly null. The claim stays fixed; do not erase, retune or misrepresent this result. This is a **new exploratory predictive ecological question chosen after observing that null**, not an independent prospective hypothesis. RC6 main, SI and submission untouched.

## Question

Does continuous difference in 250m **mapped total wetland-cover fraction** between listening stations provide transferable information about how dissimilar their frog acoustic communities are, beyond a same-night stop-distance, temperature, sound and species-richness baseline? Is a simple binary NWI PEM overlap boundary similarly predictive, or is its addition redundant after total wetland difference?

Data held fixed to prior workflow `exploration/run_naamp_macro_pem_boundary_turnover_v0_1.py` source cohort: 7,848 standardized NAAMP nights, 6,236 NWI complete, 3,717 environmental boundary-opportunity runs (2–8 mapped NWI PEM positive sites). For observed Sørensen, CI≥1 nights with ≥2 total taxa, exclude only pairs with both stops silent. Primary 3,430 nights/285 routes/143,615 pairs. Same community definition and full 45 potential pairs per run; no NWI radius, season, species or significance tuning. CI≥2 is a separate descriptive secondary.

### Exactly four fixed prediction models

Outcome `Y` = Sørensen dissimilarity (0..1) between two 10-stop positions **on the same survey route-night**. All predictors *and outcome* demeaned within the heldout and training route-night (a **conditional** composition prediction, not a future-night forecast).

- **M0:** 8 dummies for route-stop separation 2..9, absolute differences in stop air temperature and acoustic masking index, absolute difference in stop-level detected richness, mean of the two richness values. These same-night covariates include the observed survey's frog richness — thus no causal or advance forecast inference.
- **M_PEM:** M0 + binary mapped `(PEM_i>0) XOR (PEM_j>0)`.
- **M_WET:** M0 + `abs(wetland_cover_fraction_i−wetland_cover_fraction_j)`; continuous habitat mosaic.
- **M_BOTH:** M0 + both PEM-boundary and wetland-cover difference.

**No outcome-learned variable selection.** All slopes standardized using only training fold means and SD of *within-run demeaned predictors*, without fitting on evaluation fold (the within-run centering of the evaluation Y is part of the conditioning definition, not out-of-sample prediction).

### Route holdout, estimand and tests

Deterministic hash split by entire *physical route* into geographic A/B, not by run, station or individual frog. Train on A evaluate B, reverse. Route equal-weight training WLS, no regularization or parameter tuning. Evaluate heldout **mean square error per route**, averaged equally over heldout routes. Report improvement `MSE(M0)−MSE(M_model)` in units of squared Sørensen dissimilarity, and `100×gain/MSE(M0)` in percent baseline MSE. Positive = cross-route predictive gain; negative = the added landscape feature makes predictions worse. Keep all four models on exactly matched heldout route-night pairs. Report 95% t(df=G−1) intervals over route-level paired improvements (one primary and three secondary contrasts), sign consistency by route fold and 4,999 route sign flips of paired score as an exploratory noncausal alternative. Do **not** interpret loss change as an intervention effect on frog communities.

**Primary:** M_WET minus M0 in all-call CI≥1, positive route-level 95% CI and fold A/B positive required to call *exploratory transferable continuous wetland signal*. Secondary M_PEM−M0, M_BOTH−M_WET, M_BOTH−M_PEM, and analogous strong-call CI≥2, all reported regardless of result. Do not promote extra comparisons based on selected P. Give N total independent routes, matched nights/pairs, and run/route inclusion source checks.

### Interpretation boundary

NWI wetland categories/cover are **current/static map proxies**, not contemporary 2001–2015 plant surveys, and physical stop geometry, substrate, hydroperiod, oxygen, fish, insects, species histories and detection biases remain unmeasured. A positive result means *predictive habitat heterogeneity*, not vegetation-caused niche differences, biological competition, or >3 taxon interactions; a null is an informative macroecological scope boundary.

Code will be `exploration/run_naamp_macro_pem_wetland_transfer_v0_1.py`, automation `.github/workflows/naamp_macro_pem_wetland_transfer.yml`; numerical result retained as GitHub Actions artifact and branch synthesis only.
