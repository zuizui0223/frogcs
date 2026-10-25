# frogcs research — frog chorus, wetland vegetation and stage-structured biotic interactions

Status 2026-10-25: **independent prospective macroecology branch**, not a reopening of RC6 JAE or WFTS; `main` manuscript unaffected.

## Start here

1. **[New core question: rainfall × recurrent sites × macrophytes × stage interactions](CHORUS_WETLAND_VEGETATION_BIOTIC_HIERARCHY_V0_1.md)** — conceptual DAG, strict inferential boundaries, falsifiable tier sequence E0–E5, observational data contract, remote-sensing and published-data sources.
2. **[Current real NAAMP benchmark values](RC6_TO_VEGETATION_BIOTIC_BRIDGE_2026-10-25.json)** — machine-readable direct extraction from locked `provenance/CURRENT_RESULTS.json`; do not confuse local water/plant/predator mechanisms with already-adjusted atmospheric weather.
3. **[Emergent-plant mechanism evidence ledger](EMERGENT_VEGETATION_HIERARCHY_EVIDENCE_2026-10-25.csv)** — cited external studies with positive, negative, contingent and detectability effects; effects are *not* frogcs estimands.
4. **[GloBI stage-interaction live API pilot](GLOBI_TROPHIC_DIRECTION_PILOT_2026-10-25.json)** / [observational sample](GLOBI_STAGE_OBSERVATIONS_SAMPLE_2026-10-25.csv) — independent-sources and stage-QC needed; no true global reversal rate estimated.
5. **[Prospective held-out site-level comparison](scripts/compare_frog_vegetation_biotic.py)** — executable E0–E4 covariate-screening models (Brier, log loss); *not* conditional multi-site C or a joint causal model. Run `python research/scripts/compare_frog_vegetation_biotic.py --self-test` for synthetic-only data checks. E1–E4 require fully observed pond-event panels and cannot be run on NAAMP alone.

## Next empirical datasets (source and compatibility checked)

- [Ten-source availability and grain matrix](WETLAND_BIOTIC_MACRO_DATASET_MATRIX_2026-10-25.csv): distinguishes real acoustic histories from site-specific plants/fish, eggs/larvae, mesocosm interventions and stage-resolved food-web links. **Do not pool them as the same wetland observations without measured co-location.**
- Most informative vegetation × fish benchmark: 55-wetland Australian Dryad DOI 10.5061/dryad.b8gtht7b5.
- Most informative plant manipulation: 4 Great Lakes wetland Typha-removal/channel experiment, DOI 10.5061/dryad.wdbrv15tb (fish, aquatic invertebrates, plants, amphibian larvae, DO, 2 years).
- Most informative development-stage turnover: 25 seasonal Hokkaido floodplain waterbodies (Rana pirica, Hynobius retardatus, macroinvertebrates and fish), DOI 10.1002/ece3.70880; **not** measured emergent architecture or frog chorus.
- Dense **Typha dominance can be detrimental to habitat heterogeneity and oxygen even though some emergent cover is beneficial as refuge**. Model structural mosaic and plant identity, not just a monotone cover slope.

## Other relevant material

- [Original stage-dependent food-web hypotheses](ONTOGENETIC_TROPHIC_REVERSAL_PROSPECTIVE_V0_1.md).
- [Global food web + acoustic eavesdropping + meth-eDNA program](STAGE_MACRO_CHORUS_METHEDNA_PROGRAM_V0_1.md).
- [Evidence for acoustic eavesdropping](CHORUS_EAVESDROPPER_EVIDENCE_2026-10-25.csv).
- [Age/spawning and other meth-eDNA evidence levels](EDNA_METHYLATION_READINESS_2026-10-25.csv).
- [GloBI stage-annotation sample](GLOBI_OCCURRENCE_STAGE_PILOT_2026-10-25.json) / [full-snapshot script](scripts/globi_stage_macro.py).

## Research boundaries

- **NAAMP SiteID ≠ verified individual pond;** see [coordinate geometry QC](../revision/NAAMP_COORDINATE_GEOMETRY_QC_V0_1.md).
- **Past calling sites ≠ individual philopatry**, nor egg/tadpole/juvenile success.
- The unexplained residual concerns broad already-measured atmospheric/observation effects, **not all local wetland environment**. Pond-level plants, hydroperiod and predator stages remain absent.
- **Vegetation × fish can be positive or negative** depending on frog taxon, plant structure, predators and target outcome; do not assume all emergent cover is refuge.
- **Predicting marginal call probability is not predicting the constrained multi-site configuration**; C requires a separately held-out null generator preserving the appropriate first-order incidence constraints.
- A stage-resolved GloBI edge and an inferred wetland habitat class cannot be joined into demonstrated concurrent local predation.

## Priority action when new data are available

Acquire/source-audit site-coincident time-stamped hydrology, emergent/submerged vegetation, fish/odonate/salamander stage censuses and frog calls. Require pre-event timestamps, wetland polygons and verified SiteID associations before model E1/E2/E3 execution. Use independent route/study/period holdouts. Only then revisit constrained C, site-history attenuation and acoustic signal effects.
