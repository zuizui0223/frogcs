# Frozen exploratory ecology test: spatial × seasonal taxon accumulation in mapped PEM wetlands

2026-10-23. **Written before the new 2×2 accumulation outcomes were computed.** The same original NAAMP × NWI source previously yielded positive PEM acoustic alpha, gamma and two-round absolute bonus; thus this is **post-hoc source reanalysis, not preregistration, not independent biological data or an experiment**. User direction: **macroecology and ecological hierarchy, no prediction scores or literature review**. Frozen `main` and JAE RC6 manuscript/SI/submission must not change.

## Novel ecological question

Does the vegetation-associated frog acoustic pool gain from sampling **more physical stations** (spatial accumulation) differ from that from sampling **another within-year survey round** (temporal accumulation)? Does combining both dimensions yield an extra, positive or negative **space×time accumulation cross-difference** (complementarity/redundancy of observational sampling axes) in PEM-emergent wetlands versus other mapped wetlands?

The cross-difference is a *sampling-level joint accumulation contrast*, **NOT** a causal ecological interaction between species, plant taxa, or a higher-order interspecific effect. An algebraic cross term is expected even if every animal detection is independent; test contextual difference without claiming a null cross term implies independent ecological processes.

## Original source and experimental/sampling grain

Re-use original exactly `exploration/run_naamp_vegetation_withinyear_round_hierarchy_v0_1.py` **source() / build_rounds()** to retain all 2,869 matched ten-stop route-nights within **1,115 unique route×calendar-year groups / 274 independent physical routes / 20 States**. The upstream source contains **7,848 standardized NAAMP route-nights**, **6,236 NWI-complete ten-stop route-nights**, original source-only response-blind USFWS NWI **5,147 physical SiteIDs** and twelve GIS shards. Do not alter source run-year/site IDs, any threshold, allowed survey round identity (1–4), or original note that round4 is sparse.

Within each route×calendar-year, the **exact same 10 physical listening stations** are followed across R∈{2,3,4} observed seasonal survey rounds. At least two PEM mapped emergent-wetland stations and at least two other mapped-wetland stations with no PEM overlap must exist. The 250-m polygon GIS labels are static and are NOT contemporaneous botanical plants or vegetation phenology; original acoustic taxon labels including complexes retained. Two thresholds: CI≥1 all calls (main) and CI≥2 strong calls (secondary). Any/all silent stations retained, no biologically informed route selection.

Every original route×year supplies **all C(R,2) round pairs** for possible combination, but multiple pairs count as ONE route-year after averaging; multiple route-years count as ONE physical route in inference. Both PEM/nonPEM habitats are compared at fixed **exactly two physical stations** sampled without replacement, **exactly two survey rounds** sampled without replacement; no NWI+ versus NWI0 geographic effort imbalance.

## Four source-grounded exact accumulation expectations

For each habitat h (mapped PEM vs other mapped wetland) and each unordered observed round pair t1,t2 of one route-year, average across **all equally likely physical two-site samples of n≥2 mapped stations** within h:

- `G11` = expected # frog acoustic taxon units from **one physical site and one of the two rounds**, averaged over the two rounds.
- `G21` = expected # taxa from the same **two sites at one round**, averaged over the two rounds (exact hypergeometric no-replacement taxon inclusion).
- `G12` = expected # taxa from **one site pooled over the same two rounds**.
- `G22` = expected # taxa from **the same two physical sites pooled over both selected rounds**.

Taxon-level computations use the previously validated combinatorial `exact_two_round_pool(...,m=2)`, and all-round same-site unions; each expected gamma is not an observed independent biological sample. Validate results against **brute force complete enumeration** of site subsets and round choices on a known synthetic matrix including sparse diagonal detections, two silent rounds, and positive/negative cross differences.

Exactly decompose:
`S = G21−G11` (spatial taxon gain),
`T = G12−G11` (temporal taxon gain),
`I = G22−G21−G12+G11` (space×time cross difference),
`G22 = G11 + S + T + I`.

`I` need not be positive, and is *not* evidence of animal interactions. It quantifies whether the gain from combining spatial sites changes when both rounds are pooled (or equivalently if temporal bonus changes with spatial sample size), on the fixed original richness/scale metrics. Report PEM−other signed differences in all components at the physical-route level. Also report within-habitat route-balanced descriptive G11/G21/G12/G22, S/T/I to interpret both sides; do not turn a significant difference into one-sided "synergy."

## Exactly six fixed inferential endpoints

Declare before new readback six **two-sided PEM minus other wetland contrasts** in source acoustic taxon units:
1. **Primary** `ΔI_any` (spatial×temporal gamma cross difference).
2. `ΔI_strong`.
3. `ΔS_any`.
4. `ΔS_strong`.
5. `ΔT_any`.
6. `ΔT_strong`.

The original ∆G11 and ∆G22 are **descriptive only** (already overlapping prior positive richness/gamma questions), not new tests. All six results are reported whether positive, negative, or zero; pre-declared **Benjamini-Hochberg over six**. Infer with one physical-route equal mean of all its matched route-years: Student t(df=273) 95% CI and two-sided P, 4,999 whole physical route Rademacher sign flips per endpoint; 20-State equal mean/Student-t(df=19) CI and leave-one-State-out sign/range. Source coverage gates ≥150 route-years, ≥50 physical routes, ≥5 States, plus nonzero source variation; otherwise fail closed, do not switch subgroup. Main descriptive magnitude quantifies contributions to ∆G22, **not** a percentage decomposition of biological causation. As sensitivity, show equal-State mean and 1–2/1–3/2–3 round-pair component means (later pairs involving round4 sparse, documented), **no additional P tests**.

Main classification `exploratory_space_time_cross_context_difference` iff primary ∆I_any has *nonzero direction* with route CI excluding zero, six-test BH q<.05, route signflip P<.05, 20-State CI same direction, and ≥75% same-sign leave-one-State-out coefficients; otherwise `no_robust_PEM_specific_space_time_accumulation_cross_difference`. Secondary S/T tests can be supported if their own all-robust gates pass, but do not change primary classification.

## Scientific constraints

These are **acoustic community sample-incidence phenomena**, not frog abundance, true occupancy, reproduction, taxon colonization/extinction, direct frog-frog social interactions, or true trophic multispecies effects. NWI mapped wetland polygons can reflect hydroperiod, land use, water availability, acoustic transmission, and historical conditions; source survey dates 2001–2015 do not include contemporaneous plant species or biomass. The same source archive has many already studied endpoints; extra findings are not independent corroborations and post-hoc overall false-positive risk exceeds the within-family six-test adjustment. No searching literature and no adjusting the NWI map radius, season, species group, year, or statistic after readback to pursue P<.05.

Code `exploration/run_naamp_wetland_spacetime_accumulation_v0_1.py`; QA `.github/workflows/naamp_wetland_spacetime_accumulation.yml`; persistent numeric aggregate and ecological interpretation after executing/validating the actual source. **Never edit frozen JAE RC6 main/manuscript/SI.**
