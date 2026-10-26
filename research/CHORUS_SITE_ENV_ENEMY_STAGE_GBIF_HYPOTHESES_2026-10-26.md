# frogcs H_ENV × H_ENEMY × H_PHASE: chorus concentration within hydrological breeding windows

**Prospective observational extension, dated 2026-10-26.** Author-requested merger into ONE frogcs manuscript. **Freeze RC6 science and source estimates**, do not alter `main`, `release/jae-multisite-rc6` or `submission/jae-multisite-v6`. The project already inspected RC6, NPS, Hungary, INBO and GloBI/GBIF outcomes; this proposal is **post-hoc relative to those**, and therefore only genuinely unseen external source/locations can support a qualified new prospective test.

## One proposed ecological question

> For species s and multiple monitored wetland locations i on a favorable rainfall episode t, does **excess acoustic clustering** arise because successful sites have fewer aquatic enemies/competitors, closer or farther breeding-stage phenology to their neighbors, or greater time-varying wetland availability, water permanence and emergent-plant refuge?

**Important correction:** NAAMP RC6's 10 survey stops are **sequential acoustic stops, not confirmed 10 separate breeding ponds**. A stop may cover multiple wetlands and a wetland may be audible from multiple stops. Never call `strong chorus at stop` a `concentrated pond` unless original physical waterbody mapping is verified. Freshwater GBIF biodiversity records near a stop also do **not** measure competitors *in that same pond*.

## Competing, non-equivalent hypotheses: all signs frozen BEFORE new GBIF values

| Hypothesis | Mechanism and prediction at the correct scale | Required data / distinct limitations |
|---|---|---|
| **H_ENV: Rain × physical water persistence** | Favorable recent rain activates sites that maintain or newly gain suitable shallow aquatic habitat. Effect of recent rain depends on actual pond hydroperiod: episodic reflooded pools may rapidly attract chorus; permanent ponds may retain adults and predators. **No universal sign for permanent vs ephemeral** is assumed. | Exact local pre-event rain (1/3/7-day), water-level/surface area and documented dry/re-wet; historical rain at NAAMP route centroid is not measured wetland refilling |
| **H_REFUGE: Emergent/submerged vegetation** | Vegetation structure modifies habitat suitability and potential prey refuge; response may be nonlinear, fish/predator-dependent and alter both detectability and true site choice. No assumption `more emergent cover always raises CallingIndex`. | Source-measured vegetation stem density/cover by pond×event, submerged cover, water depth; NWI Cowardin PEM is static mapped wetland class, not vegetation cover (%) |
| **H_ENEMY: Enemy / competitor release** | Within identical species×route×visit and fixed total strong stops (`k`), highly allocated sites have **lower measured previous or contemporaneous enemy exposure** compared with non-activated but *surveyed* site alternatives, after habitat, phenology, sampling effort and focal history controls. | Same-pond predator cohort size/number, actual fish/newt/odonate stage survey, within-site prey species competitors, encounter/mortality or experimental cues. GBIF positive sightings in a 5-km stop neighborhood are **exposure reporting only**; unreported GBIF ≠ no predator/competitor |
| **H_PHASE: Developmental or breeding-stage affinity** | Chorus-allocated sites may coincide with other species having nearby regional breeding peaks (`abs(peak_s−peak_other)` smaller) under common rain/temperature; competing scenario is **stage staggering** where prey oviposition avoids older predator larval stage. Similar **calendar month ≠ similar individual Gosner stage/size**, and the two expectations must not be collapsed. | Date × source-verified amphibian egg/larva/stage size and size-specific predator/prey records. GBIF `lifeStage=adult/larva` by month is incomplete, and seasonal overlap may reflect common weather and observer effort |

**Mechanism conflict is informative:** a favorable long-hydroperiod vegetated pond might have *more* competitors and predators and also *more* chorusing frogs. Under H_ENV, positive acoustic×enemy covariation need not imply facilitation; negative covariation need not establish avoidance. Separate potential interactions from stage/size-specific actual attack rates.

## Nested datasets and strict geospatial evidence tiers

1. **Tier P0 — same physical wetland**: field wetland ID and actual recorded predator/prey stages, vegetation and water state at shared dates. Eligible for stage/competition exposure hypotheses, still not necessarily causal without observed attack or experiment.
2. **Tier P1 — exact NAAMP listening SiteID coordinates with source-blind geometry QA**: permitted only to describe environmental **neighborhood reporting and mapped wetland context**. No `pond` label, no direct local presence/absence or trophic coefficients. Validate USGS original SiteID coordinates (SHA256 `f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83`), reject impossible longitudes and objectively flag geometrically inconsistent routes **before** any frog/GBIF outcomes. Source metadata has 12,064 coordinate rows and known gross geographic transcription errors. Never manually repair a wrong longitude based on desired frog results.
3. **Tier P2 — NPS recorder station (66 sites)**: original source records acoustic taxa and categorical `Hydroperiod`, with no verified 1:1 pond coordinate or event-level rain; suitable for multi-taxon acoustic history/timing tests, not wetland predator counts.
4. **Tier P3 — GBIF 1° / monthly or broad stop-neighborhood sighting**: useful for stage-label and phenology **reporting opportunity** only. Always quantify contemporary GBIF all-taxon sampling effort, unknown coordinate uncertainties, source/dataset effect and human date coverage. Do not reinterpret P3 as P0.
5. **Tier P0 independent analogue — Hungary 2024**: 29 field sites with actual precipitation, depth and emergent/submerged plant cover, 129 acoustic surveys, two fish-positive sites; source-backed out-of-site prediction is a valid **environmental filter comparator**, NOT an independent NAAMP multi-stop C replication.

## Frozen new-source geographic G0 before outcome use

