# Novelty audit v0.11 — RC11 reviewer-defense release

## Central discovery

The title-level result remains:

> **Rainfall-associated expansion is more boundary-biased than uniform activation predicts.**

RC11 does not change that story. It strengthens its reviewer defense in two ways.

## 1. Observer turnover is not required

The public NAAMP run table contains a nonempty `ObserverTrackingID` for all 21,934 runs. A reviewer-robustness contract was frozen before endpoint readback and the matched analysis was restricted to wetter–drier pairs sharing the same observer ID.

The restriction retained:
- **3,152 / 4,236 pairs (74.4%)**
- **500 routes**
- **542 observer identifiers**

Headline coefficients remained positive with 95% confidence intervals above zero:
- active stops: **β = 0.352 [0.179, 0.525]**
- richness per active stop: **β = 0.098 [0.028, 0.169]**
- route richness: **β = 0.319 [0.171, 0.466]**

Observed boundary crossing remained **92.0%**.

Primary uniform null in the same-observer subset:
- mean **80.3%**
- 95% interval **73.0–87.1%**
- four-component omnibus **P=.001**

Primary persistence-preserving null:
- mean **79.1%**
- 95% interval **73.3–84.9%**
- four-component omnibus **P=.001**

Thus observer turnover is not a necessary explanation for the title result.

## 2. The common-shift null boundary is explicit

The tested null families still impose one common activation shift after accounting for baseline cell propensities and, in the persistence stress test, pair-specific dry-state identity.

RC11 now states directly that a null allowing each species its own rainfall-response shift remains untested. Therefore the paper does **not** claim to distinguish species-level response heterogeneity from site-level activation as the unique source of the excess boundary allocation.

This is an inferential boundary, not a weakness hidden from the reader.

## Why the result remains non-mechanical

Full sample:
- observed boundary crossing **92.0%**
- primary magnitude-matched null mean **80.9%**, 95% interval **74.2–87.4%**
- primary persistence-preserving null mean **77.9%**, 95% interval **73.4–82.8%**

Same-observer subset:
- observed **92.0%**
- uniform null **80.3% [73.0–87.1%]**
- persistence null **79.1% [73.3–84.9%]**

The allocation departure therefore survives both stronger state persistence and removal of between-observer turnover.

## Preferred one-sentence novelty statement

> **Recent-rain frog-community expansion crosses spatial and taxonomic boundaries more strongly than magnitude-matched uniform activation predicts, and the departure persists when dry species × site identity is strongly preserved and when comparisons are restricted to the same observer.**
