# 独立NPSの水域持続性 × 同種コーラス利用履歴：層別比較 v0.1

2026-10-25. New **post-main-result exploratory sensitivity** specified before seeing the per-hydroperiod new estimates. Research branch only; original JAE RC6 locked main and WFTS stop unchanged.

## Focal test

Does the positive within-taxon, past physical-site strong-chorus → subsequent-year strong-chorus relationship reported in independent NPS 2016–23 records hold in ephemeral, semi-permanent and permanent wetland **Hydroperiod** groups, after effort and park×taxon×year fixed effects? Do apparent class-specific relations provide evidence that *hydroperiod class* fully replaces the historical-site term?

**NPS Hydroperiod is NOT NWI PEM**. Its three 2016–23 observational categories are broad field monitoring labels ("Ephemeral","Semi-permanent","Permanent") with 66 physical SiteLocations across seven parks. No station coordinates or USFWS NWI PEM1A/C/F polygon code are provided in the public source's 54-column species×recorder CSV. These classes are neither dynamic annual water level nor same as NWI's emergent vegetation and hydrologic modifier. Never label such analysis a PEM1A vs PEM1C vs PEM1F *observed* result.

## Fixed design before opening these outcome comparisons

- Same SHA256-verified NPS complete original 147,913 species×recording rows (2016–23), dataset DOI [10.57830/2320505](https://doi.org/10.57830/2320505); source decoder `research/scripts/nps_glkn_strict_history.py` and original main already-reported strict history panel and maximum CIV≥2 threshold.
- Use **all 1,815 previously published informative park×species×year ×site sample rows**; retain 195 strata, species/year/park identifiers, common 2017–23 past-only own strong history. Do **not** retune sample based on outcomes.
- Present source hydroperiod × prior-strong contingency table of eligible acoustic cells and strong-current counts, with caveat this is **not independent pond abundance**.
- **Main** fit a park×species×year fixed-effect linear probability model `current strong ~ prior strong + hydroperiod + prior strong×hydroperiod + log1p(current recordings) + log1p(prior recordings) + prior years observed + other-species strictly prior station chorus fraction`. Use `Ephemeral` reference category. Remove unidentifiable nuisance columns by rank, but require all three a-priori interaction contrasts identifiable or report class-specific non-estimability without changing the sign definition.
- Primary estimands: prior strong historical association in each of the three categories (sums of baseline and interaction coefficients), and contrasts `Semi−Ephemeral`, `Permanent−Ephemeral` plus uncertainty; uncertainty use **2,000 cluster bootstrap draws of entire park×species trajectories**, not each annual row. Report effective successful bootstrap count, fixed design rank, source sample and class-specific independent station counts.
- Secondary **within-hydroperiod matched** same park×species×year contrasts requiring ≥3 sites per combination and prior strong variation. If one stratum is sparse, declare sample-limited; do not inflate significant conclusions.
- Alternate annual maximum CI≥1 and CI3 are separate sensitivity outcomes, not main confirmatory tests.
- Explicit source and result provenance, no NAAMP refit, no NWI polygons, no causal claim due to stable site-specific habitat and detection heterogeneity.

## Predictions that would discriminate the mechanisms

1. **Hydroperiod alone proxies persistent site suitability**: past-site term should meaningfully attenuate when site hydroperiod interaction is added *out of sample*; a positive class interaction alone does not establish a causal hydroperiod mechanism.
2. **Taxon-specific historical acoustic template within broad hydroperiod**: own history remains positive *within at least two distinct hydroperiod classes* after same-stratum comparison; this weakens the claim that the three broad NPS water duration labels alone fully explain the history effect, but **does not** exclude fine local water level/PEM vegetation/individual social context.
3. **Environment-specific age/stage interaction**: classes may have different persistence of aquatic salamander/odonate larval predators, but no NPS predator-stage counts exist. This latter process is **not estimable here**.
4. **PEM1A/C/F × predator-stage network** requires verified NWI polygons plus exact audio site coordinates and independently observed wet-dry/vegetation state; 66 SiteLocation strings alone cannot be geocoded uniquely without a NPS authoritative station GIS or field registry. Official NWI polygons are publicly available ([NWI services](https://www.fws.gov/program/national-wetlands-inventory/web-mapping-services)), but never force a generic park point join.

## Ongoing theoretical model interpretation

Existing script `simulate_pem_three_guild_stage_balance.py` uses deliberately hypothetical PEM flooding windows and narrow-cohort advantage, and labels apparent three-guild persistence rather than mathematical mutual invasibility. Its success **does not** corroborate frog synchrony selection or any real NWI PEM class effect. A next independent phase-constraint/null must hold all other parameters fixed, vary only relative phases and direct risk-cue strengths, and compare what happens when predator pressure overtakes the indirect benefit. The sign and coexistence outcome cannot be stipulated in advance.
