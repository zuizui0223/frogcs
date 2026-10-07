# DSWEmod recent-wetness temporal validation v0.1 — 2026-10-08

**Status:** post-discovery prospective validation frozen after the cross-route DSWEmod reproductive-activity prediction showed a positive recent-3-month increment, and before inspecting any early-to-late temporal-holdout score.

## Purpose

The previous route-fold analysis found:
- current-month DSWEmod did not improve transferable strong-chorus prediction;
- adding route-level recent 3-month wetness after current state improved equal-species held-out log loss;
- the full hydrology package was not supported because 12-month variability worsened prediction.

This new test asks only:

> Does the fixed 3-month route-level wetness history improve prediction of strong reproductive acoustic activity across time, not merely across routes?

It is a prospective validation of the newly generated hydrological-memory hypothesis, not part of the original concentration mechanism.

## Frozen source population

Use the same DSWEmod M3-complete run-site universe underlying the frozen reproductive-activity prediction receipt.

Product:
- USGS monthly MODIS DSWEmod;
- primary 500-m class-1–3 metric;
- 2004 remains source-unavailable and is never imputed.

Response:
- strong = 1 when CallingIndex >=2, else 0.

Cell:
- species × RunID × physical SiteID.

## Frozen temporal split

Training years:
- 2003, 2005, 2006, 2007, 2008, 2009.

Validation years:
- 2010, 2011, 2012, 2013, 2014, 2015.

Do not move the split after outcome readback.

A RunID is assigned by its survey year.

## Species pool

Use the same route × RunNumber historical species pool already frozen in the NAAMP pipeline.

No species is selected based on temporal-holdout performance.

## Models

For each species fit on training years only.

Eligibility:
- >=20 positive training cells;
- positives on >=5 training routes;
- at least one negative training cell.

Ineligible species use Laplace-smoothed training prevalence for both models and therefore contribute zero gain.

### T0 — baseline

strong ~ log1p(DaysSinceRain) + mean air temperature + sin(doy) + cos(doy) + State + RunNumber

### T1 — recent hydrological memory

T0 + route_recent3

where route_recent3 is the mean 500-m DSWEmod_123 recent_wetness_3m across the ten focal physical SiteIDs for that RunID.

Do not include current-month DSWEmod or 12-month variability in this validation.

Rationale:
- the validation target is the already observed incremental recent-3-month signal;
- current and variability terms were not supported and are not allowed to dilute or rescue this focused test.

Fit:
- binomial GLM;
- ridge fallback alpha=0.01;
- fail closed to identical smoothed-prevalence predictions if either model cannot be stably fit.

## Held-out endpoint

Predict 2010–2015 cells only.

For every species represented in validation:
- calculate mean Bernoulli log loss under T0 and T1;
- gain_species = logloss_T0 - logloss_T1.

Positive gain means recent wetness improves future-period prediction.

Primary statistic:
- equal-species mean gain.

Secondary diagnostic:
- equal-species mean Brier-score change.

## Uncertainty

Route-block bootstrap over validation-period routes:
- 10,000 replicates;
- seed 2840360;
- resample route_cluster with replacement;
- retain all species/cells within selected routes;
- recompute equal-species mean gain.

Support requires:
- observed equal-species mean gain > 0;
- 95% bootstrap interval wholly above 0.

## Robustness reported without retuning

After the primary result:
- report leave-one-species-out equal-species mean gain;
- report number of species with positive / negative / zero gain.

These are diagnostics only and cannot replace the primary bootstrap criterion.

## Interpretation

Support would show that several months of wetland-state history contain predictive information about later strong reproductive acoustic activity that transfers forward in time beyond contemporaneous rain recency, air temperature and season.

It would support a **hydrological-memory / breeding-readiness** hypothesis.

It would not establish:
- reproductive success;
- individual physiological memory;
- causality of hydroperiod;
- the mechanism of the higher-order spatial concentration.

Non-support would downgrade the recent-3-month signal to a route-cross-validation finding without demonstrated temporal transfer.

## Anti-tuning

After temporal-holdout outcomes are evaluated, do not change:
- training/validation years;
- CI>=2 threshold;
- 3-month wetness definition;
- 500-m DSWEmod class set;
- baseline covariates;
- species eligibility;
- ridge alpha;
- equal-species weighting;
- route bootstrap;
- seed;
- log-loss endpoint.
