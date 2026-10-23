# Frozen-before-readback ecological macroanalysis: seasonal acoustic taxon complementarity across mapped wetland vegetation

**Date:** 2026-10-23. This follow-up is exploratory: the **same** USGS NAAMP 2001–2015 × USFWS NWI 250m dataset and original positive PEM alpha/gamma findings were already studied. This is not preregistration, independent biological validation, forecasting, new literature review or a vegetation experiment. The specification is fixed **before the new across-round taxon-pool union outcomes** are read.

## Central biological question

Do NWI emergent/PEM wetland mosaics support **more acoustically detectable frog taxon labels across multiple within-year survey rounds** because *different taxa are heard in different rounds*, or is the already known richer PEM pool simply larger on individual visits?

This directly distinguishes two levels of community organization:
- **Community size** on a single visit, already linked to PEM.
- **Within-year temporal complementarity** of taxon labels on exactly the same physical wetland sites, not equivalent to seasonal calling-index strength, temporal persistence of individual frogs or biological species interactions.

## Source, fixed geographic/effort comparison

Start with original 7,848 USGS NAAMP standardized ten-stop route-nights, validated original 5,147 USFWS NWI physical SiteIDs, 6,236 full 250m mapped NWI + temperature/sound complete nights, across 499 physical routes and 20 States. Use **exactly** the existing verified within-year source inclusion/physical SiteID-matching function `source()` + `build_rounds()` in `exploration/run_naamp_vegetation_withinyear_round_hierarchy_v0_1.py`, without changing its NWI categories, year range, taxonomy, seasons, duplicates or geography gate. Its source population was **2,869 matched nights in 1,115 route×calendar-year groups on 274 physical routes/20 States**, with 2–4 distinct rounds/group; fail closed if these counts change.

For each accepted physical route×year, within the same exact ordered ten SiteIDs:
- PEM stations: mapped NWI emergent-wetland fraction >0 within 250m;
- comparator stations: PEM fraction=0 **but mapped total wetland fraction>0**;
- at least 2 distinct stations in each vegetation group; **m=min(n_PEM,n_otherwetland)** fixed by GIS and route identity (m=2–5). The same m **physical sites** are uniformly rarefied for both temporal visits, never independently resampling different physical sites each visit.
- One route×year with R∈{2,3,4} distinct survey rounds gives all `C(R,2)` unordered **round-pair comparisons** (R2=1, R3=3, R4=6). Within-route×year average these contrasts so a route-year with 4 rounds does NOT count as 6 independent source units. Each physical route contributes the mean of its eligible route-year values, regardless of number of years. Spatial inferential unit = independently sampled **physical route**, not observed stops, round-pairs or frog taxon labels.
- Retain all original monitoring taxon names including taxon complexes and all acoustic zeros. CI≥1 is main calling-threshold and CI≥2 separately.
- Keep original source NWI overlay, site buffers and survey date; NWI polygons are **not contemporaneous botanical plant species**, and a zero map polygon fraction is not confirmed absence of plants.

## Exact matched-site temporal accumulation mathematics — no stochastic taxon-pool sampling

For a habitat group with n candidate exact physical stops and m uniform sites chosen *once for both selected survey rounds*, for frog acoustic taxon t define:
`k_early` = number of habitat sites where taxon t called in earlier round,
`k_late` similarly in later round,
`k_union` = number of sites where t was heard in either round at that *same physical site*.
The probability taxon t is absent from an m-site sample at phase x is `P0_x=comb(n−k_x,m)/comb(n,m)`, with comb(a,b)=0 if b>a. Exact expected taxon pool:
- `G_early=Σ_t (1−P0_early)`;
- `G_late=Σ_t (1−P0_late)`;
- `G_two=Σ_t (1−P0_union)`;
- `G_mean_single=(G_early+G_late)/2`;
- **within-year temporal bonus** `B=G_two−G_mean_single=(New_late+Old_only_early)/2`.
`New_late=Σ_t (P0_early−P0_union)`, `Old_only_early=Σ_t(P0_late−P0_union)`. These are *added acoustic taxon labels in a source observation round*, NOT ecological colonization/extinction, and follow exact algebra under uniform m sites. Every per-route-year source `B>=0`, `G_two>=G_early,G_late`, `B=(New_late+Old_only_early)/2` to numerical 1e−10; validate by brute-forcing **every physical-site subset** for a multi-round synthetic example.

## Four fixed, independently interpretable inferential endpoints

Each observational outcome is **PEM minus nonPEM wetland** within route×year, then physical-route means:
1. **PRIMARY:** CI≥1 `Δ_B = B_PEM − B_otherwetland` — does emergent vegetation correspond to *additional temporal complementarity* beyond a single-round pool?
2. Secondary: CI≥2 `Δ_B`.
3. Secondary: CI≥1 `Δ_Gtwo = G_two,PEM − G_two,other` — seasonally cumulative equally sampled taxon-pool size.
4. Secondary: CI≥2 `Δ_Gtwo`.

Report **also** `Δ_GmeanSingle` so `Δ_Gtwo=Δ_GmeanSingle+Δ_B` identity is checked for every group. A positive cumulative gamma by itself may be driven entirely by the existing positive single-round richness and does NOT demonstrate extra temporal complementarity.

- Inference: Student t(df=#physical routes−1) 95% CI and two-sided P, **4,999 whole-route Rademacher sign flips** for each of 4 fixed endpoints, and Benjamini–Hochberg across **all 4** tests. Also report equal-State vs equal-route mean, 20-State t interval, # positive State means, and leave-one-State-out effect sign/range. Require >=50 routes, >=5 States and >=150 eligible route-year groups for inference.
- Treat the primary `Δ_B` as exploratory supported only if route CI lower>0, four-test BH q<.05, physical-route signflip p<.05, and State CI lower>0. Label cumulative gamma (independent secondary claim within same source) supported only with the same gates, **without** implying dynamic interactions.
- No selecting only 1/2/3/4 round-specific contrasts or removing sites after observing outcomes to rescue significance. Pre-fixed secondary descriptive comparisons: normalized temporal bonus `B/G_two` for habitat pools with `G_two>0` (report proportion undefined), `New_late` and `Old_only_early` per habitat, and round-pair combination means `1–2,1–3,2–3,1–4,2–4,3–4` with route and year counts, **no extra P values**. Round 4 is already known to be sparse (195 visits /55 routes/6 States); descriptive caveat.
- Date/temperature, call detection probability and taxon species coding are not controlled experimentally; seasonal taxon bonus cannot be called ecological extinction, evolution, reproduction, or plant-caused facilitation.

## Reproducibility and stopping rule

New code `exploration/run_naamp_wetland_seasonal_complementarity_v0_1.py`, QA and source workflow `.github/workflows/naamp_wetland_seasonal_complementarity.yml`; create permanent aggregate JSON and ecological synthesis only after full real GitHub Actions validation. Do not overfit season/region/taxon after result. Keep original JAE RC6 manuscript/SI/main unchanged and do not commit third-party raw records.
