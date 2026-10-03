# Monitoring-dependence prior-study audit v0.1

Date: 2026-10-03

## Purpose

Define exactly what is and is not new about the post-reopening monitoring implication. The present NAAMP analysis must not claim that spatial dependence among route stops, correlated spatial replicates, or spatial autocorrelation in amphibian occupancy are new ideas.

## Closest precedents

| Study | What it already establishes | What it does not test that frogcs now tests |
|---|---|---|
| Weir et al. 2009, *Herpetological Conservation and Biology* 4:389–399 | In an early multi-year NAAMP occupancy analysis, stops were treated as spatial replicates and occupancy was assumed independent across stops; the authors explicitly warned that stops nested within routes could induce spatial dependence and affect trend precision. | Whether such dependence is empirically expressed as a same-species, same-route-night acoustic state; whether it remains after measured weather and historical site use; quantitative uncertainty inflation in the present multi-species rain-pulse setting. |
| Hines, Nichols & Collazo 2014, *Methods in Ecology and Evolution* 5:583–591, DOI 10.1111/2041-210X.12186 | Provides multiseason occupancy models for potentially correlated spatial replicates and shows strong support for correlated-replicate models in a Breeding Bird Survey case study. | Frog-specific same-night acoustic-state dependence and its relationship to rainfall-associated chorus activation. |
| Doser et al. 2026, *Journal of Applied Ecology* 63:e70342, DOI 10.1111/1365-2664.70342 | Uses Minnesota Frog and Toad Calling Survey data collected under the NAAMP protocol; models 2,102 stops on 211 routes for 11 species; includes a spatially varying occupancy intercept to account for residual spatial autocorrelation across stops and spatially varying long-term trends, while modelling detection/availability with survey covariates. | A short-timescale species × route-night latent acoustic state, conditional residual dependence after actual antecedent rainfall and prior SiteID history, or a rain-pulse allocation statistic holding total activity fixed. |

## Novelty boundary

Therefore do **not** claim:

- first evidence that route stops can be spatially dependent;
- first frog occupancy model to account for spatial autocorrelation;
- first warning that treating spatial replicates as independent can affect precision;
- a new general theory of correlated replicate surveys.

The narrower contribution is:

> **In a repeated ten-stop anuran monitoring network, a short rainfall-associated behavioural state leaves broad positive residual dependence among separated stops within the same species and route-night even after flexible measured weather, actual 72-h rainfall, prior physical-site use, dry-state persistence and total activity are represented.**

The applied extension is also narrow:

> **In the same data, covariance estimators that respect route-night or route clustering are broadly larger than model-based IID uncertainty across information-rich species.**

This is an empirical demonstration in a behavioural-pulse context, not a replacement for correlated-replicate occupancy models and not a reanalysis of published NAAMP occupancy trends.

## Why the distinction matters

Doser et al. model **persistent/spatiotemporal occupancy structure** across stops. The current frogcs diagnostic instead asks whether, after a stop-specific mean model has already represented historical place and measured route-night environment, the remaining **acoustic expression during one route-night** is shared across separated stops within a species.

The two forms of dependence can coexist. Persistent spatial autocorrelation says nearby or environmentally similar stops differ systematically in long-term occupancy. Species × route-night residual dependence says the observation/availability state on a particular night can also be a landscape-scale random quantity rather than ten conditionally independent stop outcomes.

## Current evidence

Post-reopening NAAMP diagnostics:

- flexible measured common environment removed **11.4%** of the principal concentration residual;
- actual 72-h rainfall amount removed **6.5%** on a same-sample comparison;
- standardized residual-dependence statistic **D = 0.416** versus an independent-Bernoulli null centred near zero (P = 0.000999);
- drier-route-silent taxa: **D = 0.567**;
- all **40/40** information-eligible taxa had positive specieswise D;
- pair-clustered uncertainty exceeded IID for **38/39** information-eligible species (median ratio **1.61**), and route-clustered uncertainty did so for **36/39** (median **1.48**).

All of these NAAMP extensions are post-hoc/exploratory after the explicit 2026-10-03 reopening. Prospective WFTS confirmation remains separate.
