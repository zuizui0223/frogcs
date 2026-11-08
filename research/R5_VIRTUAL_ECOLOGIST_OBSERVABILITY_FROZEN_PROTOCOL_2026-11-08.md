# R5 | Virtual ecologist: structural identifiability versus observation power

**PRE-OUTCOME FREEZE, 8 November 2026 (JST).** This file is the scientific-design authority written before inspecting ANY R5 synthetic outcome. Only one last, bounded R5 diagnostic is authorized; source findings G4–G18 and the frozen Ecology Letters submission handoff are not retuned.

## Question and competing hypotheses

Could a true source-defined vegetation–odonate–caudate model-cohort process fail the spatially held-out NAAMP-style adult acoustic test because of the observation chain? Distinguish (A) failure that persists even under a noiseless observation (**structural non-identifiability**), (B) conditional recovery loss after simulating the measurement process (**power loss**), and (C) adequate recovery under field-style proxies (original failure NOT explained by these assumptions). Show positive and negative controls.

Zurell et al. (2010), Oikos 119:622–635, DOI:10.1111/j.1600-0706.2009.18284.x, provide the virtual ecologist framework. Any truth is that of the *specified simulator*, not the original wild ponds.

## Frozen sources (fail closed)

1. G4 original 256 independent legal food-web backgrounds × 3 developmental contexts × eight predictor vertices, both-on (11) and both-off (00), archived original verified model-source G4 artifact, source run 42173236906. No model-source refit, rate selection, structure choice or favorable cherry-picking.
2. NAAMP/G14 original 4,248 sites, 63,180 completed surveys, 36,554 strong-call events, 506 flooded-vegetation-positive landscape sites, 432 routes, 56 geographic blocks and fixed five spatial folds. G14 original site and visit SHA256 requirements must pass. SDM backgrounds uniform and target-group both retained as **alternative uncalibrated predator-suitability proxies**.
3. G4 trilinear interpolation and G5 model 11/00 source coefficients, existing G14/R1 covariate code and original 56-block holdout NLL. Exact 8-corner source interpolation lies within the unrestricted eight-term polynomial span 1,O,S,V,OS,OV,SV,OSV. This is a **structural-identifiability failure** against the saturated empirical interaction model regardless of n, not a low-power effect.
4. G18 independent original 1,054 visits × 13 species observations have 45/860 same-survey larval detections with calling vs 125/12,842 without, but do NOT calibrate log larval cohort → adult calling probability, timing lag, sensitivity, detection ICC, or pooled pseudo-R². DO NOT equate 5.23% larval detection with 5% explained calling variance. Real measured predator density and pond vegetation are also absent.
5. Field data contain neither salamander arrival day nor aquatic duration. The P1 arrival×duration interaction therefore cannot be independently identified by NAAMP site covariates, even with noiseless simulation of recorded calling.

## Prospective observer experiment, never tuned to obtain failure

Use source means only, all original sites and observed site-specific n completed visits. For each of two conditional **truth rank worlds** (uniform-based or target-group-based; neither is claimed actual density), and truth arm 11 vs 00, compute each original eight-corner model mean log frog aquatic-cohort surface with trilinear interpolation. Separate source-model truth from the observer's SDM background.

- **Observed conditional environmental baseline:** fit existing flexible additive original R1 acoustic regression once to the actual k/n under each of two SDM backgrounds, then FIX this baseline as shared environment in all virtual worlds; recognize its possible confounding with nature. A simulated world is not a field fit or independent evidence for mechanism.
- **Calling operator:** true site event probability is expit(logit(fixed environmental p0) + gamma × standardized source *interaction* component); generate binomial strong-call k_i on exact original n_i. Gamma is hypothetical, not measured from G18.
- **Fixed gamma values:** 0 (negative control), 0.25 (weak link), 1.00 (strong link). Report them as illustration, never as empirically inferred observation error.
- **O/S:** evaluate both observed SDM ranks against each alternative virtual-truth rank background. Do not choose the background yielding a favorable answer.
- **Vegetation:** pond V equals mapped landscape V (reference) or a frozen response-blind 25%-site-index mismatched V truth (hypothetical illustration, **not an estimated true V error**). Hold real observed proxy V constant in the analysis. Include 00 and 11 source arms, never drop the unfavorable one.
- **Sampling:** identical original 4,248 site opportunities, fixed 56 geographic blocks/five folds, with at least 100 simulation replicates per crossed scenario, master seed 20261108 and hash-stable masks; original frozen source coefficients and the complete successful/failed replicate roster must be retained. No R5 output may be inspected to choose design values. If full scenarios cannot finish, report INCOMPLETE rather than a positive subset.
- **Models scored on every replicate:** original G5 11 source-interaction predictor with train-only nonnegative coefficient, original G5 00, flexible additive environmental baseline, and unrestricted 4 interaction regression. All fit and predict out of the original spatial folds. Preserve R1/G14 held-out binomial NLL and both backgrounds.
- **Primary recovery criterion:** heldout 11 NLL must be smaller than both 00 and flexible additive, with positive lower 95% from 999 original-56-block paired resamples; compare recovery frequencies and binomial uncertainty across proxy/noise conditions. A saturated interaction model can fit the same shape and is **not a unique mechanism discriminator**.
- **Negative control:** gamma=0 must be run with original folds, returning false-positive rate; if inflated, the design is invalid.
- **Positive oracle control:** with exact latent log-cohort source and known truth, at least one original model 11 vs 00 separation in the original geometry and no measurement noise must be demonstrable; otherwise attribute subsequent failure to source observational equivalence, not to acoustic noise.
- **80%-power site design:** no definite numeric number of ponds may be claimed without calibrated local pond V, stage-detected predators and a cohort-to-call observation model. A purely conditional scenario-specific 80%-power frontier may be shown only with explicit site/block scaling and uncertainty.

## Hard decision and no-excuse rule

R5 supports *conditional observability loss* only if the oracle can distinguish source truth, the full observed-style proxy chain reduces recovery with the frozen parameters, the negative-control false positive is controlled, and ALL source/fold/count checks pass. If field-style proxies recover signals well, the original negative G5/G14 result must remain unexplained by the tested noise scenarios. If oracle fails, classify as structural/source degeneracy. Do not increase noise after seeing results to manufacture non-detection.

Field mechanism identification remains unproven under ANY result; virtual recovery rates are not posterior probabilities of a wild trophic mechanism. Claim only hypothetical power conditional on observation strengths. The original SDM-background failure and G17's failed original numerical replay are permanently retained.

## Paper and closure

Only after a complete audited R5 may one cautionary sentence go in the *Ecology Letters* Discussion; keep full R5 assumptions/results in SI. No extra manuscript figure unless replacing an existing one without exceeding journal limits, and preserve the 5,000-word Letter limit. Author approval, project archive DOI, licensing and actual journal submission are still separate user-author gates. **No G19 or other exploratory analysis after this test.**
