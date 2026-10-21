# Same-survey partner-specific frog allocation: stop microtemperature, sound masking and survey-order null

**Post-hoc, user-directed additional challenge**, frozen 2026-10-21. Does not reopen the JAE RC6 science/submission.

## Existing result
Previous [same-survey result 39597933440](https://github.com/zuizui0223/frogcs/actions/runs/39597933440) found a shared `Lithobates clamitans` with `L. catesbeianus` positive residual and either `Anaxyrus fowleri` or `Hyla versicolor` negative residual on exactly the same ten-stop route-run after NWI 250m PEM, fixed taxon incidence totals, and fixed stop richness.
- P against A. fowleri: 538 CI1–3 qualifying runs, D = +0.05405 (95% route CI +0.04516..+0.06295).
- P against H. versicolor: 744 CI1–3 qualifying runs, D = +0.04541 (+0.03911..+0.05170).
- Strong CI2–3 is a fixed secondary, in which the H. versicolor *negative edge* was not independently supported.

The central ecological question is whether observed partner identity matters even if the acoustic opportunity/detection environment differs among stops within a route-night.

## Frozen data
Exactly the original source-signed 6,236 NWI-covered, complete ten-stop/temperature/noise USGS NAAMP runs. Original fixed 3,659 CI1–3 and 1,766 CI2–3 checkerboard reference matrices, same species identity lists. Original source-blind NWI polygons and original cross-fitted wetland+PEM first-order species coefficients from Actions 39516056663. No new wetlands, species, radius, run membership, or outcome selection.

Stop covariates recorded **on the same survey run** in Stops.csv:
- local air-temperature departure from mean ten-stop air temperature, per **5°C**;
- sound masking `MassNoiseIndex` (0–4), or existing deterministic `Noise` fallback, centered within the route-run, per **2 index points**;
- visited stop sequence number centered/scaled as (StopNumber−5.5)/4.5.

These are contemporaneous observation/site proxies; sound masking and stop order can reflect detection and survey practice. They are **not time-matched water-level/predator records or a causal explanation**.

## Competing models
- M0: previous route-held-out species×mapped wetland + PEM fixed-k conditional-logit location weights, exactly imported unchanged (2 coefficients, NWI 250m fractions ×10).
- M1: species×(M0 terms + three stop environmental/observational covariates). Train on opposite deterministic route fold only with exact fixed-k location likelihood and ridge λ=3 and beta bounds [−3,3]. All available taxon units train if at least 30 informative route-runs from >=12 routes; if a species cannot estimate M1, use **M0+three zeros** without changing other taxon/stop margins.
- Do **not** add other covariates or rescale after outcomes. No taxon preselection from previous PEM q tests.

Test M1 generalization: per-species×run conditional log-likelihood on held-out geographic routes among all 6,236 NWI-covered runs with k∈[1,9]; M1−M0 site-placement gain, route-block bootstrap 2,000 replicates seed 2840310, reported separately for CI1–3 and CI2–3. Improvement not required to test sensitivity, but if M1 loses in held-out prediction, classify any biological claim of controls `predictively_unreliable`.

## Same-survey partner comparison
Exactly the two frozen three-species sets and the primary/secondary thresholds from the previous successful result (no choosing replacement pairs).

For every originally qualifying same-run trio, recompute `e(C,P)`, `e(C,N)`, paired contrast `D=e(C,P)-e(C,N)` under M0 and M1. Both nulls: fixed-row/fixed-column weighted Curveball, 199 draws per matrix, 40×n_taxa burn-in, 8×n_taxa thinning, deterministic model-specific seed 2840311. Check observed C-score and all simulated row/column margins. Retain exactly prior 538/744 CI1–3 and 72/171 CI2–3 qualifying trio sizes; abort on drift.

For M1, report route-clustered CIs of both pair residuals and D. BH correction of D over both fixed CI1–3 trios. Report geographic fold signs and early (2001–2009)/late (2010–2015) descriptive splits; source first-order coefficients span both periods so **not independent temporal validation**. Report D_M1−D_M0 with a route-clustered CI on identical runs. A confirmed stronger observational partner-specific contrast requires:
1. positive M1 D route CI lower bound >0 and BH q<.05;
2. M1 e(C,P) 95% CI lower bound >0 AND M1 e(C,N) upper bound <0;
3. both route folds D positive;
4. M1 held-out log-score gain not demonstrably negative (95% interval not wholly below zero);
5. zero mixed-up study-membership/marginal-constraint violations.
If any condition fails, classify `weak_context_adjustment_evidence` or `unresolved`, **not proof of social or competitive interaction**.

## Limits
NWI vegetation not necessarily contemporaneous with 2001–2015 frogs; stop temperature/noise are measured concurrently not pre-assigned. Ten stops are visited sequentially and do not prove frogs communicated. Crossfit across routes does not remove latent species-specific habitat, prior site history, phylogenetic/phenological population differences, substrate, fish/invertebrate predator abundance, water temperature, acoustic masking mismeasurement, or historical changes.

Keep all new outputs in exploration branch, no modifications to `paper/`, `submission/` or RC6 evidence.
