# Multigeneration trophic reversal: spatial ABM + stage-structured reaction–diffusion benchmark

Status: exploratory *mechanism* PR, 2026-10-31. Base: `research/nee-evidence-gates-20261029` (PR #144). **Sibling of acoustic bridge PR #145**; not a follow-up patch to that PR or to `main`.

## Why this is not just "add generations"

The current source in `research/scripts/stage_vegetation_network.py` is a *deterministic seasonal cohort-hazard kernel*. It includes optional `reverse`: postmetamorphic frog (F) predation on dragonfly during emergence (D). `multiyear_stage_network.py` connects season completions of all three guilds through adult carryover, density-dependent local recruitment, maturation delays and immigrants over 80 years, plus 160-year sensitivity. **The path to later years and an F→emerging D reversal edge already exist.** It is neither an individual-based ABM nor a spatial PDE, and does not track localized prey encounters, dispersal or ancestry.

The new study tests **whether stage reversal generates different local and lagged demographic effects when space, local extinction, stochastic encounters, and next-generation recruitment are explicit**. It does not assert that all adult frogs hunt adult dragonflies, that adult salamanders reverse their role, or that observed reversal frequency is high. Beranek, Clulow & Mahony (2023), *Ecology* DOI [10.1002/ecy.4108](https://doi.org/10.1002/ecy.4108) documents `Anax papuensis` larva→frog tadpole and postmetamorphic `Litoria aurea`→dragonfly larva/emerging metamorph. Population-level consequences are not measured by that observation.

## Models and common reaction contract

| Component | ABM (stochastic micro-model) | Reaction–diffusion PDE discretization |
|---|---|---|
| States | Identified individuals with stage, location, lifetime age, birth year, parent ID, lineage generation | Seven *stage density* fields on the same periodic patch ring |
| Guild stages | F:tadpole/adult, S:aquatic/adult, D:nymph/emerging/adult | Same seven stages |
| Loss links | S-larva→F-tadpole; D-nymph→F-tadpole; D-nymph→S-larva; optional S-larva→D-nymph; postmetamorphic F→D-emerging | Identical stage-specific per-capita hazards as mean-field |
| Births | Adult offspring sampled as Poisson events, seasonally gated and reduced by local aquatic crowding | Expected seasonal births from density-dependent adult fecundities |
| Maturation | Exponential stage-transition events, *not fixed ages* | Same maturation rates |
| Dispersal | Individual nearest-neighbor jumps with periodic boundary | Laplacian finite-difference flux, stage-specific mobility |
| Vegetation | Cell-specific *hypothesized* refuge multiplier, no EarthEnv calibration | Same hypothetical response function |
| Outputs | Per-year stage abundance/cell, deaths by directed link, lineages and next-generation changes; stochastic replicate variability | Same expected stage abundance/death-path diagnostics, numerical convergence |
| Comparison | Reversal-on vs reversal-off, identical initial states and common random seeds for *paired but not pathwise identical* counterfactuals | Deterministic paired edge ablation; ABM vs PDE only at compatible mean-field scale |

**Continuous-time reaction hazards** are approximated with finite `dt` in both models. PDE transport is an explicit finite-difference approximation on a 1-D *synthetic* ring (not a mapped wetland network). The ABM uses finite counts and local encounters; its mean is not mathematically identical to the PDE under nonlinear hazard feedback. Both are hypotheses, not an empirically fitted population forecast.

## Frozen minimum experiment

1. Default: 8 periodic patches with alternating vegetation low/high; identical starting stage counts for both models. 20 model years; independently log each year and cumulative predation on each of five links.
2. `reverse=True/False` controls **only** F adult→D emerging; retain D nymph→F tadpole and fixed third-guild edges. Compare immediate D-emerging losses, next-generation D nymphs, longer D adult abundance, and F abundance.
3. Toggle adult mobility and third-guild edges in *additional* fixed controls to ask whether migration compensates for the locally reversed edge. Keep no-reversal and no-predation controls.
4. Repeat ABM seeds, present mean/spread; show deterministic PDE trajectory separately. Do not estimate likelihood or field effect sizes from synthetic replicates.
5. Tests: nonnegative densities, bounded dispersal, mass accounting, stage-gated edge ablation, true second-generation ancestry, no-overlap zero, PDE refinement and seed-repeatable ABM paths. Explicitly retain negative or counterintuitive results.

## Main hypothesis and endpoints

**H1: reversal-window leverage.** A postmetamorphic F→D-emerging interaction changes *future* D nymph recruitment through D adult survival, even if F tadpole deaths occur earlier. Evaluate D nymphs at t+1 and t+2 and F larvae/adults at lag, not the sign of present-season frog survival alone.

**H2: spatial demographic buffering.** Stage-specific dispersal and asynchronous local stage overlap can turn a local mortality effect into a weaker, stronger, or spatially displaced multigeneration response. Compare abundance, occupancy and connectivity under stage-specific diffusion/jump rates.

**H3: third-party modification.** The D nymph→S larva and optional S→D links may amplify or compensate F effects; whether S adults feed on other stages is **unspecified**, not silently assumed.

Counterfactuals are within-model **in silico interventions** only. A single observed frog–dragonfly pair does not establish that these rates apply at NAAMP sites or to all wetlands.

## Interpretation gate

A successful PR delivers executable code and numerical diagnostics. **Do not** say this explains the NAAMP acoustic OV association, validates the predecessor's annual recurrence, or identifies a field population mechanism. The follow-on methylation-eDNA program is an independent stage-observation opportunity, and observed predation rates / egg-larva-adult demographic calibration are needed before ecological parameter inference.

Proposed files: `research/scripts/multigeneration_reversal.py`, `research/scripts/test_multigeneration_reversal.py`, `research/results/multigeneration_reversal_20261031/`, and a small GitHub Actions test/replay workflow.