Use `research/scripts/naamp_gbif_wetland_geo_g0.py` to sample source-coordinate-consistent NAAMP listening routes **without inspecting any calls**. Sample 24 distinct routes by deterministic SHA ranking (not by frog activity); within each choose two source stops with maximally distinct within-route positions, making **48 stops** (unless source consistency reduces population). For these, use strictly external GBIF `occurrence/search` results to inspect 2010–2015 same-period **presence-record opportunity**, not biology:
- 5-km radius around an **acoustic stop** is a search **neighborhood** (neither one pond nor the source's field GPS precision), and source points must pass G0 geometry QC;
- GBIF `Anura` other-frog reports = potential alternative chorus community reporting; `Caudata` larval reports = candidate aquatic salamanders, possibly prey or competitors, **not all tadpole predators**; `Odonata` larval/nymph reports = candidate aquatic insect predators, **not guaranteed dietary interactions**;
- separate full GBIF year-2010–2015 report counts and explicitly stage-labelled `larva/tadpole/nymph` facets; coordinate uncertainty missing or >1 km in any *retrieved point* must not count as precise records. Record main GBIF source dataset mix and timestamp coverage. Never treat `count=0` as biological absence;
- retrieve source-adjusted *background all-taxon records* from same spatial neighborhood, month/year and source, and a nonpredatory matched aquatic-group candidate when possible. No response-blind causal interpretation follows from reporting counts.

**MAPPED WETLAND:** independently inspect NWI polygons at reported recorder coordinates (source NOAA/USFWS NWI layer). `no point polygon` ≠ no nearby wetland, `PEM1A/PEM1C/PEM1F` ≠ exact water depth or live plant stem architecture. Reject geometry errors instead of nearest-pond interpolation. Local wet/dry time series requires a new field or source-validated remote-sensing panel for the same wetland.

### Pre-specified qualification gates (no posthoc thresholds rescue)

- G0 geography: SHA-verified original coordinates, no invalid or inconsistent routes included; 24 distinct eligible independent routes and 48 surveyed stop neighborhoods, or declare smaller coverage. Each query must report success vs fail; run ≤48×(3 taxon types + 1 all-source background) GBIF queries and ≤48 NWI point-only queries. Aggregate responses only; no wildlife locality keys disclosed in committed summary.
- G0 stage: require **≥15 source-independent stop neighborhoods per species-stage cohort** with at least one verified **stage-labelled, same-period, ≤1-km-precision GBIF record** plus ≥3 independent GBIF source datasets, else stage-proxy comparison ineligible. A `genus` or `adult` record is not a larval observation.
- G1 outcome linkage: use **same frozen NAAMP species×route×paired night** with stop-level wet vs dry strong call allocation and exact-k conditional null; preserve focal own-site history and total strong stops, route×year/weather, recording effort, observer bias. **Do not refit/fix RC6**; exploratory source-labeled extension only. Exposure covariates must precede outcome if selection/avoidance implied. No GBIF stage label from after survey date can predict a prior survey without historical restriction.
- G2 joint interpretation: require physically matched frog calls AND true predator/prey developmental stages AND local hydroperiod AND at least one matched measured vegetation variable; otherwise a pooled explanatory/causal `predator reduction of RC6 residual` is **NOT IDENTIFIED**.
- Multi-model compare **same eligible sample** M0 (`focal-site recurrence + rain+sampling+source/habitat`), M1 (`+ mapped hydroperiod/vegetation`), M2 (`+ predator/competitor sampled abundance and stage-size mismatch`), M3 (`+ interaction with rain/water persistence`). Prefer leave-one-route and leave-one-year out, null model preserving exact route-night strong`k`. Models cannot use future site/chorus outcomes as covariates or infer true biological absence from GBIF.

## Current observed evidence already present before this new hypothesis

- **NAAMP RC6:** route-night conditional excess C residual +0.2968537 and own strong-site effect +0.151094. Not an independently measured frog pond.
- **NPS acoustic × broad Hydroperiod:** earlier strong-site slopes Ephemeral +0.3523, Semi-permanent +0.5022, Permanent +0.4950; pooled interaction contrasts Semi−Ephemeral +0.1500 and Permanent−Ephemeral +0.1428, but within Ephemeral strict stratum not estimable. These are historical acoustic associations not direct water-volume effects.
- **Hungary original measured covariates:** weather/season Brier 0.2080 vs depth+wetland class 0.1742 on acoustic frog detection (site-blocked); emergent cover beyond those variables worsened prediction to 0.1753. Fish-positive only 2/29. This supports investigating a wetland suitability filter rather than automatically assuming refuge or enemy release.
- **Full GloBI × GBIF stage patterns:** phase overlap above 11-shift average for 16/18 source-selected links, but same-guild/stage matched prey specificity only 26/56 at strict reporting threshold. Generic seasonal co-reporting cannot establish predator/prey-specific timing or realized aquatic predation.
- **Controlled experimental developmental stage:** original `Leptodactylus fuscus` cues×drydown factorial bath-heldout M0 beats biotic-cue M1/M2 on metamorph mass and time, not a field predator attack test.

## Outcomes of this project extension

1. A **geometry/GBIF data-readiness receipt**, honest if it finds no sufficient source stages.
2. A comparison panel/working model only **if** same-dataset source stage/time/effort variables qualify. Never tune geographic radius, stage selection or species after seeing outcomes.
3. Manuscript reporting that honestly separates **rain/hydrology/vegetation**, **lower apparent aquatic enemy reporting**, and **breeding-stage synchronicity or ontogenetic staggering**, noting absent causal stage data.

These are the user-requested **new leading ecological questions**; unrelated engineering and new repos remain `later`. Keep all work inside `zuizui0223/frogcs`.
