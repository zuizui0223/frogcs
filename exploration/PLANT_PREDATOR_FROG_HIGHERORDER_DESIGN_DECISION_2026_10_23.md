# Plant-mediated frog trophic higher-order effects: empirical boundary and prospectively simulated design

**Date:** 2026-10-23. **Status:** 80 synthetic power scenarios computed and reproducible on isolated exploration branch. This is **NOT a new observation**, animal experiment, confirmation of mediation, or change to the frozen JAE RC6 manuscript/SI/main.

## Priority biological question

> Does aquatic plant structure change the *combined* effects of fish and predatory aquatic insects on focal frog tadpole survival, beyond the separately measured fish and insect effects?

The earlier 2 fish×3 macrophyte Šigutová et al. 2021 mesocosm records male toad choice across treatments, not larval survival and not simultaneous fish–odonate–frog interactions. Source-derived plant-choice effect in *Bufotes viridis* remains +45.86 percentage points (fishless aquatic plants versus no plants; exact permutation four-test q=0.0247). **No fish×plant interaction was FDR-supported**; a retrospective cross-toad fish×plant difference of 54.11 pp yielded q=0.0579, not confirmatory. No newly established causal biotic interaction follows from those comparisons.

### Experimental evidence outside frogcs (not a new source analysis)

