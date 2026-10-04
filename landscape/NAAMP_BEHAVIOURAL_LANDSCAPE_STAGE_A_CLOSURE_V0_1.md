# Behavioural-landscape Stage A closure v0.1

## Scope

Stage A tested route-order geometry only.

It is separate from RC6 and changes no RC6 claim.

## A1 — selective/discontinuous deep geometry

Prespecified prediction:
- deep k>=4 activation would show **positive q-conditioned holes excess**.

Result:
- **FAIL**.

Coverage:
- 2,835 focal pairs;
- 428 routes;
- 3,080 dry-route-silent wet-active taxon clusters;
- 767 deep k>=4 clusters;
- 243 routes represented among deep clusters.

Primary holes excess:
- observed mean excess = **−0.1535**;
- exact-k fixed-q null 95% interval = **−0.0818 to 0.0838**;
- prespecified upper-tail P = **1.0**;
- route-bootstrap 95% CI = **−0.2578 to −0.0494**.

The observed direction is opposite to the original prediction.

Fixed secondary metrics are directionally coherent:
- span excess = **−0.1535**;
- contiguous-component excess = **−0.1210**;
- mean pairwise StopNumber-lag excess = **−0.0987**.

Interpretation:
- deep active sets are modestly **more compact in route order** than fixed-q exact-k expectation;
- do not describe them as unusually scattered or fragmented.

## A2 — recurrent-core expansion

Generated only after A1 readback.

Question:
- once exact k, exact number h of active prior-strong sites, fixed q and the prior-strong mask are held constant, are active non-strong sites unusually close to activated recurrent strong sites?

Coverage:
- 337 eligible deep clusters;
- 159 routes;
- 34 taxa.

Primary core-distance excess:
- observed mean excess = **−0.07657**;
- exact-k/h null 95% interval = **−0.07842 to 0.07911**;
- lower-tail P = **0.0305**;
- route-bootstrap 95% CI = **−0.1486 to −0.0051**;
- prespecified support classification = **FAIL**.

Why FAIL:
- the point estimate is negative;
- the lower-tail probability and route bootstrap favor the predicted direction;
- but the observed value does not cross the prespecified exact-null 2.5% boundary.

Secondary adjacency-to-core fraction:
- excess = **+0.01184**;
- upper-tail P = **0.196**;
- route-bootstrap interval includes zero.

Interpretation:
- there is **no prespecified support** for a recurrent-core expansion mechanism;
- compact route-order geometry and recurrent strong-site targeting should remain separate empirical properties.

## Current landscape conclusion

The strongest authorized Stage-A statement is:

> **Deep frog chorus activation is expressed in route-order configurations that are slightly more compact than expected after exact activation depth and fixed site propensities are represented, but that compactness is not convincingly attributable to expansion around recurrent strong-chorus sites.**

This creates three separable spatial quantities:

1. **depth** — how many stops a taxon occupies;
2. **geometry** — how compact those active stops are in route order;
3. **history** — whether recurrent strong-chorus sites are preferentially included.

The data support all three as useful axes, but do not support collapsing geometry and history into one identified mechanism.

## Stop rule

Stage-A topology exploration is now closed.

No new StopNumber-derived geometry metric, threshold or recurrent-core definition may be added based on these results.

Permitted next work:
- deterministic QA / bug correction;
- exact-coordinate analysis only after independent coordinate validation;
- response-blind external landscape-covariate coverage audit;
- a new biological landscape contract written only after external coverage is frozen.

## Next evidence source

Stage C is the preferred next step:
- independently generated NAAMP landscape covariates;
- SiteID/route coverage audit before frog outcomes;
- landscape heterogeneity / habitat similarity hypotheses frozen only after coverage is known.

This is preferable to additional same-data topology fishing.
