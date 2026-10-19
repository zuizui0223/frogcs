# State × history × terrestrial landscape — source-gated macroecology

**Separate exploratory branch.** The JAE initial-submission scientific bundle on `main` is unchanged. No C1V2 forest effect or independent confirmation has been established.

## Current factual position (15 Oct 2026)

- **NAAMP matched pairs:** original paper populations reproduced from pinned survey metadata without reading frog `Counts.csv`: 4,236 overall; 2,916 with strictly prior physical-site history (439 routes, 20 states).
- **Coordinate gate:** 1,028 of 1,183 coordinate source routes have ten unambiguous physical SiteIDs with no gross geometry errors.
- **Intersection:** 2,422 of 2,916 paper pairs and 358 of 439 paper routes remain after the ten-coordinate source gate (all 20 states). **Sampling is geographically uneven:** pair retention is just 1/26 (3.8%) in Kentucky, 124/233 (53.2%) in Indiana and 77/120 (64.2%) in Iowa versus 147/148 (99.3%) in South Carolina. This is **not actual 300-m positional accuracy or forest raster completeness**.
- **C1V2 original pixels:** not acquired. Official land cover and confidence C1V2 catalog entries exist, but direct ScienceBase ZIP Range returns HTML; MRLC WMS capabilities alone are not raw categorical TIFF proof.
- **Forest-patch algorithm:** written and tested on synthetic 30-m class + confidence arrays only. Connects two listening stops only if the same 8-neighbour forest component (codes 41/42/43) touches both 300-m buffers inside a fixed route hull+1,000 m window.
- **Soil × history:** September 30 NAAMP post-hoc analyses support separate main associations but do not support the primary interaction between route-scale soil water and recurrent-site placement. See frozen audit.
- **Focal higher-order conditional residual survives source-complete selection:** exactly-ten original survey SiteIDs match all 10 coordinates for **2,422/2,422** focal pairs and 358 routes. On the archived original species+prior-SiteID+dry-persistence B=1000 null, observed β=**1.7184**, expected β=**1.4478**, conditional residual **+0.2706** versus null 95% interval **[-0.1449,+0.1396]**, Monte Carlo p=**0.000999**. Original 2,916-pair full result residual=+0.2969. **This is reused-NAAMP geographical sensitivity, not independent replication or a forest predictor.**

## 19 October: lagged soil wetting vs present water — negative mechanism test

