# DSWEmod strong-chorus secondary v0.1 — 2026-10-07

**Status:** frozen after the classes 1–3 concentration mechanism was closed and before this secondary endpoint is read.

## Role

This is the biological bridge authorized prospectively in the DSWEmod contract. It cannot rescue the negative concentration mechanism.

Question:
> Within a route-new taxon, are wet-survey CI>=2 strong choruses preferentially located at stops with greater DSWEmod partial-wetland increase?

## Population

Use the 500-m DSWEmod_123 current-state coverage-qualified focal-pair population after the 2004 source repair.

Within each pair retain route-new taxa: CI=0 at all ten drier-survey stops and CI>0 at at least one wetter-survey stop.

## Predictor

`x = DSWEmod_123_wet - DSWEmod_123_dry` at the same physical SiteID, 500-m radius.

Center x across the ten stops within each pair × taxon cluster.

## Response and endpoint

`y=1` when wet-survey CallingIndex >=2, else 0.

Retain clusters containing at least one y=1 and one y=0.

For each cluster calculate:
`d = mean(x | y=1) - mean(x | y=0)`.

Primary endpoint = equal-cluster-weight mean d.

## Null

Permute centered x among the ten stops within each pair × taxon cluster while holding y fixed.

Use 1,000 permutations, seed 2840315.

Support requires observed mean d above the null 95% upper bound and plus-one one-sided P<0.05.

Coverage gate:
- >=500 informative pair × taxon clusters;
- >=100 routes;
- >=10 taxa.

## Boundary

This tests spatial alignment of partial-wetland change with reproductive acoustic state switching, not reproductive success or causal mediation.