1. **Adams et al. (2003), Ecology Letters** [DOI](https://doi.org/10.1046/j.1461-0248.2003.00435.x): sunfish reduced predatory odonate densities, indirectly facilitating bullfrog tadpole survival; macrophytes **not** manipulated. Different fish and frog life histories matter.
2. **Resetarits et al. (2021), Proceedings B** [DOI](https://doi.org/10.1098/rspb.2021.0558), [Dryad](https://doi.org/10.5061/dryad.t76hdr80m): 45 tanks in five blocks (7 fish-presence combinations plus two fishless controls) show ovipositing *Hyla chrysoscelis* avoids predator fish assemblages that cannot be predicted simply from all isolated single-species avoidance responses. Fish combinations used **six fish total** (single 6; pair 3+3; triple 2+2+2); such **substitutive** treatments also change per-species density. Plants were not manipulated and the response was oviposition, not survival.
3. **Xu / Böttner et al. (2025), Proceedings B** [DOI](https://doi.org/10.1098/rspb.2024.1149), [Dryad](https://doi.org/10.5061/dryad.kh18932h7): three living aquatic taxa (duckweed, competing green algae, herbivorous snail) show an animal consumer can indirectly increase plant growth by reducing its competitor, sometimes reversing the expected direct negative effect. This is independent previously published evidence that biotic indirect effects are context-dependent **but does not include frogs, fish or odonates**.

**None of these three experiments jointly manipulates P×F×O on focal tadpole survival.**

## Main trial: randomized P×F×O (8 cells/block), outcome survival

P = absent/low vs dense living macrophyte structure (predefined species, coverage, live biomass and shade measured); F = ecologically permissible fish absent/present; O = predatory odonate larvae absent/present at a preset initial density. Same local focal frog species, larval stage, size and baseline **20 larvae per independently randomized tank**. One tank per eight treatment cells per spatial block, fixed assay duration and standardized water/oxygen/temperature/hydroperiod. Spatial block and whole tank are experimental units, not individual tadpoles nor repeated days. **No animals are being manipulated at this design stage**; later work requires permits, biosecurity and animal welfare approval.

Declare the *marginal probability-scale* three-factor causal contrast:

`D_PFO = {S(1,1,1)-S(1,1,0)-S(1,0,1)+S(1,0,0)} - {S(0,1,1)-S(0,1,0)-S(0,0,1)+S(0,0,0)}`

where `S(p,f,o)` is the probability a focal larva survives a fixed period, measured in the randomized tank. That is **the difference in the fish×odonate difference-in-differences between plant treatments**. A 20 pp PFO contrast does **not** mean one tank has a 20 pp survival advantage. Significant D_PFO establishes a chosen-scale randomized treatment effect modification; it does **not** by itself tell whether fish killed odonates, whether odonates changed frog behavior, or whether chemical cues caused the response.

**Mediation is a separate intervention:** alongside the primary treatment, measure odonate density over time; in a prospective second stage randomize odonate restoration/protection versus a matched sham at fixed fish/plant treatments. Predator cages require a sham cage that controls flow, chemistry and shelter. A fish×odonate effect alone is *not* a mediated pathway estimate.

### Quantitative simulation (not measured effect sizes)

Hypothetical baseline survival by PFO cell order 000,001,010,011,100,101,110,111: `[0.80,0.54,0.64,0.56,0.82,0.66,0.70,0.72]`. Baseline PFO = 0 (both plant strata have fish×odonate risk contrast +0.18). Inject a signed `delta/8` shift to each cell to set exact risk-scale PFO=delta; the induced individual-cell shifts are only 2.5, 5.0 and 7.5 percentage points for delta=0.20, 0.40 and 0.60. Add shared within-block hydrology shift (Normal SD 0.025 clipped ±0.06), tank beta-binomial survival with **ICC=0.05 or 0.20**, 20 correlated focal larvae/tank. Fit two-sided **block-level t(df=B−1)** contrast, conservatively α=0.05/3 for three potential separately planned programme-level primary contrasts; **3,000 independent simulation replicates per scenario**. The model contains no mortality-related tank dropout, treatment-by-hydrology heterogeneity, fish mortality or spillover.

| PFO risk contrast δ | ICC | 8 blocks / 64 tanks | 16 / 128 | 32 / 256 | 64 / 512 | 128 / 1024 | First tested grid ≥80% |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | .05 | .097 | .264 | .611 | **.926** | .999 | 64 blocks |
| 0.20 | .20 | .058 | .105 | .254 | .522 | **.889** | 128 blocks |
| 0.40 | .05 | .443 | **.890** | .999 | 1.000 | 1.000 | 16 blocks |
| 0.40 | .20 | .178 | .471 | **.844** | .992 | 1.000 | 32 blocks |
| 0.60 | .05 | **.827** | .999 | 1.000 | 1.000 | 1.000 | 8 blocks |
| 0.60 | .20 | .416 | **.868** | .998 | 1.000 | 1.000 | 16 blocks |

Under **delta=0**, empirical false-rejection fractions range about .013–.021 across these grid points, close to the specified .0167. Monte Carlo half-width for a power estimate near .50 with 3,000 draws is ~1.8 percentage points. These threshold estimates are illustrative **grid crossings, not an animal-number justification**.

## Secondary trial: P×F×O×C (16 cells/block)

C = focal heterospecific amphibian competitor treatment. **Density control is critical:** adding a second species to 20 focal tadpoles raises total density, so C presence versus absence otherwise confounds species identity with crowding. If species-identity attribution is required, compare marked sentinel focal tadpoles at the same starting density while adding **equal numbers/biomass of extra conspecifics versus heterospecifics**, with identical handling/marking. If those matched controls are infeasible, call C an addition/density treatment, **not** heterospecific competition alone. This requires a new protocol and animal ethics review before use.

Use the alternating **16-cell marginal survival risk contrast** D_PFOC. Four-factor significance on risk scale is not automatically an interaction on a logit or hazard scale.

Hypothetical 16-cell baseline: each corresponding PFO cell's survival is reduced by .06 when C=1, no baseline four-factor interaction. Inject signed delta/16 to target four-factor contrast. Identical tank survival and error assumptions as above.

| Four-factor δ | ICC | 8 blocks / 128 tanks | 16 / 256 | 32 / 512 | 64 / 1024 | 128 / 2048 | First tested grid ≥80% |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | .05 | .057 | .121 | .302 | .625 | **.931** | 128 blocks |
| 0.20 | .20 | .031 | .055 | .112 | .253 | .524 | not reached |
| 0.40 | .05 | .212 | .528 | **.908** | .999 | 1.000 | 32 blocks |
| 0.40 | .20 | .081 | .218 | .485 | **.838** | .992 | 64 blocks |
| 0.60 | .05 | .476 | **.904** | .999 | 1.000 | 1.000 | 16 blocks |
| 0.60 | .20 | .179 | .513 | **.866** | .997 | 1.000 | 32 blocks |

**Practical decision:** the old v0.1 idea of **8 blocks ×16 tanks =128** is not confirmatory for modest four-factor effects under these assumptions. Prioritize an **8-cell PFO pilot** with ~4 blocks/32 tanks to get survival variance and baseline estimates (not a hypothesis test), then re-estimate required tank number from ethical and logistic constraints. Keep C/PFOC as a later hypothesis, not a default add-on.

## Crucial scale-sensitivity check

A purely additive **logit** survival model (`logit(S)=.1+.7P−1.0F−.7O`) has exactly zero logit PFO coefficient yet its survival-*risk*-scale PFO contrast is **−0.0456868** (−4.57 pp). This is nonlinear link-scale curvature, not uniquely evidence for a mechanistic three-body interaction. Pre-specify the survival-risk estimand, secondary logit-model comparisons and at least one mechanistic intervention before attributing species interactions.

## Reproducibility and scope

- Executed algorithm: `exploration/run_plant_predator_higherorder_power_v0_1.py`; NumPy 2.3.5, SciPy 1.17.0, Python 3.13.
- 80 simulated scenarios = 2 designs × 2 within-tank ICC settings × 4 true risks (including null) × 5 block counts, each 3,000 repetitions.
- GitHub Actions workflow `.github/workflows/plant_predator_higherorder_power_qa.yml` runs all cases and uploads the numerical JSON artifact rather than adding large generated JSON to `main`.
- The parent `exploration/plant-mediated-cross-taxon-audit-2026-10-23` keeps the earlier real source-audited toad result separately.
- Frozen `main`, JAE RC6 manuscript, supporting information and submission assets not changed.
