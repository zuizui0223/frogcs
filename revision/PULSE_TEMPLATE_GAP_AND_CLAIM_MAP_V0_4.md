# Gap and claim map v0.4 — spatial organization of frog reproductive acoustic activity

## Literature gap

Previous frog studies already establish rainfall-sensitive calling, short-term assemblage change, cross-site covariance, pulse-associated multi-site chorus change, persistent species × wetland calling structure and breeding-site fidelity. The closest antecedents include Sarker et al. (2022), Brodie et al. (2025) and Guzy et al. (2012). The unresolved ecological question is narrower:

> **When a frog taxon becomes acoustically active on a favourable night, what spatial unit organizes that activity — independent wetlands, a uniform route-wide shift, or a recurrent subset of taxon-specific locations?**

The conditional concentration analysis is the statistical test used to distinguish those possibilities after taxon response, prior physical-site use, dry-state persistence and total activation magnitude are represented.

The novelty is not “frogs are spatially coherent”, not “rain synchronizes frogs”, and not “environmental pulses alter chorusing at multiple sites.”

## Frog-specific discovery

1. **State switching:** 65.3% of CallingIndex change is 0→positive; 87.1% of activation is 0→CI2/3; direct 0→CI3 is positive.
2. **Depth:** exact marginal-depth auditing shows no third-stop threshold; calling-incidence depths 1–3 lie within both activation-null envelopes, whereas depths 4–10 are overrepresented. The result is a heavier/deeper within-taxon tail and is overwhelmingly strong chorus.
3. **Within-taxon concentration:** in 2,916 pairs with strictly prior site history, observed concentration β=1.650 vs 1.353 predicted by cross-fit species response + prior SiteID history + dry persistence (P=0.000999).
4. **Stronger sensitivity:** adding a held-out rain × history gate predicts 1.332, still below 1.650 observed (P=0.000999).
5. **Historical placement:** prior strong SiteID predicts later wet strong chorus within the same pair and taxon (β=0.151).
6. **Rain selectivity:** historical full-chorus targeting strengthens toward the survey closer to rain (β=0.0245).

## Why this is surprising

The response is not only “more taxa” or “more occupied stops.”

Even after a comparator is allowed to know:
- which taxa are rain-responsive;
- which physical sites those taxa used previously;
- whether the cell was active in the dry survey;
- the observed magnitude of wet incidence;

the observed wet-state calling is still more concentrated within the same taxa than expected.

## Exact N,K diagnostic: useful but secondary

The exact combinatorial diagnostic gives raw excess β=0.244 (0.147–0.340), but its expectation treats taxa as exchangeable once N and K are fixed.

It therefore cannot exclude a first-order explanation in which rain preferentially recruits taxa that are intrinsically widespread across route stops.

The integrated manuscript uses this only as a secondary check that the concentration is not a mathematical consequence of N and K alone.

## General ecological principle

> **Favourable nights can organize frog reproductive acoustic activity at an intermediate spatial scale: broader than independent wetland responses, but more selective than a uniform landscape-wide switch.**

The NAAMP evidence constrains that spatial organization:
- calling by the same taxon remains dependent across widely separated route positions;
- a uniform taxon-night shift makes the stops too coherent;
- unusually deep k≥4 expression is preferentially placed at strictly-prior strong-chorus sites after exact k and fixed-q site propensity are represented.

The strongest surprise is therefore **not how much activity appears, but which recurrent locations participate when a taxon becomes active across a route**.

## Generality

Within NAAMP:
- 53 taxa in the concentration decomposition;
- 25 positive contributors;
- top1 18.8%, top5 54.2%, HHI 0.0855;
- all leave-one-taxon-out totals positive;
- all 21 leave-one-state-out estimates and CIs positive.

But state-specific effects are heterogeneous:
- 14/17 positive point estimates;
- 2/17 wholly positive CIs.

Correct wording: **broad within-programme support, not spatial invariance.**

## Exploration status

The integrated story is post-opening and exploratory.

No unexamined NAAMP partition remains a genuine confirmation dataset. Cross-fitting protects component fitting and route-transfer diagnostics from direct route leakage, but is not independent replication.

The explicitly reopened NAAMP mechanism-analysis line was closed again on 2026-10-03 under `revision/NAAMP_POST_REOPENING_CLOSURE_2026-10-03.md`. No new same-data lower-level mechanism family is authorized.

The next decisive test is the prospectively frozen WFTS v0.4 external replication, including the deep-versus-shallow template-coupling prediction.

## Closest-study audit

Detailed study-by-study comparison:
- `revision/CLOSEST_PRIOR_STUDIES_AUDIT_V0_1.md`

## Current title

**Rainfall-associated frog chorus activation reveals recurrent within-taxon multi-site organization**


## Title lock after mechanism refinement

Keep the current title:

**Rainfall-associated frog chorus activation reveals recurrent within-taxon multi-site organization**

Do **not** retitle the NAAMP paper around “fast gate”, “latent state”, “template coupling”, “synchrony” or a named lower-level mechanism.

Reason:
- the title names the robust empirical object supported by the principal comparator;
- fast-gate × distributed-template structure was refined post hoc after explicit reopening;
- the current title remains accurate if WFTS later supports, weakens or fails to reproduce the secondary structural prediction;
- mechanism-level wording is appropriate in the Abstract/Discussion with an explicit exploratory boundary, not as the paper title.
