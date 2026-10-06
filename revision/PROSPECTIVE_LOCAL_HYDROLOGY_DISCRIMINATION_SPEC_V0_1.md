# Prospective local-hydrology discrimination test v0.1

## Status

Future-study design only. **Do not execute on the current NAAMP outcome archive.**

This specification is generated from the environmental-factor coverage audit and preserves the current science lock.

## Biological question

Does the residual taxon-by-place configuration observed during favourable calling conditions arise because a broad taxon-night activation state is filtered through dynamic local wetland conditions?

## Competing generators

### H1 — broad weather only

Calling probabilities are determined by route-night atmospheric conditions, taxon-specific environmental response and persistent site propensity.

Prediction:
- adding direct local wetland state should add little;
- conditional within-taxon concentration should remain excessive.

### H2 — local wetland state only

Each site responds independently once its actual water state and local microenvironment are known.

Prediction:
- direct hydrology should remove most conditional concentration and residual route-night dependence;
- prior-site alignment should largely disappear after current hydrology is represented.

### H3 — broad activation × local filtering

A taxon enters a favourable-night state at a scale broader than an individual wetland, but expression depends on site-specific wetland state.

Prediction:
- direct hydrology should improve local prediction substantially;
- a taxon-night shared component should still be needed;
- the interaction of shared state with local hydrology should outperform either component alone;
- recurrent site effects may shrink if they proxy persistent hydrological suitability but need not vanish.

## Minimum data design

Use a repeated fixed-site monitoring system with verified physical coordinates.

Before reading the configuration endpoint, collect or reconstruct for every site × survey event:

- water level or inundation state;
- hydroperiod class and recent wet/dry transition;
- local soil moisture / runoff proxy;
- local precipitation where possible;
- air temperature;
- water temperature;
- relative humidity;
- pressure;
- exact observation time;
- moon illumination;
- canopy / emergent vegetation;
- stable wetland type / morphology;
- observer and acoustic-detection conditions;
- taxon × site CallingIndex or equivalent calling intensity.

## Primary comparison

Fit the same response-magnitude-conditioned configuration endpoint under three frozen comparators:

1. broad weather + prior site history;
2. direct local wetland state + prior site history;
3. broad taxon-night state × local wetland state + prior site history.

All models must be trained out of block relative to the focal geography or time period.

## Primary mechanistic decision

### Supports environmental filtering mechanism

- model 2 or 3 removes the conditional configuration residual to within its prespecified null envelope;
- residual route-night dependence collapses;
- historical-site alignment is substantially attenuated after current wetland state is included.

### Supports broad-state × local-filter mechanism

- model 3 clearly outperforms models 1 and 2;
- local hydrology improves site-level prediction;
- a shared taxon-night component remains necessary;
- spatial expression remains non-uniform.

### Supports additional latent/social/demographic mechanism

- direct hydrology is strongly predictive but substantial conditional residual dependence remains;
- model 3 remains insufficient;
- recurrent-site alignment persists after current wetland state is represented.

## Required inferential boundary

This test must distinguish:
- **prediction of calling occurrence/intensity** from
- **prediction of the realised taxon-by-place configuration conditional on response magnitude**.

A hydrology model can predict marginal calling well and still fail to explain the joint spatial configuration.

## Why this is the decisive next test

The current NAAMP evidence already makes another route-wide weather covariate low value.

The remaining environmental explanation must be event-varying, within-route heterogeneous and taxon-specific. Direct local hydrology has exactly that structure and is independently known to influence frog calling and breeding habitat availability.

Therefore the most informative next mechanistic experiment is:

> **measure the local wetland state directly, then ask whether the configuration residual disappears.**

This future design is separate from the current manuscript and does not reopen the NAAMP analysis.
