# Locked exploratory macroecology: emergent × woody wetland structural mosaic and frog community richness

**Created 2026-10-23 before the new PEM×woody cross-product outcome is computed.** This hypothesis was motivated *after* observing positive NAAMP 2001–2015 × USFWS NWI 250-m PEM richness/gamma contrasts; it is deliberately **post-hoc**, not preregistration nor independent new sampling. **No literature review and no predictive scoring.** Main / JAE RC6 manuscript and SI remain frozen.

## Ecological question

Does mapped **emergent wetland (PEM) overlap × woody/shrub wetland overlap** correspond to a non-additive increase or decrease in how many frog taxon units are heard at the same 10-stop monitoring route-night, compared with the two mapped habitat signals acting additively? Is any nonadditivity due to more sites with frog calls or to more taxon units calling at already active sites?

This is an **interaction of overlapping remote-mapped environmental categories**; not a randomized plant×plant competition/facilitation experiment and certainly not a causal multi-frog-species interaction. The mapped 250-m NWI "vegetation" attributes are **not contemporary botanical species, ground-measured macrophyte abundance or source-year habitat structure**.

## Source and denominator frozen

- Original NAAMP 7,848 standardized route-run nights; source/NWI complete **6,236 ten-stop nights = 62,360 site-by-night observations**, from 499 physical routes /20 US States, using original geometry-vetted USFWS NWI 12-shard 5,147-site response-blind crosswalk, Actions #39450277196. Original direct acoustic taxa labels including explicit complexes.
- **Condition to stations inside the NWI mapped total wetland 250-m polygon footprint** (total wetland fraction>0) to rule out the simple mapped wetland-vs-nonwetland distinction. A 10-stop run with fewer than 2 such mapped-wetland stations has no within-night design information; exclude by geography-only rule and report. **Retain silent frog stops** and all survey nights otherwise; no outcome-based run filtering. NWI "absent" class means no polygon match, not measured plant absence.
- Binary P = NWI PEM-emergent overlap>0; W = NWI woody/shrub overlap>0. Four classes P0W0, P1W0, P0W1, P1W1 are **not four exclusive species communities**; they label which NWI polygons intersect the **same 250-m station buffer**. Some buffers contain both mapped classes. Report raw observations, independent SiteIDs, physical routes and geographic States in each cell before testing.
- Two outcome thresholds: CI≥1 any call **primary**, CI≥2 strong call **secondary**. Outcome = number of distinct detected NAAMP taxon units per site, not abundance/occupancy/survival.

## Primary: two-vegetation-type non-additivity within the same monitoring night

At each wetland-mapped station, use the fixed 16-column, within-run (exact fixed-effects demeaned) linear count-mean regression:
Y = β_P P + β_W W + **β_PW (P×W)** + β_A aquatic-bed map overlap indicator
  + β_T 10×total NWI wetland area fraction
  + β_temp local stop air temperature + β_noise local acoustic masking
  + 9 dummies for standardized stop positions 2..10 (stop 1 reference)
  + route-run-night intercept.

**β_PW** is the simultaneous, adjusted difference-in-difference:
[PEM change at woody present]−[PEM change at woody absent], in detected taxon units/stop; it is *not* biological synergy without causally manipulated plants.

Give each **physical route equal total weight**, not each repeated stop/night. Calculate cluster-sandwich SE with correction G/(G−1)×(N−1)/(N−16), route Student-t(df=G−1) 95% interval and P. For same model separately cluster by **20 US States**, with 19-df t interval. Also leave one entire State out at a time and report sign and effect ranges without tuning.

Treat the pair (CI≥1, CI≥2) as the **only two primary PEM×woody tests**, BH correction over both. Report P+W main coefficients and PEM effects conditional on W=0 and W=1, including the correct covariance matrix for confidence intervals (route clustered). Rank deficiency, fewer than 30 physical routes with all four cells combined, or missing source geography fail closed rather than fabricate a biological nonadditivity effect.

## Biological mechanism-free partition of the detected richness response

Define for each CI threshold the identity (for every site):
**number of calling taxon units = 1{≥1 calling taxon} + max(number of calling taxon units−1,0)**.

Fit **all three outcomes with identical samples, fixed effects, predictors and route weights**:
- number of calling taxon units Y (primary),
- calling site activation indicator I (descriptive),
- number of additional taxon units beyond the first E (descriptive).
Verify numerical coefficient identity **β_PW,Y = β_PW,I + β_PW,E** to ≤1e−9. This separates a non-additive change in likelihood that any frog was heard from a non-additive change in the number of *other* taxa heard, with no assumption of direct frog–frog behavior.

Do not conduct extra post-hoc significance claims for the activation/extras components; report them as exact accounting and disclose the sampling/observation limits.

## Strict within-night all-four-habitat comparison

Separately, for nights with **at least one wetland-mapped stop in each** P0W0, P1W0, P0W1, P1W1 cell, calculate the raw 2×2 contrast (mean species counts within each class). Average first over nights within each physical route and report equal-route mean, 95% route-t interval, directional State sensitivity, and coverage. This descriptive strict complete-cell contrast checks whether identification relies on extrapolating across different nights with differing incomplete habitat combinations. **No covariate adjustment**, so its coefficient need not equal the 16-column estimate. If fewer than 30 routes / five States or 50 complete nights, label "insufficient coverage." No new threshold or buffer-radius selection.

## Decision & inference boundary

A statistically supported adjusted β_PW after two-endpoint BH plus geographically consistent direction would be an **exploratory environmental architecture interaction** (nonadditivity across mapped P and W descriptors), **not** proof of causal plant structural complementarity, enhanced breeding, social calling, direct frog competition, predator interactions or third-order species interactions.

If β_PW is 0 or fragile, report that wetland architecture is **approximately additive on this count scale**, despite positive original PEM main-effect richness and exact rarefied gamma; do not chase geography/season/prefix or NWI radii after readback.

Prior verified positive macro results are **unchanged**: within-wetland equal-effort PEM gamma +0.29837 taxon units (CI≥1; 281 routes), route-balance positive contributions dispersed across 39/48 source taxon labels, 59% nestedness-resultant share of PEM-vs-nonPEM pooled Sørensen, and strong State→route→stop covariance hierarchy. These do NOT pre-authorize an interaction claim. Raw source NAAMP and USFWS data never committed. Publish only aggregate numeric JSON, code and ecological synthesis to this isolated branch.
