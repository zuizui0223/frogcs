# Source-verified 3,600-model joint ABC–POM outcome (2026-11-01)

## Bottom line

**The previously reported 158 fixed-rate four-sign matches reproduce exactly, but their apparent structural requirement and timing winner are not robust to jointly sampled nuisance rates.** In the 20,000 independent seeded structure×stage×rate prior draws, 787 (3.935%, Wilson 95% Monte Carlo interval 3.674–4.213%) generated the four model-native signs. **269 accepted proposals explicitly lacked salamander→dragonfly-nymph predation** (edge_SD=0), disproving the narrower assertion that this edge is *necessary within the sampled model space*.

This does NOT identify a field mechanism or an empirical Bayesian posterior. These are deterministic aquatic F_B pattern-generating models with synthetic parameter priors; geographic suitability, adult calls, actual predator abundances and the observation process are not fitted.

## Source authenticity and execution receipts

- Frozen main commit: 5e2f0a87c639df373fa2700b29403d2ab417a1cc.
- Successful source and full simulation workflow: [Actions #41260789313](https://github.com/zuizui0223/frogcs/actions/runs/41260789313); all eight simulation shards and final complete-draw aggregation passed.
- Distinct source full-screen files: 38 archived gzip chunks, 194,400 cells, 10,800 models×contexts; exactly 18 cells per unit, all eight corners intact.
- Fixed-screen log(F_B) targets: 158 four-sign and 275 OS−/OV−/SV+ three-sign successes (out of 10,800). Stage-context counts: 14, 8, 136 out of 3,600, respectively. This independently confirms the user-supplied counts.
- Four independent tests passed: known factorial algebra, null rejection, seed/shard invariance, original-kernel integration.
- ABC proposal count 20,000; 8 corners/proposal=160,000 genuine original 40-year seasonal/annual scenario evaluations at dt=0.5; **20,000 exact unique draw IDs** verified during aggregation.
- Main canonical models actually sampled: 3,582 of 3,600; distinct IDs among accepted: 638. Unsampled 18 IDs are not counted as structurally impossible.
- Downloadable run artifacts include all 20,000 raw proposal records, accepted-draw parameter vectors, model acceptance and conditional-axis acceptance tables.

## Genuine joint ABC–POM outcome

Precommitted priors: equal probability among original 3,600 model IDs and three original stage-duration contexts; independent discrete-uniform attack {0.5,1.5,3}, rho {0.25,0.5,0.75}, conversion {2,4,8}, vegetation strength {0.5,1.0}, refuge-order {S,equal,D}, size gate {none,0.5}; seed=20261101.

| Target and sensitivity | Accepted / proposed | Acceptance |
|---|---:|---:|
| Primary log(F_B): OS−, OV−, SV+, OSV+ | **787 / 20,000** | **3.935%** |
| Raw F_B instead of log(F_B) | 573 / 20,000 | 2.865% |
| Primary log signs plus minimum F and S survival ≥5% | 428 / 20,000 | 2.140% |

Raw and log matches need not coincide: 454 proposals meet both. The different screens are **sensitivity results**, not post hoc opportunities to change the original acceptance definition.

### Directional edge: prior claims of necessity fail

| Edge_SD S→D | Accepted / proposed | Conditional acceptance (Wilson 95% MC interval) |
|---|---:|---:|
| OFF | **269 / 6,608** | **4.071%** (3.620–4.575%) |
| ON | 518 / 13,392 | 3.868% (3.554–4.208%) |

The 269 exact accepted draws with S→D OFF are direct constructive counterexamples to necessity under these model-native priors. The tiny marginal percentage difference is **not** evidence that the edge is causally harmful; different canonical structures/other features co-vary across catalog groups. Actual matched edge ablation is needed for isolated effect interpretation.

D→S (edge_DS) is compatible in 677/16,101 = 4.205% of ON draws versus 110/3,899 = 2.821% of OFF draws. This is a prior-conditional structural association, not field evidence of dragonflies consuming salamanders.

### Developmental timing switches after integrating nuisance rates

| Main context | Four-sign accepted / proposed | Conditional acceptance |
|---|---:|---:|
| 0: S arrives day 40, D aquatic 40 days | 308 / 6,501 | **4.738%** (4.248–5.281%) |
| 1: S arrives day 40, D aquatic 60 days | 267 / 6,827 | 3.911% (3.476–4.397%) |
| 2: S arrives day 0, D aquatic 60 days | 212 / 6,672 | 3.178% (2.783–3.626%) |

At the original fixed-rate screen, context 2 dominated (136/3,600 versus 14 and 8). This does not hold for the **specified independent nuisance prior**. Consequently, the fixed-rate stage winner must not be described as universal.

The prior-averaged edge×stage pattern is highly nonadditive:

| Context | S→D OFF accepted / proposed (rate) | S→D ON accepted / proposed (rate) |
|---|---:|---:|
| 0 | 112/2,171 (5.159%) | 196/4,330 (4.527%) |
| 1 | 132/2,288 (5.769%) | 135/4,539 (2.974%) |
| 2 | 25/2,149 (1.163%) | 187/4,523 (4.134%) |

This suggests timing-dependent compatibility **within the weighted model catalog**: S→D ON is enriched under early S arrival but not late S arrival. It is **not a same-parameter, same-other-edges ablation**, so cannot by itself attribute a causal reversal to the isolated edge.

### Role of other vegetation functions and rates (marginal, not causal)

| Catalog feature | OFF acceptance | ON acceptance | Descriptive implication |
|---|---:|---:|---|
| Frog shelter from salamander, cover_SF | 3.785% | 4.034% | Small change; not required |
| Frog shelter from dragonfly, cover_DF | 4.432% | 2.940% | Lower compatibility with ON |
| Salamander shelter from dragonfly, cover_DS | 3.348% | 4.806% | Higher compatibility with ON |
| Vegetation supports dragonfly→frog feeding, support_DF | 2.518% | 5.332% | Higher compatibility with ON |
| Vegetation-dependent litter/type-III-like response | 4.036% | 3.737% | Not necessary |
| Adult frog→dragonfly reversal, reverse | 4.031% | 3.838% | No strong directional preference |

The nuisance-rate prior matters at least as much as many of these catalog features: attack 0.5/1.5/3.0 gives **6.48%/3.32%/2.06%** acceptance; annual rho 0.25/0.50/0.75 gives **1.60%/3.97%/6.20%**; conversion 2/4/8 gives **1.96%/4.09%/5.74%**. These rates are artificial choices, not field-calibrated parameter distributions.

## Original finalist IDs: not estimable as a reliable ranking

Under random catalogue draws, ID 780 was sampled twice (one accepted), 1479 four times (one accepted), and 586 six times (none accepted). These extremely small denominators **cannot rank the three IDs**. The valid primary result is structural-axis and stage-conditional compatibility, not a single winner. The old 20×24 finalist exercise was preselected by main's different criterion.

## Interpretation and publication gate

A defensible model-native claim is:

> Stage arrangement, vegetation function and predator pathway jointly constrain whether a positive third-order frog–odonate–caudate pattern can emerge, but no single trophic edge or developmental order is necessary across the tested synthetic rate distribution.

The tempting stronger statement, "vegetation-mediated S↔D predation causes the observed chorus pattern," is **NOT supported**. Mapping aquatic cohort dynamics into species-specific adult-call probabilities and matching the magnitudes/uncertainties of six real site-scale patterns remains uncompleted. The 0/132 site-mapped candidate failure in the separate exploratory work must not be hidden by these directional matches.

Limitations requiring preservation: catalog prior multiplicities, three prespecified stage contexts (not all conceivable orderings), independent synthetic nuisance distributions, deterministic dynamics, four signs ignoring magnitude, and post-hoc comparison with the fixed-rate screen. Wilson intervals quantify *prior Monte Carlo sampling error*, not ecological uncertainty.

**Canonical code and detailed numeric tables:** research/scripts/abc_pom_main3600.py and the archived full output artifacts from [Actions #41260789313](https://github.com/zuizui0223/frogcs/actions/runs/41260789313). Main and original results remain immutable.
