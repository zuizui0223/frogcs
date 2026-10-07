# Surface-hydrology mechanism closure — 2026-10-07

## Scope

This record closes the currently tested **remotely sensed surface-hydrology** explanations for the NAAMP within-taxon multi-site concentration.

It does not claim that all hydrology is irrelevant. It closes only the measured surface-water / partial-wetland routes described below.

## 1. JRC MonthlyHistory visible open water

Primary 250-m test:
- 1,881 pairs, 366 routes, 20 states;
- same-sample M0 residual = 0.174490;
- M1 current-water residual = 0.182250;
- fraction removed = **-4.45%**;
- M1 residual remained above its simulated upper 95% bound.

500-m named sensitivity:
- 2,016 pairs, 371 routes, 20 states;
- fraction removed = **-0.07%**;
- residual remained outside the null interval.

100-m named sensitivity:
- 1,640 pairs, 349 routes, 20 states;
- M0 residual was already inside its null interval before hydrology;
- therefore this subset was mechanism-uninformative rather than evidence of sufficiency.

Strong-chorus bridge:
- 1,000 informative pair × taxon clusters;
- 252 routes, 45 taxa;
- observed water-change difference at CI>=2 vs other stops = +0.000160;
- permutation 95% = [-0.000798, +0.000831];
- P = .360.

Conclusion: visible monthly open-water change does not explain concentration or strong-chorus placement.

## 2. MODIS DSWEmod partial / potential wetland

The DSWEmod source uses monthly 250-m DSWE classes:
- 0 not water;
- 1 high-confidence water;
- 2 moderate-confidence water;
- 3 potential wetland;
- 4 low-confidence water/wetland;
- 9 no data.

The primary exposure included classes 1–3 and therefore tests partial/potential wetland state beyond visible open water.

Year 2004 was prospectively classified as source-unavailable because the official ScienceBase child TIFF had size 0 and returned HTTP 404. No imputation was used.

### Primary 500-m M0–M3 sequence

M1 current-state coverage:
- 2,249 pairs;
- 372 routes;
- 19 states.

M3 complete-sequence coverage:
- 1,649 pairs;
- 324 routes;
- 19 states.

On the identical 1,649-pair M3-complete sample:

| Model | Meaning | residual | null 95% interval | upper-tail P |
|---|---|---:|---|---:|
| M0 | principal comparator | 0.502156 | [-0.197230, 0.224164] | .000999 |
| M1 | + current partial-wetland state | 0.516837 | [-0.210036, 0.196035] | .000999 |
| M2 | + 3-month persistence | 0.506561 | [-0.193356, 0.199021] | .000999 |
| M3 | + 12-month variability | 0.530218 | [-0.194326, 0.198577] | .000999 |

Residual decomposition:
- current-state fraction removed = **-2.92%**;
- recent-persistence increment = **+2.05%**;
- variability increment = **-4.71%**;
- total M0→M3 fraction removed = **-5.59%**.

Classification:
**dswemod_dynamic_hydrology_not_supported**.

### 250-m named sensitivity

- 2,246 pairs;
- 372 routes;
- 19 states;
- M0 residual = 0.349605;
- M1 residual = 0.341742;
- fraction removed = +2.25%;
- both M0 and M1 remain far outside their simulated upper bounds, P=.000999.

This small residual reduction is partial in sign only and does not change the primary negative conclusion.

### DSWEmod strong-chorus secondary

- 1,211 informative pair × taxon clusters;
- 263 routes;
- 45 taxa;
- observed DSWEmod_123 difference at CI>=2 vs other stops = **-0.000441**;
- permutation 95% = [-0.002297, +0.002384];
- P = .646.

Classification:
**dswemod_strong_chorus_alignment_not_supported**.

## Scientific conclusion

Across two independent remotely sensed surface-water representations:

1. 30-m Landsat-derived monthly visible open-water extent;
2. 250-m MODIS DSWE including moderate-confidence and potential-wetland classes;

the focal concentration residual is not explained by:
- current surface-water state;
- current partial/potential wetland state;
- recent 3-month wetness persistence;
- recent 12-month surface-hydrology variability.

Nor do these remotely sensed surface-water changes preferentially identify the stops expressing the established CI>=2 strong-chorus transition.

Therefore the earlier limitation can now be narrowed.

The leading unresolved environmental explanation is no longer generic **surface-water extent**. Remaining environmental candidates must involve wetland properties not captured by these products, such as:
- water depth;
- water temperature;
- soil/substrate moisture;
- water beneath dense emergent vegetation or canopy;
- very small pools below product support;
- chemistry or hydroperiod features not represented by monthly fractional inundation.

The alternative class of explanations also becomes relatively more important:
- demographic readiness / local abundance;
- latent reproductive state;
- social facilitation or chorus-state dependence.

## Next authorized landscape test

A separately frozen NWI rain-filter analysis tests a distinct mechanism:

> persistent wetland hydrogeomorphic type may modify how a common rainfall pulse is translated into reproductive acoustic activation.

This is not another dynamic surface-water test.

## No-retuning rule

Do not reopen JRC or DSWEmod by:
- changing radii beyond the already named sensitivities;
- changing DSWE class sets after seeing results;
- relaxing missingness rules;
- changing persistence/variability windows;
- searching species subsets for favorable hydrology effects.

Any future hydrology analysis must measure a genuinely different environmental quantity.
