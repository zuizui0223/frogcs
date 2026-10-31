# Speculative danger-amplification competitor: S-facilitated D→F risk (2026-10-31)

## Clarifying the hypothesis

This **post-observation** mechanism is NOT the existing frog behavioral-risk refuge (which suppresses some predation) and it is NOT the experimentally documented negative indirect Kishida 2009 D→S→F path. Here the hypothetical pathway is **presence of aquatic salamanders S increases dragonfly D→tadpole F encounter/attack**, e.g. via disturbed tadpole movements or refuge sharing. Neither field occurrence nor attack rate is demonstrated in the existing NAAMP data. Treat the pathway as an *explicit exploratory competitor*, not a literature-established fact.

The original frozen `stage_network_extension_20261029.py` must not change. A separate `stage_network_s_facilitated_danger_20261031.py` fork and copied annual summary are used only for this hypothetical test.

**Equation (per tadpole hazard, before prey-density litter response):**

`H_DF,new = H_DF,original × [b + a × S/(1+S)]`

where S is the actual **synthetic season-varying aquatic salamander cohort density** (not SDM habitat suitability); `b` is basal D risk fraction and `a` the S-facilitation strength. This multiplier is applied only to the D→F attack pathway, **not** to S→F, D→S, S→D or the frog→dragonfly reversal edge.

## Fixed before looking at these new simulation results

Exactly 24 structural scenarios from the original NAAMP POM (3 ontogenetic arrival/order contexts × 2 shared-handling assumptions × risk-refuge off/on × reversal off/on), 2 vegetation states × 9 S sources × 9 D sources, unchanged 80-year annual recurrence/dt=.25, original mature-lag values and baseline rates. No ABC posterior, no observational slope fitting.

Three whole factorial conditions, each applied to **all 24 cases**, with no result-based parameter tuning:
- `neutral`: `a=0`, `b=1.0`. This MUST numerically reproduce the source 24-case `F_B, F_fraction` at 1e-8 and `F_B_sd` at 1e-7. Otherwise stop the full analysis.
- `facilitation_moderate`: `a=1.0`, `b=0.5`. At S=0, D→F hazard is halved; at larger S it increases.
- `facilitation_strong`: `a=2.5`, `b=0.15`. At S=0, D→F hazard is 15% of the original; at higher S, it increases with S. These values are dimensionless **hypothetical contrasts**, not field-calibrated attack ratios.

Primary outcome: observed **direction-only**, robust-sign and low-S ternary-category POM score; secondary: full six-dimensional quantitative POM distance and the unused four observed patterns, using identical 4,248-site distributions and observed-only bootstrap uncertainty as previous PR #146. Keep both SDM backgrounds and the complete candidate set. Describe risk-refuge and S-facilitation as distinct processes that can co-occur in these fixed scenarios, not automatically as the same plant effect.

Statistical warning: This structural alternative was introduced **because earlier models failed** low-S ≈0 with high-S negative; even exact matching here would be a **post-hoc feasibility demonstration**, not independent evidence the pathway exists. Never use an ABC posterior from these three manually selected parameter states. If neither improves joint match / unseen patterns, retain the negative finding. If an artificial amplification solution improves direction fit, it becomes a testable field hypothesis about salamander–tadpole behavior/dragonfly attack rates and must be checked independently.

The original 132 frozen models, both successful POM/ABC pilot runs and process-rate ensemble remain untouched; new files live exclusively under this PR #146's hypothesis branch.
