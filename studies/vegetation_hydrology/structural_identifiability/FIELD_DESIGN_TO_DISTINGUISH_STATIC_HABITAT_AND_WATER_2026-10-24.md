# External field-monitoring design to distinguish habitat, local water and site-history predictors
Date 2026-10-24. **Proposed new study, not executed.** No permission to claim independent replication or field confirmation. The existing JAE RC6 study remains frozen.

## What cannot identify the mechanism
Repeated chorus signals at the same sites with a fixed annual habitat map do not distinguish persistent mapped habitat effects `βE_i` and unrestricted persistent site latent state `U_i`. An across-route uniform rainfall/water increase can affect calling magnitude but cancels from **placement conditional on k**. Satellite monthly visibility varies by season and vegetation and is not site-specific event-night water depth. Adding other fixed habitat variables or repeatedly refitting old NAAMP acoustic data cannot solve this structural aliasing.

## Practical independent observation contract
- Choose new ten-site monitoring routes containing **both** emergent/woody wetland and exposed-water sites, balancing road proximity, canopy, route reachability and species pools before seeing call outcomes.
- Record actual water state **at every listening station at every monitored visit**: water present/absent (ground-verified even under vegetation), water depth in cm (with reference benchmark), estimated flooded fraction of the fixed local wetland footprint, hydroperiod/last-dry date where feasible, and vegetated cover within a declared 100m/500m spatial extent. Do not substitute nearby stream height or 30m exposed-water satellite pixels for microhabitat pond depth.
- Use temporally repeated independent rain and relatively dry opportunities within the **same breeding season** and at the same physical stations. Document source observations before or contemporaneously with sound recordings (no future climatic reconstruction as though causal).
- Acquire observer/recording detection controls: microphone calibration, detection distance/ambient noise, wind, visit timing/order, temperature, taxon identification and repeat detection; consider time-synchronised autonomous audio if simultaneity is a planned endpoint.
- Compute *environment-only* route×event water-change vectors and first pre-check **nonuniform site-specific changes**: `ΔW_i-mean_j ΔW_j` across ≥6 matched physical stations; do not promote route-wide shifts into evidence for location placement.
- Train/evaluate on whole routes and complete events withheld from the model, and include truly new routes and years for independent validation. Document missingness and field effort.
- Endpoint remains a fixed-k ten-stop conditional placement logscore, alongside a **separate** calling magnitude analysis; uniform global weather may explain magnitude without reorganising placement. Avoid inferring occupancy, successful breeding, site fidelity of individual frogs or frog movement from acoustic detections alone.

## Measurement necessity vs statistical power
The environment-only NAAMP JRC panel permits eligible same-season, same-site, adjacent-observed-year contrasts in 9,420 route-month-year comparisons but only 15.0% of route-balanced first eligible contrasts have ≥5 percentage-point site-relative water changes. This establishes a concrete reason to ensure rank support before any new analysis, **not** a power calculation for field sample size. A numerical sample size recommendation would require species-specific response variance, season, water measurement sensitivity, route clustering and an independently validated generative model, none of which is provided by the current source.

## Analysis gates
1. Pre-freeze source measurement protocols, quality thresholds, route/time blocks and missingness before looking at acoustic responses.
2. Demonstrate actual site×time water variation not absorbed by site and visit effects.
3. Use a detection-calibrated observation model; model deviations of local water from each station's own seasonal baseline, not just its spatial water class.
4. Reject unsupported mechanism claims even if an association is strong: temporal variation plus covariate overlap gives conditional association, not automatic causal identification.
