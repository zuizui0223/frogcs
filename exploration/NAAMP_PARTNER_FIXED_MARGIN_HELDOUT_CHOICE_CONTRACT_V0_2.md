# Correction to fixed-margin partner-choice route holdout (v0.2, 2026-10-22)

This replaces only the **nested routing of original first-order NWI weights** in `exploration/NAAMP_PARTNER_FIXED_MARGIN_HELDOUT_CHOICE_CONTRACT_2026_10_22.md`. All focal species, null variables, historical SiteID score, primary/secondary endpoints, regularization, training/test route folds, gates and decision criteria remain unchanged.

## Why correction was necessary before empirical readback

The first implementation computed out-of-fold NWI first-order offsets for **every** route-run. That is valid for a fixed external evaluation of an already learned NWI model, but **not** for the new second-stage training on the opposite route fold: stage-2 training rows in fold A would have NWI offsets learned on fold B (the stage-2 evaluation rows), and vice versa. That would introduce indirect route-label leakage into second-stage training. Results from the first workflow commit `fbcf5ad1cbc938724e3863f57b108fdb23edd432` / Actions **39712455457** must **not** be interpreted as held-out partner prediction, whether the job succeeds or fails.

## Correct two-stage nested fold rule

For evaluation on fold B:
- source first-order NWI wetland+PEM coefficients **trained exclusively on fold A**, frozen earlier in workflow 39516056663;
- fit partner coefficients on fold-A route-runs using that *same* fold-A trained NWI offset (in-sample baseline for model fitting);
- apply both fitted first-order NWI and fitted partner coefficients to fold B, never using coefficients trained on B.

For evaluation on fold A, reverse A/B.

Prior physical-SiteID scores are always constructed from **strictly earlier survey years** in the same seasonal stratum, with no same-year target calling data. Those history scores can use earlier-year records from the same geographic route as the target but cannot use target-year records.

Each eligible exact row-swap event therefore carries two frozen environmental offset variants:
1. `train_offset_from_own_fold` for stage-2 partner fitting when the source route is in the training fold;
2. `test_offset_from_opposite_fold` for stage-2 out-of-route evaluation.

**No coefficient from the evaluation route fold is allowed in either model's training data.**

## Temporal diagnostic limitation

The named early→late check retains previously frozen NWI source coefficients trained across the full 2001–2015 record. It is explicitly a descriptive late-year transfer of partner coefficients **and not independent chronological validation**, and may not override the nested geographic route test.

## All other conditions unchanged

Read v0.1 for the original scientific hypothesis, thresholds (≥60 runs, ≥25 routes, ≥20 per fold), model stages, exact swap conditioning, generic nonfocal richness control, ridge=3, bounds=±3, 2,000 route-block bootstrap and BH adjustment across the fixed two partner trios. Results must not be promoted as direct frog–frog interaction or changed in RC6/JAE.
