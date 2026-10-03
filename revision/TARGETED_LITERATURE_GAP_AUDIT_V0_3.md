# Targeted literature-gap audit v0.3 — conditional calling allocation

## Status

This file supersedes `revision/TARGETED_LITERATURE_GAP_AUDIT_V0_2.md` as the current novelty lock.

The detailed closest-study matrix is:
- `revision/CLOSEST_PRIOR_STUDIES_AUDIT_V0_1.md`

## What the literature already establishes

The following are **not** novelty claims for frogcs:

1. **Weather-sensitive calling.** Rainfall, temperature, humidity and other weather variables affect frog calling, often in species-specific ways.
2. **Assemblage-wide acoustic dynamics.** Calling richness and composition change rapidly over time.
3. **Environmental pulses can change chorusing across multiple sites.** Sarker et al. (2022) showed species- and site-specific chorus changes before and after river-flow inundation at six acoustic sites.
4. **Cross-site covariance/synchrony exists.** Brooke et al. (2000), Trenham et al. (2003), Brodie et al. (2025) and Rush et al. (2026) establish covariance or synchrony at local-to-regional scales.
5. **Species × wetland calling matrices have persistent structure.** Guzy et al. (2012) explicitly analysed calling-index structure across wetlands.
6. **Meteorological response functions can be estimated across many species.** Thompson et al. (2022) modelled 100 Australian frog species at continental scale.
7. **Site fidelity and persistent site suitability are known in frogs.**

Therefore avoid:
- first evidence that rain coordinates frogs across sites;
- first multi-site frog chorus study;
- first species × site acoustic matrix;
- first evidence of recurrent frog chorus sites;
- first evidence of spatial coherence in frogs.

## Updated empirical object

The depth audit changed the biological description.

Do **not** say:
> the unusual effect begins at the third occupied stop.

The exact marginal-depth audit shows:
- calling-incidence depths 1–3 fall within both activation-null envelopes;
- depths 4–10 exceed both;
- marginal coefficients decrease smoothly with depth.

Authorized description:
> **recent-rain calling has a heavier/deeper within-taxon multi-site tail than expected.**

This is not:
- a threshold at exactly three stops;
- exponential growth with stop number;
- movement through successive stops.

## Strongest remaining novelty

The novelty is **conditional allocation**.

The key question is:

> After representing the amount of acoustic activation, transferable taxon-specific rainfall responses, strictly-prior taxon × physical-site use, dry-state persistence and wet-incidence magnitude, is wet-state calling still more concentrated within the same taxa across sites than expected?

Principal evidence:
- 2,916 pairs;
- 439 routes;
- 20 states;
- observed concentration beta = 1.6503;
- principal comparator prediction = 1.3535;
- conditional residual = 0.2969;
- null residual 95% interval = -0.1319 to 0.1187;
- P = 0.000999.

Strongest sensitivity:
- held-out rain × history gate prediction = 1.3323;
- residual = 0.3180;
- P = 0.000999.

## Why this differs from the closest studies

### Versus Sarker et al. 2022

Sarker et al. already show that an explicit wetting pulse changes chorus richness and species-specific chorusing at multiple sites.

frogcs instead asks:
> given the amount of activation, **how is it allocated among taxa across repeated sites?**

### Versus Guzy et al. 2012

Guzy et al. already show structured species × wetland calling-index matrices.

frogcs instead asks:
> during a short wet-state contrast, does the **incremental acoustic expression** retain dependence after historical species × site structure is placed inside the null model?

### Versus Brooke 2000 / Brodie 2025 / Rush 2026

These establish cross-site covariance or synchrony.

frogcs does not ask whether sites covary. It asks:
> whether multi-site calling remains disproportionately concentrated within the same taxa after first-order ecological expectations are represented.

### Versus Thompson et al. 2022

Thompson et al. establish broad species-specific weather response.

frogcs explicitly uses species-specific response as **part of the comparator**, then tests what structure remains.

## Frog-specific novelty

> Recent-rain conditions are associated with direct switching from acoustic silence into strong chorus, and the resulting calling-incidence distribution has an unusually deep within-taxon spatial tail across separated route stops. Strong calling is preferentially re-expressed at taxon-specific physical sites with prior strong-chorus history.

## General ecological novelty

> **An environmental pulse can alter not only marginal activity but the dependence structure of a joint species × place activity matrix.**

Stronger formulation:

> **Pulse-associated activity can remain non-independently allocated after marginal species response, local historical propensity and total activation magnitude are explicitly represented.**

This is the conceptual contribution.

## Scope limits

The evidence does not establish:
- causal rainfall effects;
- demographic occupancy;
- colonization;
- movement among route stops;
- literal simultaneity;
- direct acoustic communication among route stops;
- individual memory or philopatry;
- spawning or reproductive success;
- a unique lower-level mechanism;
- universality beyond the sampled system.

## Closest-study verdict

The two closest ecological antecedents are:
- **Sarker et al. (2022)** for an explicit environmental pulse acting on multi-species chorusing across multiple acoustic sites;
- **Brodie et al. (2025)** for species-specific cross-site chorus correlations and rain-associated onset across fixed sites.

**Guzy et al. (2012)** is the closest precedent for persistent species × wetland calling-index structure.

These studies remove any defensible novelty claim based simply on multi-site response, cross-site covariance, or recurrent acoustic site structure.

## Current novelty verdict

**Novelty remains substantive but narrow.**

The paper should not be sold as discovering weather-sensitive frog chorusing or spatially coordinated frog activity.

It should be sold as:
> **a large-scale dependence-level analysis of how wet-state acoustic activity is allocated within a repeated species × place matrix, after the most obvious first-order ecological explanations are explicitly built into the comparator.**
