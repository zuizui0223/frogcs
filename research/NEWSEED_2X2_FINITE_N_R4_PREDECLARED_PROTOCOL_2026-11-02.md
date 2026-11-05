# R4 New-seed extension: finite-N 80-year consequences for the same 256 original vegetation 2×2 backgrounds

2026-11-02. **Source-locked prospective calculation before examining finite-N outcomes.** Stacked on Draft PR #161, whose independent 256 canonical structure/rate draws and genuine 80-year deterministic seasonal responses are already complete. Preserve all existing main/PR145/146/158/159/160/161 biological results and their negative interpretations. All rates remain synthetic, no field calibration or new animal observations.

## Question

Given the same 256 new-seed original main model backgrounds (seed 20261123), each with exactly four legal plant treatments 00/10/01/11 crossed with three source developmental contexts and fixed original `attack=.5`, `rho=.75` and original nuisance θ, does the **combined vegetation mechanism** that generated model-native four-sign patterns at higher frequency:
1. increase *or decrease* modelled **year80 frog patch occupancy, last20-year mean occupied patches and mean frog count**, relative to neither function? Does a 2×2 factorial interaction appear at population rather than four-sign scale?
2. change the **movement-associated occupancy contrast** between moving and nonmoving identical source biology? Are the original model's true zero→positive patch returns and local extinctions altered?
3. change its long-run demographic consequence between count scales `q=3` and `q=12` and developmental contexts? Is high-q occupancy at ceiling?

This checks the **same new 256-source backgrounds as PR161** and DOES NOT select sources based on whether they passed the four-sign criterion. No retrospective selecting favorable viability/rate/time contexts. The original 20,000 R2 exploratory rate-region selection is pre-existing, not independently inferred from field observations. We will report all four plant arms and both q scales and movement levels, including null/opposing effects.

## Frozen source, numerical model and sample unit

- Same **unchanged seasonal biology** at `main` commit SHA `5e2f0a87c639df373fa2700b29403d2ab417a1cc`, original `final_mechanism_common.catalog` and 80y annual delayed recruitment.
- PR #161 source background generator `confirmatory_2x2_vegetation_predator_switch.original_draws` at seed **20261123** exactly reproduces 3,072 structures×stage×plant treatment tuples. Require equivalence to archived original PR161 source table before releasing R4.
- **Finite-N stochastic population protocol copied by calling the unmodified PR160 `integrated_finite_main3600.run_finite_batch`**: fixed original eight 2×2×2 V/S/D patch vertices connected in artificial ring; initial individuals = source density×q; binomial season completion and survival, Poisson delayed local recruits and **external immigration retained ON**, conservative symmetric annual left/right `TRANSFER=.15` for carryover/recruit individuals when movement is ON. The model has discrete counts and immediate stage population feedback, not additional field measurements.
- All **3,072 PR161 source M×θ×stage×plant** proposals × **q∈{3,12}** × **movement OFF/ON** × **two new numerical process seed labels {311,313}**, with **S→F predation ON in this primary experiment** = **24,576 genuine 80-year synthetic population arms**. Each original source identity has 4 plant treatments × two q × two movement × 2 seeds within each of 3 developmental contexts. Any source loss fails.
- **16 source shards** each holding 16 distinct base backgrounds; **1,536 80-year population arms per shard**. Original PR160 80-year method functions are used unchanged. The PR160 random generator includes original proposal draw ID/arm in the key, so **paired model structures and theta DO NOT imply identical random draws across plant arms**. Two seed *labels* are crossed; include stochastic Monte Carlo noise in interpretation.
- The independent resampling unit is **256 original base backgrounds**, not 24,576 arms, 3× repeated contexts, 8 model-patch vertices, seed labels or colonizations. Use 10,000 source-background bootstrap replicates with frozen seed **20261125**. Cluster the three contexts together, and average two process seeds before calculating a source's matched counterfactual contrasts.
- No additional free historical rate exploration, no plant treatment selection by model agreement with NAAMP, no calibrated occupancy probability or acoustic calling mapping.

## Primary and secondary endpoints (locked)

**Primary per fixed q and context:** estimate source-paired means and model-source 95% bootstrap ranges of `year80 occupied F patches(11)−occupied F patches(00)` and the **2×2 factorial** contrast `11−10−01+00`, separately at movement OFF and ON. Report `year80 occupancy` bounded 0–8, and **mean occupied F patches in years61–80** as a non-ceiling-resilient companion (still capped 8).

**Secondary:**
- `mean_F_count_year61_80` model integer F counts (not density or wild real census), with the same 2×2 contrasts;
- `recolonization_events_80y` and `local_extinction_events_80y` (complete census of model 0→positive and positive→0 yearly patch transitions). The original finite-N model contains immigrants, so local reoccupancy is NOT uniquely caused by movement;
- `movement_assisted_returns_80y` model source flag (`incoming_f>0` at new positive patches), **co-occurrence with annual movement**, not an independent proof of movement necessity because local/external recruit arrivals may also occur;
- full 2×2 plant interaction on **movement ON–OFF effect** for each q and developmental context, and `[movement effect(11)−movement effect(00)]`, with source cluster bootstrap. These are paired population-model interventions, not actual wildlife dispersal rescue.
- proportion of 80y arms with all 8 patches occupied at q12 and q3 to diagnose ceiling/saturation; do not attribute a null q12 to absence of biological function.
- Explicit ecological lens: the PR161 positive **model-native 4-sign acceptance synergy** and negative **pooled model mean log aquatic frog cohort effect** do not entail a positive effect on 80y finite-N occupancy.

**Scientific decision rule:** We will call a positive source-average occupancy shift or positive factorial synergy under a specified stage/q/movement regime only if the source-bootstrap 95% Monte Carlo interval excludes zero. Main full-design claim must display all stages/q/movement and any sign changes. A positive selected source subgroup cannot override a null/negative full-design effect. No multiple-comparison-corrected field inference; intervals are model source Monte Carlo uncertainty conditional on hypothesis assumptions.

## Tests and independent audit gates

1. Original PR161 canonical source IDs, behavior/litter/gate and all θ must match the archived original true80 PR161 results (exact old draw ID, model ID, source ID, context, arm, rate tuple), without biological resimulation in the auditor.
2. Each 16-source shard emits exactly 1,536 genuine full-year80 population results, with all q/movement/seed/plant/stage cells, 0–8 occupancy, nonnegative integer returns and extinctions, balanced movement and original source SHA.
3. **Original PR160 finite-N code's source replay gate** checks unchanged main seasonal and annual 4y expectation; an independent seed-only model test checks conservative integer ring transport and coherent model zero/positive patch counts.
4. Across 16 immutable CI artifacts, verify full **24,576** source stochastic arms and **256** base independent backgrounds, no duplicated keys, 3 stage repeats and 4 plant variants; original 3,072 distinct PR161 deterministic source identities; 10,000 cluster source-bootstrap and full numerical outputs.
5. Full **R4 observed model results** are recorded in a reusable separate report and manuscript without altering previous R1–R3 claims. Failure to show the previously hypothesized R4 rescue or synergy must be reported as such. No wild prediction, actual predator replacement or NAAMP observed causal effect will be inferred.

## Execution

Publish code and experiment in **separate stacked Draft PR #162** based on PR161; do not merge, retune after outcomes, or submit the paper. Original PR161 genuinely independent test and PR160 prior positive/negative results remain intact.
