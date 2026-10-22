# USGS ARMI 2024 species-event grouping correction — v0.2, 2026-10-22

**Source-only structural repair before any bullfrog–greenfrog pair association was computed or its result read.** The original v0.1 hypothesis, sample, target taxa, weather covariates, site-disjoint folds, minimum effect/coverage gates, regularization and primary model remain unchanged.

## Observed source-forensic evidence, frozen first

Original source file `ARMI_2024_cricket_frog_data_release_2025_v1.1.csv`, 235,391 bytes, original SHA-256 `dafd388c7ccb79e08dbadd37a25c604473a8caf4ff5c8318532740acb56a04e4`, official MD5 `e201e24463d90e23c1f5f903e730e26c`.

A QA-only diagnostic (no pair co-occurrences or outcome models) in [workflow 39782928959](https://github.com/zuizui0223/frogcs/actions/runs/39782928959), receipt `exploration/ARMI_2024_SURVEY_SPECIES_DUPLICATE_AUDIT_RECEIPT_V0_1.json`, showed:

- **1,934** original rows, **798** unique 6-part `Project×Site×Date×Arrival_time×Observer×Method` events, as in the prior result-blind source preflight.
- **515** extra rows within **368** original species×6-part event keys; **275** distinct survey events with at least one repeated species entry.
- **367 of 368** repeated species/event groups have different `Compass_direction` (original FGDC documents this as approximate magnetic bearing to a calling individual/group).
- **101 of 368** differ in `Number_heard`, again consistent with recording different audible individuals/groups. One extra row is a full-row duplicate; one group has differing source `Comments`.
- **Zero** within-event conflicts in `Site_original`, `Latitude_WGS84`, `Longitude_WGS84`, `Wind_Beaufort` or `Cloud_cover_percent`; six-part survey identity fields themselves are fixed.
- No raw SiteIDs, event identifiers, animal recording contents or species-pair co-detection pattern were shared.

Consequently, a repeated *Species* name in a single **five-minute survey** does not necessarily imply a separate survey. Multiple bearings to different callers should not create extra Bernoulli events or artificially inflate sample size.

## Deterministic source-only grouping repair

Aggregate all rows with identical frozen six-part survey event key into **one** survey (same original 798 events). A target taxon has binary recorded-call detection **1 if any original row within that event has the exact named species**, otherwise 0, justified by FGDC's "All anurans heard were recorded." A `Species=none` sentinel is allowed only when no other species row is present in that same event.

- Do **not** interpret different `Compass_direction`/number heard as new independent surveys, and do not use `Number_heard` as an abundance/count outcome.
- Do **not** select a species row based on call direction, number of individuals, observer note, or strength.
- All generic-other-taxon richness is distinct species-name count, not number of audio/bearing rows.
- Preserve the original site-disjoint fold assignment over **all 343 original Project×Site** groups, including none detected.
- Do not modify original NAAMP data, methods, scientific claim, or RC6 release.

## Success criterion

The corrected source grouping must yield the exact same 798 survey and 343 site units as the response-blind preflight. Each event has consistent weather and all six identifiers. The source-species duplicate QA receipt remains available for audit.

**There is no change to the positive partner hypothesis or cutoff**. Only now is the original predeclared independent heldout presence model allowed to compute acoustic outcomes. If the original species detection sample gates fail, stop; never tune alternative thresholds or select different species to obtain a favorable result.
