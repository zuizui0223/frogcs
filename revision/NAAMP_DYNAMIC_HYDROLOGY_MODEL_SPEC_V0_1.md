# NAAMP dynamic-hydrology model specification v0.1 — 2026-10-07

**Frozen before any hydrology-augmented concentration result is calculated.**

This specification fixes how remote-sensing hydrology enters the existing principal comparator.

## Response and null machinery

Unchanged from the existing higher-order within-taxon concentration analysis:
- endpoint: within-taxon concentration among route-new taxa
- conditioning: route-new taxon coefficient and total extra-stop coefficient
- simulation replicates: 1,000
- dry-state persistence anchor: a = 0.75
- pair-level total wet-incidence matching
- deterministic route folds inherited from the principal comparator

No new ecological response is selected.

## Primary analysis sample

The final mechanism analysis uses only:
1. pairs in the existing 2,916-pair strictly-prior-history population;
2. routes passing the strict geometry-only remote-sensing gate;
3. pairs for which all ten focal physical SiteIDs have valid M3 hydrology values in both wet and dry focal runs.

All M0–M3 models are compared on this identical complete-case sample.

This all-ten-sites rule supersedes the >=8/10 wording in the v0.3 variability coverage paragraph for the primary mechanism analysis. No missing focal hydrology value is imputed.

Coverage gate:
- >= 1,500 pairs
- >= 300 routes
- >= 15 states

If the all-ten M3 gate fails, M3 is variability-inconclusive. M1 may still be evaluated separately on its own all-ten-site current-hydrology complete-case sample under the same pair/route/state thresholds.

## Cell-level training data

Hydrology coefficients are learned using species × RunID × physical-SiteID calling cells from the unique focal RunIDs represented in the final complete-case principal-pair universe. A RunID that appears in more than one adjacent-year pair contributes its calling cells only once to coefficient training.

Binary training response:
- y = 1 when the species has CallingIndex 1–3 at the stop;
- y = 0 otherwise.

Training cells use only routes in the training fold opposite the focal route fold.

A species' focal-route cells never contribute to the coefficient applied to that focal route.

## Covariate control in coefficient training

For each species, hydrology coefficients are estimated while controlling for:
- log(1 + DaysSinceRain)
- mean run air temperature
- first annual sine/cosine harmonics
- State
- RunNumber

These broad terms are controls only. Their fitted coefficients are not added to the mechanism generator because the M0 comparator already contains the cross-fitted rainfall response.

## Within-SiteID centering of hydrology covariates

Hydrology coefficients target temporal wetland-state change, not static habitat differences.

Before species-specific fitting, for each physical SiteID compute the mean of each hydrology covariate across the available focal RunIDs for that SiteID and center:

- H_current_c = H_current - mean_site(H_current)
- recent_wetness_3m_c = recent_wetness_3m - mean_site(recent_wetness_3m)
- hydro_sd_12m_c = hydro_sd_12m - mean_site(hydro_sd_12m)

Because a physical SiteID belongs to one route and therefore one deterministic route fold, this centering does not leak focal-route information across folds.

The fitted hydrology coefficients therefore reflect within-site temporal association with calling.

For focal-pair prediction, the centered site mean cancels exactly, so the applied shift remains beta times wet-minus-dry hydrology at the same SiteID.

## Nested species-specific hydrology models

M1 training model:
calling ~ broad controls + H_current_c

M2 training model:
calling ~ broad controls + H_current_c + recent_wetness_3m_c

M3 training model:
calling ~ broad controls + H_current_c + recent_wetness_3m_c + hydro_sd_12m_c

For M1–M3 coefficient comparison, training uses cells with all M3 variables available. Thus added-variable effects are not created by changing the training sample.

## Estimability and fallback

Inherited minimum information:
- >= 20 positive calling cells
- >= 5 positive routes

If below gate:
- all hydrology coefficients for that species/model/fold are set to zero.

Primary fitting:
- binomial GLM.

Fallback for separation or unstable/nonfinite coefficients:
- L2/ridge regularized binomial fit, alpha = 0.01.

If the fallback still gives nonfinite hydrology coefficients or any absolute hydrology coefficient > 20:
- hydrology coefficients are set to zero for that species/model/fold.

No species is removed because its hydrology response is inconvenient.

## Applying hydrology to a focal pair

For each species and each of ten stops:

M0 logit:
logit anchored prior + cross-fitted species rainfall shift

M1 adds:
beta_H * (H_wet - H_dry)

M2 adds:
beta_H * (H_wet - H_dry)
+ beta_recent * (recent_wetness_3m_wet - recent_wetness_3m_dry)

M3 adds:
all M2 terms
+ beta_variability * (hydro_sd_12m_wet - hydro_sd_12m_dry)

After these stop-specific shifts, solve the same pair-level common shift so expected total wet incidence exactly matches the observed wet incidence magnitude.

Therefore remote sensing is tested on where activity is allocated, not on whether it trivially predicts more total activity.

## Simulations

Use 1,000 Bernoulli simulations for each M0–M3 on the identical focal sample.

Fixed seeds:
- M0: 2840310
- M1: 2840311
- M2: 2840312
- M3: 2840313

For every model report:
- observed concentration beta
- predicted concentration beta
- observed conditional residual
- null residual 95% interval
- plus-one upper-tail P

## Primary mechanism decomposition

total hydrology fraction:
(residual_M0 - residual_M3) / residual_M0

current-state increment:
(residual_M0 - residual_M1) / residual_M0

recent-persistence increment:
(residual_M1 - residual_M2) / residual_M0

variability increment:
(residual_M2 - residual_M3) / residual_M0

These quantities are reported even if negative.

## Sufficiency

A model is sufficient for the focal concentration only when its observed conditional residual does not exceed that model's simulated upper 95% residual bound.

Residual reduction without crossing the null bound is partial explanation, not full mechanism closure.

## Secondary biological check

Only after the concentration mechanism result is frozen, the same cross-fitted hydrology variables may be used to test the already-existing direct strong-chorus transition endpoint (dry CI=0 to wet CI>=2).

This secondary test asks whether the hydrology variables that explain spatial allocation also predict reproductive acoustic state switching.

It cannot redefine or rescue the primary concentration mechanism.

## Interpretation boundary

Hydrology effects concern reproductive acoustic activity and spatial breeding-site expression.

They do not establish reproductive success, larval production, recruitment or fitness.
