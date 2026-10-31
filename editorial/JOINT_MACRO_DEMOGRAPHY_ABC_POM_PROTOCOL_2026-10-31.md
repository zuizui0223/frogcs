# One-pipeline macroecology → mechanism → demographic ABC–POM (2026-10-31)

**New scientific integration specification for the SINGLE frogcs macro-first paper.** The historical separate "mechanism catalog" and "dispersal/population boundary" results become one mechanistic result, tested at two successively stronger levels. This is an execution specification, NOT a claim that a common field-conditioned posterior exists already.

## 1. Research question

Which stage-structured freshwater trophic networks can generate the OBSERVED caudate-conditioned odonate–frog calling pattern, and what would the SAME network/rate parameters predict about local reoccupation and long-run persistence?

POM here = pattern-oriented modelling. ABC = approximate Bayesian computation. The core distinction is **adequacy to real-site observations** versus **model-native ability to produce idealized directional signs**.

## 2. One ordered inference, not two independent results

**Gate A — actual 4,248-site pattern adequacy.** For one common biological network m and process-rate vector θ, use original odonate O / pond-caudate S modelled suitability, EarthEnv vegetation V, and site calling response to calculate the same SIX jointly observed statistics on the same actual NAAMP sites, separately for uniform and target-group background:
- OS, OV, SV, OSV in the shared global-rank, unadjusted regression.
- correlation(O, response) in low-S and high-S *fixed masks*, with source global ranking.
- Quantify covariance and 95% marginal intervals through 56 geographic blocks, 999 block resamples and source shrinkage. Use a covariance-aware distance for POM model comparison. The six marginal 95% bands are descriptive adequacy, NOT one formal 95% joint p-value.
- Hold out O–response in V-zero vs V-positive locations and within-route OS/OV for separate checks; these use the SAME observational programme and are not independent external datasets.

**Critical estimand warning:** the site-POM global-rank low/high S correlation from the actual source is +0.0321/−0.2364 (uniform); earlier source-specific low/high correlation +0.101/−0.284 is a DIFFERENT local rank estimand. Do not mix one observed target with the other model output.

**Gate B — ABC on EXACTLY the same biological simulation.** Rather than declaring any structure with the idealized model-native 4 signs to have fitted field observations, simulate one common source library with:
- canonical model class, source plant role, stage onset and growth, active directed predator edges, model handling and risk;
- original 120-day seasonal trophic kernel +80-year lagged cohort recurrence;
- hypothetical biological rate θ: attack scale, S/D growth multipliers, rho×conversion annual local recruitment, juvenile/adult frog survival and maturation delay;
- exact O/S suitability-to-source-supply rank mapping and a *fixed positive monotonic rank* observation diagnostic for F_B→adult calling fraction. The rank link is an illustrative proxy, NOT independent calibration for larval-to-adult calling.
- Actual SAME θ and source hypothesis must emit the 4,248-site six fitted statistics. Never perform ABC on model-native 2×2×2 signs then call it a site-level field posterior.

The 12 legal plant roles collapse to 108 canonical structural classes in the previous library after merging redundant risk states. Equal-class, equal-plant-role and main-catalogue-frequency weights produce different preferred mechanisms. Account for duplicate 80-year F_B responses, paired reverse-on/off states and conditional structural priors, rather than counting every 3,600 original catalogue entry as a separate field prior. Use biological source rate draws with transparent, potentially hypothetical priors and model-recovery/confusion diagnostics.

**Gate C — downstream long-run predictions, NOT another pseudo-observation likelihood.** For every actual m,θ source row retained by Gate A/B, pass SAME input and original 120-day +80-year biological source into the finite-N 8-ring-patch model:
- annual movement OFF versus both surviving and recruited cohorts at the same specified rate;
- year80 occupied F patches, exact zero→positive annual reoccupation, three-year persistent return and right-censoring;
- synthetic count scale q, with q3/12 as core sensitivity; q6/q9 are explicitly post-result exploratory; migration and external immigration values kept visible;
- compute long-run endpoint distribution conditional on the *site-adequate* m,θ set, with true model θ matching and prior weights. NAAMP contains NO observed 80-year F cohort occupancy, so do not add those model outcomes to ABC as independently fitted observed targets.

