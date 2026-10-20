# Frog chorus ecology × mapped aquatic vegetation — exploratory synthesis (2026-10-21)

## Current finding

**Species-specific use of recurrent strong-chorus sites persists after adjustment for mapped wetland vegetation and measured stop-night conditions.** NWI plant structure does not yet provide a sufficient explanation for recurrence. Between-taxon acoustic checkerboarding shows a *fragile, exploratory negative* association with among-stop emergent-vegetation heterogeneity, not evidence that plants cause species exclusion.

This is a new, user-directed study outside the frozen JAE RC6 submission. All biological findings below are exploratory on previously inspected NAAMP frog outcomes.

## Sources and sampling

- Frog outcome: USGS NAAMP pinned Runs/Stops/Counts, 2001–2015, 7,848 standardized route-runs, 4,236 wetter–drier pairs and 585 matched routes.
- Vegetation: current/available USFWS NWI polygon classification (`PEM` = emergent; `PAB/LAB/RAB` = aquatic bed; `PFO/PSS` = wooded/shrub wetlands; `PUB/LUB/RUB` = unconsolidated bottoms). These are **mapped habitat proxies**, not species or percent vegetation cover measured during 2001–2015.
- Frozen geometry gate: original source coordinate records 12,064, 15 excluded suspect/geocode-incomplete routes; no outcome-dependent geometry repair.
- Matched-route NWI attempt: **554 routes**, **501 successful**, **53 failures** (failed requests are *missing*, not absent vegetation).
- Matched NWI physical sites with contextual buffers: **5,147**; a 250-m NWI emergent polygon overlaps **1,286**; NWI aquatic-bed overlaps **66**; any NWI wetland polygon overlaps **4,743**.
- Full NWI source-only QA was completed before reading frog response outcomes in this study. Receipt in workflow 39450277196.

## Q1 — historical acoustic site use versus mapped aquatic plants

Within species × matched-survey pair (linear probability model, route-clustered uncertainty), same **10,166** site records, **1,017** species-pair groups, **241** routes:

| Predictor/effect | Estimate | 95% CI | P |
|---|---:|---|---:|
| Historical CI≥2 use, unadjusted within same sample | +0.152990 | +0.130122 to +0.175858 | < 0.001 |
| Historical CI≥2 use, adjusted | **+0.144416** | **+0.122226 to +0.166606** | < 0.001 |
| NWI emergent cover, 250 m | +0.050491 | −0.160611 to +0.261593 | 0.639 |
| NWI aquatic-bed cover, 250 m | +0.457111 | −0.162852 to +1.077074 | 0.148 |
| Prior-use × emergent-cover interaction | +0.003231 | −0.344863 to +0.351325 | 0.985 |

The adjusted model represents total mapped wetland, mapped emergent, aquatic-bed and woody wetland fractions within 250 m; stop air temperature, recorded sound masking, other taxa's strong calls, and position along the ten-stop route. The positive past-use coefficient remains after those controls; it does **not** establish individual memory or environmental independence because local water level, hydroperiod, substrate, vegetation at historic surveys and historical population size are unmeasured.

## Q2 — does vegetation heterogeneity explain between-species checkerboarding?

For **3,682** runs, **478** routes, **20** states, a post-hoc between-route model regressed the previously fixed-margin-corrected C-score residual on across-stop variance of 250-m NWI emergent cover. Covariates: mean NWI emergent, mapped aquatic-bed, total wetland, woody-variance cover; temperature, log rain recency, year, State and seasonal RunNumber. SE clustered at route level.

- Estimated coefficient for emergent heterogeneity = **−3.12236**, 95% CI **−5.79213 to −0.45259**, nominal P = **0.02189**.
- Mean fixed-fixed C-score excess in linked runs = **+0.05169**.
- An independent predetermined **11-of-12 NWI geography-shard** sensitivity produced **−2.71112**, 95% CI **−5.66242 to +0.24019**, P = **0.07179**.

Therefore the direction is negative in both samples, but statistical robustness is insufficient to promote a strong vegetation → checkerboard claim. The coefficient is per one unit of cover *variance*, not per 1% vegetation. A spatial-scale and State-block stability analysis has been started as an exploratory falsification and must be read before any stronger claim.

An acoustic checkerboard is not direct competition or occupancy-based exclusion. Static NWI wetland context is correlated with geography, hydrology, wetland size and land-use histories, so omitted site-quality and mapping-age differences remain explanations.

## Important inferential hierarchy

1. **Established in the new NAAMP analyses:** past species × SiteID strong-chorus records are informative beyond measured microtemperature, acoustic context and coarse mapped plant structure.
2. **Unresolved:** whether persistent site quality, transient local hydrology, vegetation at the **actual survey date**, social calling context or demographic availability generates the recurrence.
3. **Exploratory, not stable enough yet:** routes heterogeneous in NWI emergent cover may have *less*, rather than more, excess checkerboarding. The effect is sensitive to the geographic subset and should not be treated as confirmation.
4. **Not tested:** plant species identity, true aquatic macrophyte cover, plant–frog co-occurrence at the same microhabitat, plant facilitation versus plant-driven interspecific segregation.

## Provenance

- Full geospatial crosswalk and original linked ecological output: [GitHub Actions run 39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).
- Same-complete-case ecological analysis: [run 39453784896](https://github.com/zuizui0223/frogcs/actions/runs/39453784896).
- Original independently simulated checkerboard C-score run: 39436588431.
- 11-of-12 geographic restriction, same-sample historical-usage check: [run 39453442248](https://github.com/zuizui0223/frogcs/actions/runs/39453442248).
- Numeric results: `exploration/NAAMP_AQUATIC_VEGETATION_FULL_RESULT_V0_2.json` (and original runner artifact).
- RC6 frozen JAE submission documents and paper are unchanged.

## Next scientific discriminator

A replicated **same-site, time-matched** survey measuring percent emergent/submerged/floating macrophyte cover together with water depth, water temperature, hydroperiod, fish presence, and exact night-specific calling is needed to distinguish habitat filtering from behavioural reuse independent of local hydrology. This is a new research programme, not a requirement for submission of RC6.
