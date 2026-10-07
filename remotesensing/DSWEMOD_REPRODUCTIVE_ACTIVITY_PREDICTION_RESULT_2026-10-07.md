# DSWEmod reproductive-activity prediction result — 2026-10-07

## Role

This result is distinct from the closed concentration mechanism.

The surface-hydrology mechanism tests showed that remotely sensed water state did not explain the higher-order within-taxon spatial concentration after total activation was conditioned on.

This analysis instead asks whether the same hydrology contains transferable information about **whether a taxon reaches a strong reproductive acoustic state** on unseen routes.

## Frozen design

Population:
- DSWEmod M3-complete population;
- 1,649 focal pairs;
- 324 routes;
- 19 states;
- 2,488 unique RunIDs;
- 175,820 species × RunID × physical-SiteID prediction cells.

Primary response:
- CallingIndex >= 2.

Secondary:
- CallingIndex >= 1.

Cross-fitting:
- deterministic route folds;
- fit on one route fold and score only the opposite fold;
- species-specific models;
- equal-species held-out Bernoulli log loss;
- route-block bootstrap, 10,000 replicates, seed 2840330.

Model sequence:
- B0: weather/season baseline;
- B1: + current route wetness and local current wetness;
- B2: + 3-month recent wetness;
- B3: + 12-month hydroperiod variability.

## Primary result: strong chorus, CI >= 2

Equal-species mean held-out log loss:
- B0 = 0.380420
- B1 = 0.383023
- B2 = 0.372454
- B3 = 0.374729

Incremental gains, where positive means better held-out prediction:

### Current water state

- observed gain = -0.002604
- 95% route-bootstrap interval = [-0.008946, +0.004734]

No transferable gain.

### Recent 3-month wetness

- observed gain = **+0.010569**
- 95% route-bootstrap interval = **[+0.002535, +0.025074]**

This is the only hydrology increment whose interval lies wholly above zero.

### 12-month variability

- observed gain = **-0.002276**
- 95% route-bootstrap interval = **[-0.005901, -0.000334]**

Adding long-term variability significantly worsened held-out prediction relative to B2.

### Full hydrology set

- total B0 -> B3 gain = +0.005690
- 95% interval = [-0.005152, +0.021601]

The full hydrology set is therefore not supported as an overall transferable predictor under the frozen primary rule.

Classification:
**hydrology_activity_prediction_not_supported**.

The negative overall classification must be retained even though the predeclared 3-month increment is positive.

## Secondary result: any calling, CI >= 1

Incremental gains:
- current = +0.001207; 95% CI [-0.004908, +0.006972]
- recent 3-month = -0.000614; 95% CI [-0.003763, +0.002746]
- 12-month variability = -0.003246; 95% CI [-0.008058, +0.000125]
- total = -0.002654; 95% CI [-0.011810, +0.005151]

No hydrology increment is supported for any-calling.

## Biological interpretation

The remote-sensing results now separate two questions:

1. **Where is reproductive acoustic activity allocated?**
   - current surface water, partial/potential wetland state, recent persistence and 12-month variability do not explain the concentration residual.

2. **When does activity escalate to a strong chorus state?**
   - recent 3-month wetness contains transferable predictive information for CI>=2, even after weather/season and current water state are represented;
   - the same signal is absent for simple CI>=1 calling.

Thus recent wetness may contribute to **reproductive-state escalation** without determining the higher-order spatial configuration of that activity.

This is consistent with a two-stage ecological picture:
- recent habitat history contributes to whether a taxon becomes strongly active;
- an additional process determines which set of sites expresses that activation together.

The second stage remains unresolved.

## Important boundaries

Do not interpret the positive 3-month gain as:
- reproductive success;
- spawning success;
- larval production;
- abundance;
- a causal mediation proof;
- an explanation of the concentration residual.

The response is reproductive acoustic activity only.

Species coefficients were heterogeneous, so do not headline a pooled directional hydrology coefficient.

## Decision

Retain the positive 3-month held-out prediction result as a separate ecological result.

Do not reopen current-water or 12-month variability definitions, and do not use the positive intermediate increment to relabel the frozen overall B0->B3 result as a primary success.
