# P1 follow-up: explain when the two vegetation functions benefit frogs

## Status and question

This is an explicitly **post-hoc decomposition of the completed P1 factorial**. Its four timing means and endpoints were already known when this plan was written. It is not a preregistered new experiment, a new field sample, or an attempt to change the G7 decision.

Question: in the original source-matched 256 food-web backgrounds, how do the isolated refuge increment, isolated odonate-feeding-support increment, and their nonadditivity account for the shift in the net two-function effect from late/short to early/long salamander development?

## Fixed inputs and complete scope

- Source commit: `053add0cc445975f26a6a0f61445a98810d177f2`.
- Inputs: all 4,096 P1 scenario outputs and all 32,768 underlying vertices in `research/results/submission_frozen_sources_20261106/P1/`.
- Keep all 256 backgrounds, all four timing combinations (LS, LL, ES, EL) and all four intervention arms (00, 10, 01, 11), including failures and zeros. No survival gate, model selection, rate fitting, or subgroup search is added.
- Response: source `mean_log_F_B`, the equally weighted mean across the eight source corners of log aquatic cohort abundance (each F_B is the final-20-year mean of the 80-year deterministic model). The log is not applied to the across-corner mean. The four vegetation-absent corners have zero focal-function effect.
- `00` switches off the two focal vegetation functions; other fixed vegetation features can remain. It does not mean vegetation is absent.

## Exact decomposition

For each source background and timing, using Y_ab = mean_log_F_B in arm ab:

1. Refuge increment: C = Y_10 - Y_00.
2. Feeding-support increment: D = Y_01 - Y_00.
3. Nonadditivity: I = Y_11 - Y_10 - Y_01 + Y_00.
4. Net two-function effect: T = Y_11 - Y_00 = C + D + I.

Report the complete 4-timing × 4-term table. For every term, report the average early-versus-late contrast, average long-versus-short contrast, arrival×duration contrast, and the diagonal EL-minus-LS contrast. The last is a description of the already established reversal, not a separately selected confirmatory endpoint.

Use 10,000 paired bootstrap resamples of all 256 source backgrounds (seed 20261126), with the **same indices for every timing and component**, to describe variation across this synthetic source sample. Report pointwise 95% percentile intervals, without p-values or claims of new confirmatory significance. These are not field confidence intervals. Record the resampling-index hash and input hashes.

Also report all four timings' counts of positive/negative/zero net effects, and the full LS→EL sign-transition table using exact zero. Report positive/negative shifts separately from actual sign reversals. These counts describe the sampled model family, not prevalence among real wetlands.

## Verification and interpretation

Reconstruct every mean_log_F_B from vertices; verify complete pairing, source identity, positive finite F_B and the V=0 numerical control. Require C+D+I=T for every background/context and every bootstrap replicate. Independently recalculate the summaries and transitions.

Treat C and D as factorial intervention effects that include feedback through the model. They are not measured mediation paths, direct mortality partitions, or percentages of a natural causal effect. Keep G7 unchanged. Preserve the original P1 inference intervals and distinguish the new shared-resample intervals from those existing values. The original attack=.5/recruitment=.75 regime remains conditional on an earlier exploratory choice.
