# G12 — Prior dependence and identifiability of the original model-native ABC–POM screen

**Fixed diagnostic design, 2026-11-07 JST, before computing G12 alternative-prior and tolerance outcomes.** All R1–R4, G5/G7, G8–G11 findings stay immutable. The original R2 20,000-draw results and 794 accepted four-sign outcomes are known; G12 is **post hoc research and no empirical ABC posterior**. This uses no new field data and no new biological simulation.

## Controlling source

The original **80-year** joint 3,600-catalogue ABC–POM R2 synthetic prior run: GitHub Actions [#41262102436](https://github.com/zuizui0223/frogcs/actions/runs/41262102436), eight original \`integrated-80year-abc-shard-0..7\` artifacts. Each is 2,500 distinct \`draw_id\`s, exactly 0..19999 without duplicates. Preserve all acceptance failures and all 3,600 original model IDs as the legal prior universe (the sampled prior contained 3,582 unique IDs). Read the original authoritative run summary and hashed R2 receipt when available; verify the archive SHA256 of each entire gzip shard and reject drift. Recount the original strict four-sign acceptance using the saved four log(F_B) contrasts with epsilon=1e-6, expecting **794/20,000**, and the artificial 5% model survival floor subset expecting **426/20,000**. Provenance: original main SHA \`5e2f0a87c639df373fa2700b29403d2ab417a1cc\`. No recoding of the mechanistic kernel.

## Fixed synthetic rate-prior scenarios (independent rate axes)

The original proposal prior is discrete uniform for attack (.5/1.5/3), local recruitment rho (.25/.5/.75) and conversion (2/4/8), with uniform original 3,600-model \`model_id\`, three developmental contexts and discrete nuisance levels. G12 **does not refit** a posterior. It importance-reweights the already simulated 20,000 proposals to illustrative hypothetical *rate* priors. Each list below gives the target mass in ascending rate-level order, independent across the three axes. The remaining two rate axes stay uniform. Pre-specify:

1. \`uniform_original\`: (1/3,1/3,1/3) on all three.
2. \`weak_attack\`: attack (0.60,0.30,0.10).
3. \`strong_attack\`: attack (0.10,0.30,0.60).
4. \`high_recruitment\`: rho (0.10,0.30,0.60).
5. \`low_recruitment\`: rho (0.60,0.30,0.10).
6. \`fast_conversion\`: conversion (0.10,0.30,0.60).
7. \`slow_conversion\`: conversion (0.60,0.30,0.10).
8. \`joint_pattern_favorable\`: weak attack, high recruitment, fast conversion all simultaneously.
9. \`joint_pattern_unfavorable\`: strong attack, low recruitment, slow conversion all simultaneously.

Weights for each simulated draw = product across three axes of [target probability / 1/3], with zero extra weighting on structure or stage, and are *not* likelihood weights. Weighted synthetic acceptance = sum(weights × accepted) / sum(weights), so changes represent **prior predictive sensitivity**, not evidence for an observed wild predation or recruitment rate. Compute weighted accepted effective sample size (Kish ESS), whole-proposal ESS and weighted accepted model diversity. Do not relabel the weighted accepted draws as an empirical posterior.

## Fixed mechanistic summaries and criterion sensitivity

- All 20,000 proposals: observed-prior and accepted counts by rate, context, canonical model ID, and exact binary mechanism features (edge_SD, edge_DS, cover_SF, support_DF, cover_DF, cover_DS, cover_SD, support_DS, survival, timing, reverse, litter and behavior, plus refuge-order/strength and size-gate). No cherry-picking a helpful feature after results.
- For each of the nine rate priors: synthetic acceptance fraction, proposal and accepted effective sample size, accepted versus full-draw weighted feature frequencies (one table for every categorical feature level), accepted model-ID entropy effective number and inverse Simpson effective number, fraction of weighted acceptance concentrated in top 10/50 model IDs; compare explicitly to the original uniform model-ID sampling. These support diagnostics are conditional on a synthetic model catalogue that overrepresents some functional forms.
- Tolerance epsilon applied to the four **original log-scale** model summaries, without biological reruns, at **[0,1e-6,1e-4,1e-3,1e-2,5e-2,1e-1]**. Strict signs OS < -eps, OV < -eps, SV > eps, OSV > eps. Report exact accepted count, overlap with baseline, original 20,000 denominator, distinct accepted model IDs, and loss due to tightening. This is not an observational-distance tolerance.
- Original raw(F_B) four-sign acceptance from \`raw_OS,raw_OV,raw_SV,raw_OSV\` at eps=1e-6 separately from log-scale; report raw/log overlap and discordance. Their **scales are not interchangeable**. Do not promote a different result merely because it has higher acceptance.

## Source, inference and decision guardrails

- At least one substantive alternative-prior result must be independently computed by a second implementation from the same raw saved proposal records; verify the published original rate-cell 27-table and 3 original 1-dimensional marginal axes against the preserved 20,000 rows.
- For each scenario report full and accepted weight ESS. A non-negligible acceptance under one prior does not uniquely identify a mechanism or prove the posterior from field observations; hold rates and model-native four-sign summaries distinct from the NAAMP adult calling/statistical association endpoints.
- Source bootstrap: optionally 10,000 resamples of original simulation proposal IDs (fixed seed 20261107), purely to describe finite prior Monte Carlo variability. Not independent biological replicates, not wild field uncertainty.
- **Core interpretation decisions fixed:** We can claim that a defined model family generates the four signs under certain rates and mechanisms; enrichment and accepted-model diversity quantify identifiability *under the synthetic prior*. If many models remain, report equifinality honestly; if rates strongly change acceptance, report prior fragility. No G12 conclusion is a field-conditioned posterior. No retuning priors based on G12 outputs or filtering failed model proposals.

## Publication gate

Only after all 8 shards, original 794 and 426, 27 rate-cell and original marginal checks, all 9 prior scenarios and 7 epsilons are independently validated, write G12 result and add concise Supplement S14 to the current stacked Draft. Leave the G11 positive independent structural-replication result unchanged, along with original negative G5/G7 field validation. If the original shards fail to materialize or their hashes cannot be confirmed, declare G12 **not verified** and do not fabricate any quantitative findings.
