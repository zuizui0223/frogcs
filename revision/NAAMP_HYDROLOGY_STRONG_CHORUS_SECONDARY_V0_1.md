# NAAMP hydrology–strong-chorus secondary test v0.1 — 2026-10-07

**Frozen before any hydrology-augmented frog endpoint was calculated.**

## Role

This is a secondary biological bridge only. It cannot rescue or redefine the primary concentration mechanism test.

Question:
Within a taxon that was acoustically silent across the drier route, are strong wet-survey choruses preferentially expressed at physical stops that became wetter?

## Population

Use only focal pairs retained by the primary M1 current-water coverage gate.

Within each pair, retain route-new taxa: taxa with CallingIndex 0 at all ten drier-survey stops and CallingIndex >0 at at least one wetter-survey stop.

Cluster identity = focal pair x taxon.

## Response

For each of ten physical stops:
- y = 1 if wetter-survey CallingIndex >=2;
- y = 0 otherwise.

CI>=2 is fixed because the existing paper already identifies direct 0->CI2/3 activation as the dominant recruited state.

## Hydrology predictor

x = W_wetter - W_drier at the same physical SiteID, using the frozen 250-m JRC MonthlyHistory water fraction.

Within each pair x taxon cluster, center x by its ten-stop mean.

Thus x represents local hydrological change relative to the same route event, not route-wide wetness.

## Primary statistic

For each informative cluster containing at least one y=1 and one y=0 stop, calculate:

d = mean(x | y=1) - mean(x | y=0)

Primary endpoint = mean d across informative pair x taxon clusters, with each cluster weighted equally.

Positive d means strong chorus placement is biased toward stops with greater local water increase.

## Null and inference

Within each pair x taxon cluster, randomly permute the centered x values among the ten physical stops while holding the observed y pattern fixed.

Use 1,000 permutations, seed 2840314.

For each permutation calculate the same equal-cluster-weight mean d.

Report:
- observed mean d;
- permutation 95% interval;
- plus-one upper-tail P.

Support requires observed d above the upper 95% permutation bound and P<0.05.

## Coverage gate

Require:
- >=500 informative pair x taxon clusters;
- >=100 routes;
- >=10 taxa.

If the gate fails, classify as secondary-inconclusive. Do not lower thresholds.

## Interpretation

Support would connect remotely sensed local wetland change to the spatial placement of a previously established reproductive acoustic state transition.

It does not show spawning success, larval survival, recruitment, abundance change or unique causal mediation.

## Anti-tuning

Do not change CI>=2, 250-m radius, route-new definition, cluster weighting, permutation unit, seed or one-sided direction after hydrology values are joined.
