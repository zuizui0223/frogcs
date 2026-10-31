# Primary objective — explain the NAAMP macro pattern, not showcase ABM/PDE

Frozen before the new scenario-selection experiment (2026-10-31). This redirects PR #146 from a method-first demonstration to an **observed-pattern-first selection test**. Prior 20-year spatial ABM/PDE experiments are explicitly secondary mechanistic diagnostics, never candidate-selection evidence.

## Existing model that best matches the present evidence

Choose the existing *deterministic stage-structured seasonal cohort + annual delayed recruitment model*, which already supports multi-generational effects, stage ordering, three trophic guilds, juvenile/adult dragonfly emergence and the frog→emerging dragonfly reversal option. It is currently better matched to the available data than an ABM or spatial PDE because no same-pond stage counts, immigration routes or agent behaviors are observed in the 4,248 NAAMP sites. ABM may later test stochastic extinction; PDE may later test patch-scale dispersal **only where measurement permits**.

## Fixed observational target and candidate set

Source cohort: 4,248 NAAMP sites, 63,180 completed visits (2001–2015), completed-survey strong-call count as the **only primary outcome**. Source covariates are original SDM-based **odonate/pond-breeding caudate habitat suitability**, EarthEnv flooded-vegetation consensus within 3 km, survey controls, bioclimate/water/herbaceous cover and geography. This is not matched pond density or pond refuge.

Reuse *existing, completed 80-year synthetic model surfaces*, last 20-year averages, from `research/results/literature_extension_20261029/primary_{0,1}_{dynamic,frozen}_cells.csv.gz`; **do not retune predator attack, maturation or recruitment to observed calls**.

Pre-fixed factorial **24 scenarios**:
- Stage/time context: `original`, `D_first_S_overtakes`, `S_first_D_overtakes` (synthetic relative arrival/growth)
- Saturation/processing: `baseline`, `shared_both` (existing source naming)
- Behavioral refuge: `risk=False/True`
- Reciprocal frog predation on emerging dragonflies: `edge=dynamic` (off), `edge=frog_reverse` (on)

All other trophic edges retain their original source configuration; no hidden implicit selection on prior sign matching. Each scenario's `F_B` surface has V=0/1 and a 9×9 S/D source grid. Compare **both** uniform and target-group SDM backgrounds with the same mapping from *predictor ranks* to source-grid bins and observed landscape vegetation detected/not detected to model V. This mapping is hypothetical; no equivalence between SDM suitability and predator density is claimed.

## Observation operator and strict selection

- **Scenario model**: `strong-call count / completed visits ~ binomial(logit^-1[site controls + O + S + V + b * log(F_B scenario)])`. Coefficients and `b` are estimated on training blocks only with fixed ridge regularization (`ridge=10`), not calibrated from independent acoustic-density data. The ecological dynamics used to produce `F_B` are **never fitted** to calls.
- **Competing environmental nulls**: same site controls + O/S/V main effects (`env_additive`), and same + OS/OV/SV/OSV interactions (`env_interactions`). Both must be reported. A mechanism must improve over the better predictor-only environmental null; merely beating a weak one does not qualify.
- 5 spatially blocked **outer** folds (2° route-centroid clusters). For each outer training set, inner *3-way* spatial-block CV chooses the best among the 24 mechanism surfaces and the better of the two environmental nulls **without inspecting outer-fold outcomes**. Then retrain the chosen models on outer training blocks and score the held-out outer fold. Store each fold's selected scenario, positive-vegetation support, held-out probabilities and all failures.
- Primary: mean negative binomial log score **per completed visit** and selected-minus-null paired spatial-block bootstrap (999 draws, conditional on fixed fitted predictions). Positive gain means selected mechanism predicts better. Report both backgrounds and full score intervals. All-candidate outer evaluations for diagnostics are explicitly exploratory and not winner validation.
- Secondary: measured vs held-out predicted **OV** and other OS/SV/OSV contrasts using the same response and covariate estimator, with uncertainties. OV is the most stable observed term. Weak/unstable OS and SV are **not required to have an imposed sign**.
- If there is no predictive gain in both backgrounds relative to the competitively selected null, say **NO EMPIRICALLY SUPPORTED WINNER**, not the first configuration with a matching sign.

## Observational constraints and future steps

Strong adult calling is not proportional to larval density by a known calibrated coefficient. NAAMP site data lack predator density, local pond plant structure, age/size overlap, exact adult frog capture events and eDNA stages. A success would therefore imply only **conditional predictive compatibility under the frozen proxy→model mapping**, not field causal identification. Later methylation-eDNA and independent field manipulations are distinct validation studies. Do not refit the environmental proxy→density mapping to force agreement, choose favorable SDM background after viewing results or claim that simulation counts are likelihoods.

This protocol is **post-PR #145**, not an independent confirmatory holdout against prior use of NAAMP; nested folds protect new within-dataset scenario selection against leakage, but prior analyses on this cohort still matter.

Success criterion for this PR: a reproducible nested-selection result with complete scores and explicit no-winner outcome if warranted. ABM/PDE implementations and their synthetic exploratory results remain separate secondary appendices.