[**Full empirical hydrologic trajectory result**](NAAMP_SOIL_WETTING_TRAJECTORY_EMPIRICAL_RESULT_2026-10-19.md) asks whether **the rise in soil moisture in the preceding seven days or 24 hours**, rather than present moisture, explains new strong CallingIndex≥2 species×site acoustic activation. Precommitted 24/168h windows were newly extracted for **7,559 original source-pinned NAAMP runs**, then reused the **same 4,045 physically stable pairs / 563 routes** in an identical adjusted route-FE test. Seven-day rise β/**0.01 m³/m³**=**+0.000846** [−0.03394,+0.03563], Holm P=.96199; 24h rise β=−0.03903 [−0.14463,+0.06658], Holm P=.93777; the original positive **current hydric level** coefficient +0.09907 was reproduced. The 2008→2009–2015 temporal transfer added virtually no seven-day predictive improvement (route-equal MSE reduction +0.00202 [−0.06415,+0.05821]). The 24-hour secondary model improved more in previously unseen routes only, but the **overall** interval includes zero and no between-group difference was established; do not rescue the failed main trajectory hypothesis by cherry picking. This constrains a **fast-wetting-as-cue** explanation in these data but does NOT show soil-water persistence causally causes breeding. Independent explicit-route dummy regression reproduced all primary slope estimates and SEs. [Actual successful workflow 39208626998](https://github.com/zuizui0223/frogcs/actions/runs/39208626998), [full 7,559-run historical soil and 4,108-pair archive](https://github.com/zuizui0223/frogcs/actions/runs/39208626998/artifacts/12166263352). Frozen JAE main unchanged.

## 19 October: reproduction-mode falsification of the soil correlation

[**What soil water does — and does not — reveal about frog reproduction**](NAAMP_BREEDING_MODE_FOSSORIAL_SOIL_RESULT_2026-10-19.md): pinned original NAAMP species-list check confirms adult burrowers usually lay aquatic eggs, while the single specifically identified terrestrial-egg direct developer has **0** CI≥2 source records. Five named adult-burrowing aquatic breeders have **84** CI≥2 source records across the full eligible source; a precommitted spadefoot-specific power gate **failed** (83 records vs 200 minimum). In the identical **4,045-pair, 563-route** ERA5 sample, removing these six named taxa leaves the within-route soil coefficient essentially unchanged: **+0.09907 → +0.09716 per 0.01 m³/m³** for new strong taxon×site calling (latter CI **[+0.06371,+0.13060]**). The named taxa account for just **76/13,347** new strong events. [Source trait audit](https://github.com/zuizui0223/frogcs/actions/runs/39201606641), [post hoc direct developer source check](https://github.com/zuizui0223/frogcs/actions/runs/39201940702), [same-model acoustic leaveout QA SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/39202528021). **Not a test of eggs, successful breeding, soil-mediated causal effects, or all fossorial species.** No JAE main change.

## New source-quality robustness result

[**Complete original-null evidence audit**](NAAMP_GEOGRAPHY_GATE_HIGHER_ORDER_NULL_RESULT_2026-10-15.md) — complete empirical subgroup regressions, SHA-pinned survey↔coordinate exact SiteID matching, and original unchanged species×SiteID crossfit null on 2,422 pairs. [Successful conditional-null Actions run](https://github.com/zuizui0223/frogcs/actions/runs/38726385727); [source-only geometry matching run](https://github.com/zuizui0223/frogcs/actions/runs/38725438609). No C1.2 GeoTIFF accessed. The [Delaware 210302 source-only GeoJSON](aoi/NAAMP_Delaware_210302_source_only_C1V2_request.geojson) and [StopNumber↔SiteID table artifact](https://github.com/zuizui0223/frogcs/actions/runs/38724734319/artifacts/11967790799) are ready for a human-initiated official MRLC Viewer data request (email required).

## Reproducible sources and scripts

| Purpose | File | Status |
|---|---|---|
| September 30 hydric / memory results with negative interactions | [Evidence audit](STATE_HISTORY_HYDRIC_EVIDENCE_AUDIT_2026-10-14.md) | Archived, post-hoc |
| Biological hypotheses, exact-k logic, source/validation gates | [Study plan](STATE_HISTORY_LANDSCAPE_TEST_PLAN_V0_1.md) | Methods only |
| Real strict-ten-site coordinate-only source pilot | [Geometry results](NAAMP_TERRESTRIAL_GEOMETRY_PREFLIGHT_RESULT_2026-10-14.md) | Verified |
| Paper cohort / C1V2 access audit and blockers | [Source gate](NAAMP_TERRESTRIAL_C1V2_EVIDENCE_GATE_2026-10-15.md) | Verified or explicitly unresolved |
| NAAMP focal paper inclusion recreated from original Runs/Stops only | [Metadata join code](scripts/naamp_focal_metadata_geometry_join_v0_1.py) | Successful for 2,422/358 on source-only gate |
| USGS original C1V2 source/ZIP/WMS bounded probe | [Official source probe](scripts/official_nlcd_c1v2_access_gate_v0_1.py) | Original TIFF **not obtained** |
| Raster forest-patch component and site-pair extraction | [Forest feature extractor](scripts/nlcd_c1v2_forest_patch_features_v0_1.py) | Synthetic QA only |
| Fixed-k conditional site allocation likelihood | [Exact-k kernel](scripts/exact_k_placement_kernel_v0_1.py) | Synthetic QA only |

## 15 October method and source audit

- [**WCS2, Collection 1.2 and concentration handoff**](NAAMP_TERRESTRIAL_WCS_AND_CONCENTRATION_AUDIT_2026-10-15.md): official WCS2 has 1985–2025, 30m data in EPSG:5070, but bounded 2012 GetCoverage returns an XML server exception rather than a GeoTIFF. The original C1V2 pixel identity remains unverified.
- [**Exact-(K,N) whole-matrix concentration generator**](scripts/conditional_kn_concentration_kernel_v0_1.py) replaces the erroneous suggestion that per-species exact-k site placement can explain the algebraically fixed within-taxon C. **Ten synthetic tests PASS**, including the generic-vs-forest-pair non-identifiability check.
- [**Official MRLC Viewer AOI prepared — download GeoJSON + manifest**](NAAMP_FIRST_OFFICIAL_NLCD_VIEWER_AOI_2026-10-15.md): verified outcome-blind first eligible route **Delaware:210302**, 10 physical SiteIDs, 12 focal survey pairs, fixed hull+1km AOI **127.4488 km²**, [actual Actions artifact](https://github.com/zuizui0223/frogcs/actions/runs/38718741980/artifacts/11964571575). This is source export readiness only; no Collection 1.2 TIFF acquired and no frog effect.
- Comparison standard: **forest-linked same-taxon pairing must improve on generic same-taxon pairing**, using an independently validated forest-patch raster, a precommitted fixed-q baseline and geographically held-out events.

## Evidence links

- [Original no-outcome geography screen](https://github.com/zuizui0223/frogcs/actions/runs/38563109769) — 1,028/1,183 exact-ten coordinate routes.
- [Frozen-paper metadata × coordinate join and state retention](https://github.com/zuizui0223/frogcs/actions/runs/38704933550) — 2,422 pairs / 358 routes; all 20 States, unequal completeness.
- [USGS 2012 C1V2 archive/WMS source preflight](https://github.com/zuizui0223/frogcs/actions/runs/38703861726) — no original C1V2 numeric pixels.
- [Exact-k synthetic QA](https://github.com/zuizui0223/frogcs/actions/runs/38563866657) — eight mathematical tests.
- [30-m forest component synthetic QA](https://github.com/zuizui0223/frogcs/actions/runs/38704389950) — eight tests.

## Hard stop before ecological claims

1. An original **matching Collection 1.2** categorical landcover raster and confidence raster, acquired and source-provenance checked, must exist for a predetermined coordinate-eligible route.
2. Historical physical-site continuity and categorical/confidence completeness must pass before interpreting canopy as true local habitat.
3. Acoustic support and frozen `q` baseline must correspond to exactly the same CallingIndex threshold.
4. Results remain exploratory in NAAMP. Positive forest effects, if found, would be associations; independent repeated fixed-site data are required for evidence upgrading.
5. Never change the frozen JAE submission, retune forest/soil/guild cutoffs after readback, or count this documentation as a new frog effect.
