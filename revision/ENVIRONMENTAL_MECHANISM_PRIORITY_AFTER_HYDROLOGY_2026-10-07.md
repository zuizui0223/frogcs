# Environmental-mechanism priority after surface-hydrology closure — 2026-10-07

## Purpose

Prevent open-ended post-hoc environmental variable search after the JRC and DSWEmod surface-hydrology lines were closed.

The response endpoint remains the existing within-taxon multi-site concentration. This ledger sets the order of remaining abiotic mechanism tests before their focal outcomes are read.

## Closed

### E0. Remotely sensed surface inundation

Closed as not supported for the focal mechanism:
- JRC MonthlyHistory visible open water;
- MODIS DSWEmod classes 1–3 current partial/potential wetland state;
- 3-month DSWEmod persistence;
- 12-month DSWEmod variability;
- JRC and DSWEmod strong-chorus spatial bridges.

Do not reopen by searching additional radii, class sets or time windows.

## E1. Persistent hydroperiod regime × rainfall — ACTIVE

Source:
U.S. Fish & Wildlife Service National Wetlands Inventory.

Primary:
official WATER_REGIME_NAME × rainfall response, with the frozen 500-m geometry and cross-fitted within-SiteID rain interactions.

Secondary diagnostics already frozen:
- no-NWI interaction set to zero without refitting;
- WETLAND_TYPE interaction on the identical primary-complete sample.

Decision:
- if M_REGIME is sufficient, stop abiotic mechanism search and interpret mapped persistent hydroperiod regime as a candidate spatial filter;
- if partial, retain as partial mechanism but do not tune grouping/radius;
- if unsupported or coverage-inconclusive, proceed to E2.

## E2. Local nocturnal thermal state — CONDITIONAL NEXT TEST

Proceed only if E1 is unsupported or inconclusive.

Preferred source:
MODIS/Terra MOD11A1 Collection 6.1 daily 1-km nighttime land-surface temperature, which spans the full 2001–2015 NAAMP period.

Scientific distinction:
route-average air temperature is already represented in existing analyses. E2 asks whether local nighttime surface thermal state differs among stops within the same route event and modifies species activation.

Before any frog endpoint readback, freeze:
- QC_Night quality rule;
- temporal matching to survey date;
- spatial extraction rule;
- route-relative / SiteID-relative centering;
- coverage gate;
- cross-fitted coefficient model.

Do not substitute daytime Landsat surface temperature for the primary E2 test because its overpass time is less aligned with nocturnal calling.

## E3. Local vegetation/substrate moisture — LAST ABIOTIC REMOTE-SENSING TEST

Proceed only if E2 is unsupported or coverage-inconclusive.

Use a prospectively frozen Landsat Collection 2 Level-2 spectral moisture metric from public imagery, intended to capture vegetated/substrate wetness not represented by open-water products.

One primary moisture index and one fixed spatial/temporal rule must be chosen before focal values are read.

## Stop rule

If E1–E3 do not materially reduce the concentration residual under their frozen rules, close the remote abiotic search.

Do not continue cycling through:
- additional spectral indices;
- more buffer radii;
- alternate rainfall windows;
- arbitrary land-cover variables;
- species subsets selected by result.

At that point the highest-priority unresolved mechanism class is biological/latent:
- species × route-night reproductive readiness;
- local demographic availability/abundance;
- spatially non-uniform social or chorus-state dependence;
- mixtures of these.

This follows the existing evidence that:
- a uniform species × route-night scalar state can reproduce concentration magnitude but is too spatially coherent for the observed near/far dependence profile;
- same-night stop conditions shared across taxa do not remove the target-taxon residual.

## Interpretation discipline

A failed remote-sensing mechanism does not establish absence of environmental causation. It narrows the measurable environmental quantities that can explain the observed configuration.

The purpose of this ledger is to distinguish hypothesis testing from an indefinite search for any environmental covariate that improves fit.
