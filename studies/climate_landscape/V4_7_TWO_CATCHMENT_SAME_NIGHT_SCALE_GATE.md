# v4.7 — Scale correction: two catchments cannot be pooled into one frog chorus-night

**Date:** 2026-10-09 JST. **Work type:** source-backed sampling-frame analysis and synthetic, response-blind proof. **No new amphibian counts, night-level real original data, hydrology records or experiments read.** JAE RC6 `main` locked and unchanged.

## 1. New source-backed biological constraint

[Ocock et al. (2024)](https://doi.org/10.1071/MF23181) reports **29 study wetlands**, partitioned into **15 Gwydir Wetlands** and **14 Macquarie Marshes**; **343 completed site surveys** comprise **195 Gwydir** and **148 Macquarie**, across **95 survey nights**. These are two separate catchments, not stops along a single NAAMP route. The source's stated research outcome combines taxon-wise 5-minute frog calling categories into a **flow-dependent taxon guild call measure**, with separate later metamorph follow-up.

The paper's total-site and visit counts are not evidence that four or more physically independent sites **within the same catchment and environmental cue context** were recorded on a single night.

A same-date cross-catchment combination does **not** define one shared taxon×route-night calling state. Within-catchment co-sampling is only a **necessary condition**; neighboring wetlands might still be too far apart, on different watercourses, or exposed to different rain/inundation/temperature histories for a coherent common-night ecological interpretation.

## 2. A stronger non-identifiability result than v4.6

v4.6 established that one published 29/343/95 margin can reflect 3, 58, or 82 nights with `≥4` different sites **pooled across the entire programme** in different **synthetic** schedules. None of those is the real 2015–2020 timing.

Now add the *real published regional margins*: **195 Gwydir visits and 148 Macquarie visits** and site caps of 15 and 14.

The new [v4.7 source-only catchment/night contract](scripts/audit_ocock_catchment_night_aggregate_v47.py) constructs a different **fabricated** 95-night schedule that simultaneously satisfies all six published pooled and regional totals:

- Gwydir: `5 nights × 3 wetland visits + 90 nights × 2 = 195`;
- Macquarie: `74 nights × 2 wetland visits + 21 nights × 0 = 148`;
- combined visits = **343**, distinct source-defined survey nights = **95**, source frame caps 15/14 wetlands.

In this hypothetical schedule, **74 nights would appear to have at least four wetland surveys if the two catchments were pooled by night**, but **ZERO** nights contain four different completed wetland surveys *inside either catchment*.

**This is not a finding about the Ocock field data.** It is a mathematical counterexample that validates the need for a region-aware sampling-frame check. It does not assert that the nightly events truly coincided across catchments, that all 29 study sites were visited in this specific schedule, or that any frog species called.

**Therefore even a source-authenticated pooled `n≥4` nightly statistic is insufficient** for frogcs-like within-landscape spatial organization. A date-matched multi-basin dataset might instead support a separate **regional synchrony** hypothesis if its events and environmental histories were appropriately matched, but cannot by itself identify one local route-scale chorus configuration.

## 3. Minimal privacy-safe source request is now smaller than an original frog export

The following already-aggregated five-column record would be enough **as a first step** to decide whether within-catchment `k≥4` opportunity even exists:

| Authorized column | Meaning |
| --- | --- |
| `source_night_alias` | Source-defined actual comparable survey night ID, e.g. a privacy-safe original night's alias |
| `catchment` | Either `Gwydir` or `Macquarie`; no exact location |
| `n_distinct_wetlands_completed` | Number of distinct physically verified wetlands with completed comparable 5-minute frog censuses |
| `n_completed_five_min_visits` | Total source-authoritative five-minute completed site visits on that catchment/night |
| `source_version` | Original survey/manifest version identifier |

The [validator](scripts/audit_ocock_catchment_night_aggregate_v47.py) rejects individual species/calling fields, non-whitelisted regions, impossible site counts (>15 Gwydir / >14 Macquarie), more sites than visits, negative counts, and duplicated catchment-night rows. It **does not** download sensitive site IDs, actual frog responses or ancillary hydrology. If the original `343 / 195 / 148 / 95` margins do not match, it reports a source/version mismatch without creating fabricated zeros.

**Further, even a positive result is NOT a biological result.** Any group with four completed wetlands must still be validated for ecological/spatial independence, temporal alignment, actual same-species opportunities, correct original audio categories and strict prior species×physical-site history. An original environment/larval dataset with source-stable site ID and plausible lag is still needed for downstream payoff claims.

## 4. Operational decision and provenance

- **Existing JAE RC6:** strong chorus and rain-selected historically recurrent sites across separated NAAMP route stops; no individual return or breeding success asserted.
- **Ocock 2024 published:** inundation extent associated with call-based breeding attempts, antecedent hydroperiod/river flow with metamorph recruitment; **authors' result**.
- **v4.7 new contribution:** a **source-design impossibility warning**, demonstrated with synthetic data; original 29/343/95 and even 195/148 splits do not establish that within-catchment night-level four-site tests are observationally possible.
- **No original per-night site configuration obtained or reconstructed**. Anonymized five-column source aggregate should be the first request **if the author chooses to contact an authorized data custodian**; no contact or access attempt has been made to registered NSW fauna database.
- **Do not repurpose later NSW statewide programme reports (2019–2024; 2024–25) as the missing Ocock 2015–2020 visit ledger**. Even a source claiming all sites visited in one later season does not establish the earlier programme's precise night-level effort.

**Stopping rule:** if authentic `n_distinct_wetlands_completed` is almost always <4 within the same catchment/night or the physical sites have no independently verifiable historical recurrence/opportunity, formally rule out **this data source** for a frogcs `k≥4` spatial configuration replication; do not interpret it as a null ecological rain×history result. A narrower local hydroperiod × metamorph prediction may still be possible once its appropriate source-grade data actually exist.