If no real-site source model is adequate, the final status is NO_FIELD_CONDITIONED_LONG_RUN_PREDICTIONS. Retain conditional simulations as informative, original model-native counterfactuals, NOT a field-posterior prediction.

## 3. Critical existing evidence, as checked before consolidation

**Site-mapped POM:** 132 archived fixed-rate candidates /104 exact output-equivalence groups on actual 4,248 NAAMP locations, with zero cases fitting all six observed patterns within individual 95% spatial-block intervals in BOTH backgrounds. Best uniform case_005 (distance10.8269; 0/6 patterns within bands); best target-group case_036 (distance8.2624; 2/6). Most relevant mismatch: candidate odonate–calling correlation in LOW caudate-suitability sites is far too negative, despite selected ODONATA×vegetation signs. Source: research/MACRO_POM_132_ABC_RESULTS_2026-10-31.md and compact catalog132 results in the PR146 branch.

**Four-sign model-native ABC:** 12 structures ×256 hypothetical rate draws ×2 paired reverse predator states =6,144 real original 80-year population source runs. The original-timing/baseline-riskOFF case matches model-native four-sign directions in 65/256 independent rate draws (25.39%). This is a prior-conditional feasibility result, not observational site-POM success and not a posterior over actual field predator mechanisms. The expanded plant-role ABC winner depends on structural prior. Source: PR146 research/MODEL_NATIVE_GENUINE_80Y_ABC_RF_RESULT_2026-10-31.md and research/VEGETATION_MAIN_CANONICAL_108_PRIOR_RESULT_2026-10-31.md.

**Model-native long-run finite-N:** in a selected high-local-recruitment source setting, S-larva→F-larva predation was necessary/sufficient for strict growth-dependent movement-effect sign reversal under q3. Across q3/6/9/12, model-input plant settings with the strict reversal are 2/2, 1/2, 0/2, 0/2. q is a synthetic count-per-density ratio; the source biological-rate switch failed in three of four prior process vectors. Source: PR153 and PR155 genuine original 80-year source runs and audit.

**NO MATCHED JOINT LIBRARY:** site-POM 132 frozen model surfaces, original model-native 12/108 structural classes with 256 rate draws, and the selected finite-N q experiments are NOT currently audited to share one site-level emission and the same θ. DO NOT join those old result rows as if each is one biological configuration. The number of jointly field-calibrated process models is NOT computed, not literally 0 over the unmatched libraries.

## 4. Unified main figure and manuscript result

Rename the two former model Results sections into ONE section:

**"Pattern-oriented model assessment reveals conditional mechanisms but no jointly validated demographic explanation."**

One main Fig3 with (a) six observed site patterns & uncertainty; (b) the 132-case POM failure and key O×V vs high-S-low-S contradiction; (c) distinct genuine model-native ABC prior support / canonical role sensitivity; (d) q-dependent original-model finite-N movement consequences with a dashed, **not yet validated** field observation-to-process link.

This is a model assessment and explicit identification boundary, rather than a claim that the field pattern's causal trophic route was found. Figures1 and2 remain the MACRO third-guild association and habitat/site history. All rate axes, stability, failed candidates, 12-seed source diagnostics and model details go to ONE Supplement.

## 5. Executable next step / failure gates

1. Version an audit of the three existing results: compact source 132-case site-POM summary, 12-class genuine model-native 256-rate rejection ABC and q3/q6/q9/q12 count-scale outcomes. It must validate each result without inventing cross-library source IDs or joint ABC weights.
2. To perform a genuine one-model ABC–POM, generate the common **m,θ,plant,stage,rate,site-predictor** prior predictive reference first; use the same source rate/site-emission assumptions to produce demographic outcomes.
3. Demand absolute site-level adequacy (not only closest Mahalanobis distance) and held-out within-route/background checks BEFORE interpreting model choice, and report NO ADEQUATE MODEL if the gate fails.
4. No extra arbitrary rank-noise or observation mapping may be tuned post hoc to turn the observed macro three-way into a favorable model sign. Only real common-pond stage/acoustic data could calibrate a biological observation model.

**Scope/status:** The author selected ONE macro-first paper, and RC6 rainfall chorus clustering is historical Introduction motivation only. Source models and main paper remain untouched by this protocol. A true joint field-conditioned ABC posterior and corresponding demographic posterior predictions are NOT yet available.
