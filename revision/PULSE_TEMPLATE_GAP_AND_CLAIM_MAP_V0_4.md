# Gap and claim map v0.4 — conditional within-taxon multi-site allocation

## Literature gap

Previous frog studies already establish rainfall-sensitive calling, short-term assemblage change, cross-site covariance, pulse-associated multi-site chorus change, persistent species × wetland calling structure and breeding-site fidelity. The closest antecedents include Sarker et al. (2022), Brodie et al. (2025) and Guzy et al. (2012). The unresolved question is narrower:

> **After total acoustic activation, taxon-specific rainfall response, prior taxon × physical-site use and dry-state persistence are explicitly represented, is the remaining wet-state calling still disproportionately concentrated within the same taxa across sites?**

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

> **Short environmental pulses can reveal a spatial dependence structure that remains hidden during behavioural inactivity and is not recovered from first-order species responses or static site propensities alone.**

This distinguishes:
- **fast gate:** short environmental state;
- **slow template:** recurrent species × place structure;
- **dependence layer:** wet-state calling remains concentrated within taxa beyond the tested species/site propensities and total incidence magnitude.

The strongest surprise is therefore **not how much activity appears, but how a fixed amount of calling is allocated among taxa across sites after first-order expectations are represented**.

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

No unexamined NAAMP partition remains a genuine confirmation dataset. Cross-fitting is protection against training/test leakage for model components, not independent replication of the discovered claim.

The next decisive test is a prospectively frozen external replication in another repeated fixed-site frog monitoring network.

## Closest-study audit

Detailed study-by-study comparison:
- `revision/CLOSEST_PRIOR_STUDIES_AUDIT_V0_1.md`

## Current title

**Rainfall-associated frog chorus activation reveals recurrent within-taxon multi-site organization**
