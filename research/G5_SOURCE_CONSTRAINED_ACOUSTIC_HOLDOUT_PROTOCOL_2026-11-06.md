# G5: source-prior mechanistic geometry as a constrained adult acoustic predictor

**Prospective field prediction design frozen before the new G5 source scores are inspected; 6 Nov 2026.**

## Reason / prior result

G4 original-source preflight (Actions #42172357235) recovered all 4,248 NAAMP physical acoustic sites, 63,180 completed visits, 506 vegetation-positive sites, 432 route components and 56 geographic blocks. **15 of 16** low/high O/S × V field cells met the prespecified minimum; the target-group-background V1 / high caudate / high odonate cell had 18 sites, below the 20-site minimum. Hence a universal eight-corner field-sign claim across both backgrounds is **not source-eligible**.

G4 also demonstrated to numerical precision (maximum residual <1e−15) that multilinearly interpolated eight-corner source F_B values fall in the span of saturated empirical `1,O,S,V,OS,OV,SV,OSV`. Therefore adding a mechanistic column to the full interaction regression could only reparameterize the same predictor space under ridge, not identify the underlying trophic process.

**G5 question:** Can a *pre-fixed one-dimensional shape* from the original modelled trophic mechanism explain adult calling on genuinely held-out geographic blocks as well as, or better than, empirically unconstrained multi-term interactions? That would support a model-constrained **predictive compatibility** claim, not wild predation identification.

## Frozen source inputs

1. Original field: same 4,248 sites / 63,180 completed acoustic visits, both original uniform and target-group SDM backgrounds; original site/visit files from `main` SHA `5e2f0a87c639df373fa2700b29403d2ab417a1cc`.
2. Source geometry: G4's archived `G4_predirected_source_priors_two_plant_arms.csv` from [Actions #42172357235](https://github.com/zuizui0223/frogcs/actions/runs/42172357235). The source prior averages **all** 256 independently sampled original PR161 model backgrounds × three developmental contexts, regardless of model four-sign acceptance or frog amount, into the eight source log F_B corners of **both** plant mechanisms active (11) and neither plant mechanism active (00); not selected by NAAMP responses.
3. Original PR145 fixed five geographically held-out folds and train-only binomial penalization ridge=10, source `acoustic_mechanism_cv` SHA `a5ddc281ba17017a52b404a5725327f6e829824f`; and unchanged G1 `design_matrices` from PR162. No spatial fold tuning on held-out calls.
4. Original O and S *environmental suitability* rank transforms (affine to [0,1]), binary landscape V. Direct source 8-corner logF_B interpolation has no independent dimension beyond the full free factorial; strip its additive components and retain only its fixed O×S/O×V/S×V/O×S×V **interaction geometry**. Source-interaction columns are calculated without using calling outcomes.

## Predeclared model comparison

Compare six otherwise-identical binomial adult **strong-call / completed visit** prediction rules on the *same original geographic source holdouts* and both backgrounds:

- `env_add`: original G1 fixed additive environment O,S,V, survey, water, climate, geographic controls;
- `env_all`: original G1 with all four unrestricted empirical O/S/V interactions (PR145 score replay control);
- `flex_add`: `env_add` + the original 21 nonlinear shared-environment terms;
- `flex_all`: `flex_add` + the four unrestricted O/S/V interactions;
- `flex_prior_11`: `flex_add` + **one** source-prior model interaction geometry feature from 11, with positive-only association to adult calling (`beta>=0`) fitted on training blocks only;
- `flex_prior_00`: same, but plant mechanisms 00 as a pre-fixed alternative-structure control.

The `beta>=0` monotone adult calling response to synthetic aquatic frog F_B is an **untested observation-link assumption**, not independently calibrated. It prevents a free sign flip from spuriously claiming that the mechanism predicts a pattern opposite to its source simulation. The original model/field field-SDM rank transfer is another explicit untested assumption. Other coefficients use original PR145 binomial ridge 10; no class balancing, posterior source weighting or O/S map retuning on held-out calls.

Primary test: for the 11 feature, **NLL reduction per original completed visit** versus `flex_add` (same 56-block cluster source bootstrap, 999 replicates seed 20261106). Require **both** SDM backgrounds to have positive 95% block intervals and the source-proxy feature's fitted slope to be positive in >=4/5 folds in **both** backgrounds before claiming reproducible *predictive* compatibility.

**Secondary safeguards:** (i) 11 vs the source-precommitted 00 structure; (ii) 11 vs `flex_all` (not necessarily nested), with uncertainty; (iii) full empirical `env_all` and `env_add` NLL must reproduce historical PR145 values within 3e−5; (iv) same spatial blocks and sites under all six models; (v) no meaningful novel feature beyond saturated free interactions is claimed (mathematical redundancy is exact).

Even if G5 passes, it does not demonstrate odonate/salamander predator abundance, pond refuge, stage chronology or larval→adult survival: the source 11 mechanism depends only on same R1 suitability proxies, so identification is still impossible without independent observations of predators/plant function.

## Stop/interpretation rules

If the 11 source prior does not beat both backgrounds against nonlinear shared environment, write **"model-native pattern and demographic divergence, but no robust field-level mechanism discrimination"**. Do not substitute better results from 00, a stage selected after seeing field outcomes, a favorable O/S mapping, or alternative synthetic attack/rho. G4's insufficient target-group V1/high-high direct cell remains a separate limitation regardless of continuous prediction performance.

All original R1–R4 positive outcomes, G1/G2/G2B negative observation bridge checks, G3 GBIF qualification failure and P1 source-level stage effects retained. Keep PR Draft and main untouched; no field causal or journal submission claim.
