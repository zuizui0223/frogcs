# State × history × terrestrial landscape — source-gated macroecology

**Separate exploratory branch.** The JAE initial-submission scientific bundle on `main` is unchanged. No C1V2 forest effect or independent confirmation has been established.

## Current factual position (15 Oct 2026)

- **NAAMP matched pairs:** original paper populations reproduced from pinned survey metadata without reading frog `Counts.csv`: 4,236 overall; 2,916 with strictly prior physical-site history (439 routes, 20 states).
- **Coordinate gate:** 1,028 of 1,183 coordinate source routes have ten unambiguous physical SiteIDs with no gross geometry errors.
- **Intersection:** 2,422 of 2,916 paper pairs and 358 of 439 paper routes remain after the ten-coordinate source gate (all 20 states). This is **not actual 300-m positional accuracy or forest raster completeness**.
- **C1V2 original pixels:** not acquired. Official land cover and confidence C1V2 catalog entries exist, but direct ScienceBase ZIP Range returns HTML; MRLC WMS capabilities alone are not raw categorical TIFF proof.
- **Forest-patch algorithm:** written and tested on synthetic 30-m class + confidence arrays only. Connects two listening stops only if the same 8-neighbour forest component (codes 41/42/43) touches both 300-m buffers inside a fixed route hull+1,000 m window.
- **Soil × history:** September 30 NAAMP post-hoc analyses support separate main associations but do not support the primary interaction between route-scale soil water and recurrent-site placement. See frozen audit.
- **Original focal conditional residual:** has not been explained by a forest or terrestrial-connectivity model.

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

## Evidence links

- [Original no-outcome geography screen](https://github.com/zuizui0223/frogcs/actions/runs/38563109769) — 1,028/1,183 exact-ten coordinate routes.
- [Frozen-paper metadata × coordinate join](https://github.com/zuizui0223/frogcs/actions/runs/38703262483) — 2,422 pairs / 358 routes.
- [USGS 2012 C1V2 archive/WMS source preflight](https://github.com/zuizui0223/frogcs/actions/runs/38703861726) — no original C1V2 numeric pixels.
- [Exact-k synthetic QA](https://github.com/zuizui0223/frogcs/actions/runs/38563866657) — eight mathematical tests.
- [30-m forest component synthetic QA](https://github.com/zuizui0223/frogcs/actions/runs/38704389950) — eight tests.

## Hard stop before ecological claims

1. An original **matching Collection 1.2** categorical landcover raster and confidence raster, acquired and source-provenance checked, must exist for a predetermined coordinate-eligible route.
2. Historical physical-site continuity and categorical/confidence completeness must pass before interpreting canopy as true local habitat.
3. Acoustic support and frozen `q` baseline must correspond to exactly the same CallingIndex threshold.
4. Results remain exploratory in NAAMP. Positive forest effects, if found, would be associations; independent repeated fixed-site data are required for evidence upgrading.
5. Never change the frozen JAE submission, retune forest/soil/guild cutoffs after readback, or count this documentation as a new frog effect.
