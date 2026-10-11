# v4.5 — Original five-minute call index and authorized survey-opportunity source contract

**Date:** 2026-10-09 JST. **Evidence status:** verified published method + a passing **synthetic-only** authorized-data audit. No new frog or hydrology data collected, downloaded or modeled. JAE RC6 remains frozen on `main`.

## New positive finding from the primary paper, not inferred from BioNet fields

[Ocock et al. 2024, `MF23181`, Methods and original outcome construction](https://connectsci.au/mf/article/75/2/MF23181/194409/Managing-flows-for-frogs-wetland-inundation-extent) reports:

- **29 wetlands** across Gwydir (15) and Macquarie (14); **343 actually completed site surveys** over **95 survey nights**, in 2015–2020. Not every site was surveyed every year because access was constrained.
- Each evening after sunset, surveyors completed a **5-minute auditory census** and a separate **one-person-hour visual-and-auditory encounter survey (VAES)**; the VAES entailed two trained observers searching 30 min. These are **different observation methods**, not duplicate measures to average.
- Species-specific raw five-minute calling classes: **rare (1–5 individuals calling), common (6–10), abundant (11–20), very abundant (>20)**.
- For the paper's focal *flow-dependent guild* response, the authors transformed those **positive classes** to lower bound scores **1, 6, 11, 20** and summed across flow-dependent species at each **site-survey**. This gives the published **guild-level** calling response (the paper describes potential maximum of 120), not the original taxon×site categorical pattern. Do not confuse this with **BioNet `abundanceScore`**, which the Feb 2026 BioNet v6.3 dictionary explicitly defines for PLANT plot abundance.
- Recently metamorphosed frogs were identified during VAES using remnant tail stubs and species-dependent body-size criteria. **An observed metamorph is an observed stage**, not proof that the immediately previous acoustic survey caused that individual's recruitment, and a metamorph absent from sightings could be undetected.
- The source authors' paper already reported **different hydrological predictors** for the guild-level calling index and the total count of recently metamorphosed frogs: inundation extent vs antecedent 90-/120-day or preceding-months river-flow conditions. This is published background, not a new frogcs finding.

**Critical scientific implication:** the existing published fitted calling response is a *sum over taxa*. A study of historical **species × physically distinct wetland** chorus recurrence needs the **original pre-aggregation species-level 5-minute call class**, a valid source opportunity denominator including recorded nondetection, and a later life-stage outcome at the same wetland.

### Zero category is not a reconstructed observation

The positive class definitions contain **1/6/11/20**. A **zero** at site×night×species is admissible only if the original 5-minute listening was actually completed, the protocol included the taxon in the eligible detection frame, valid no-call coding and effort are source-authenticated, and acoustic detection/masking limitations have been assessed. Empty BioNet rows must not be recoded zero. A recent metamorph observed at a subsequent visit does not retrospectively validate a missing earlier auditory survey.

## v4.6 essential spatial-availability correction — source publication margins do not specify true same-night breadth

The original **29 physical sites, 343 completed site visits, 95 survey nights** imply only **3.61 sampled sites per night on average**. The published three marginal totals do **not** identify the count of nights with four or more independently surveyed wetlands — a necessary condition before even attempting to reproduce the frogcs `k≥4` within-taxon deep cross-site calling configuration.

A synthetic-only [v4.6 mathematical/source-opportunity audit](V4_6_PUBLISHED_MARGINS_VS_NIGHTLY_MULTISITE_OPPORTUNITY.md), verified by [run 37896010971](https://github.com/zuizui0223/frogcs/actions/runs/37896010971), constructs three **FABRICATED** observation schedules that each have exactly **29 sites / 343 completed visits / 95 nights**, but only **3**, **58** and **82** nights with `≥4` distinct completed sites, respectively. None is the real Ocock schedule.

The source-only ledger program now returns the **histogram of distinct physical wetlands actually surveyed per source-defined night**, the count of nights with `≥4`, and `null` for actual species-specific chorus or metamorph counts. Repeated surveys at one pond on a night are **one spatial site**, not independent locations. This distinction is prior to and independent of any inference about rain or breeding success.

**New minimum custodian-data request:** ask **first** for only the anonymized histogram `n_distinct_5min_completed_wetlands_per_night` and original method/site-night linkage metadata (no protected coordinates, frog detection lists or private observer IDs). If full deep `k≥4` configurations are not observable in enough nights, no amount of later rain/water modelling can rescue an exact spatial replication.

## An executable authorized-source **opportunity-only** gate

[Metadata-only checker](scripts/audit_ocock_visit_opportunity_manifest_v45.py) with [source-independent GitHub Actions 37893965568 (SUCCESS)](https://github.com/zuizui0223/frogcs/actions/runs/37893965568).

The checker accepts exactly these metadata fields and **refuses all extra response, observer, or location columns**:

`physical_wetland_alias, survey_night_alias, survey_visit_alias, survey_date, survey_status, audio_method, auditory_effort_minutes, source_form_version`

Source-documentation requirements:
- `physical_wetland_alias` must be a **nonreversible authorized project alias** for an actually verified physical wetland; **not** a generalized GPS point, ad hoc join, or protected coordinate.
- `survey_night_alias` must come from the source programme and group true same-night surveys, **not** reconstructed merely by matching a calendar date, particularly where sampling passes midnight.
- `survey_visit_alias` is **one original opportunity**, not one frog species record. For NSW BioNet, `eventID` and `visitID` are duplicate **aliases of the same census** and cannot be counted twice.
- `survey_status` is `COMPLETED`, `NOT_VISITED`, or `ABORTED`. Missing site×night combinations are **not** fabricated visits; if the source has unattempted scheduled wetlands, they may be recorded separately, never as completed.
- `audio_method` is a separately attested five-minute listening method; `auditory_effort_minutes` should be exactly 5 for a complete auditory opportunity. Actual masked/partial audio should not be declared `COMPLETED` without a primary field-protocol basis.
- `source_form_version` must identify the real source dictionary/recording instrument, not simply a date invented after extraction.

The script counts unique completed site-survey opportunities, physical-site aliases and survey-night aliases, compared **descriptively** with the paper's 343/29/95. It rejects duplicate visit IDs, extra fields such as `taxon` or `calling_index`, unapproved methods, invalid duration and purported complete visits on unvisited rows. It **never outputs the input aliases** and does not load frog responses. The synthetic fixture demonstrates that *exactly matching counts is still not evidence of historical authenticity*.

**Explicit verification states always remain false** until source attestation: genuine original files/dictionary, historical site continuity, effort and verified zero-call policy, water and metamorph linkage, and results. This prevents an inadvertent “343 rows == analysis-ready” inference.

## Minimal scope of any authorized data-custodian request (NOT SENT)

If a study author later chooses to pursue original records, the high-value request is **not a generic export of frog sightings**. The smallest scientifically interpretable package is:

**A. Audit-only non-sensitive counts and dictionaries first:**
1. Confirm whether the original 343 completed **site×visit** audio surveys can be enumerated *independently of any sighting*, including sites with no frog calls, missed visits, partial/masked data and duration.
2. Verify retained original `rare/common/abundant/very abundant` **species-specific** source codes and whether completed-listening zero counts are explicitly known versus only inferred.
3. Confirm a documented join from original site aliases and survey/visit identifiers to (i) nightly species calls, (ii) local hydrology (depth, inundation, persistence/flow), and (iii) separately observed metamorphs/tadpoles with dates and effort.
4. Report whether years before each target held-out evaluation could supply truly **strictly prior species×site strong-call history**, with method consistency, and whether source events have independent/no-flow controls.
5. Confirm permissible use/licence and how to cite the source/avoid leaking sensitive locations and volunteer information.

**B. Only if A is supported and permission is granted:** use a restricted approved source view with source-defined aliases, *not* protected coordinates or private observer IDs; retain survey opportunities and outcomes in an authorized workspace; never upload unapproved sensitive files to public GitHub.

Original paper's Data availability: frog survey records are through NSW BioNet, while **ancillary data are available on request**. Official BioNet Systematic Fauna Survey offers logged-in analysis/export, but a publicly accessible sighting-only OData response has **not** been shown to supply the 343-visit denominator or source-call categories. The public 2025 blank fauna submission workbook is not the same as the registered historical database export.

## The ecological question if the source passes

> **Among physically stable wetlands where a focal species could actually have called, does strictly prior taxon-specific strong chorus history predict later metamorph recruitment beyond objectively measured water availability/hydroperiod, or are historical high-chorus sites sometimes acoustic hotspots with poor larval persistence?**

**Do not overstate the target estimand.** Historical strong-site association is a *predictive modifier*, not evidence of individual memory or habitat adaptation. Inference about reproductive **payoff of a calling event** further requires matching actual breeding attempts to a plausible larval lag and source; merely recording metamorphs in a later survey in the same wetland does not establish parentage/event-specific survival.

The proposed primary practical outcome would first be **held-out site/year metamorph occurrence or count prediction** with detectability/opportunity correctly represented; separate species-specific versus guild aggregate tests require actual data support. Compare strict-prior chorus history against contemporaneous hydroperiod with a specified out-of-year/site blocked validation. No fitted regression, rain-sound mediation, larval fitness or species movement claim is licensed by this audit.

### Stop decisions

- If the complete original 343 site-survey **opportunity manifest** is inaccessible: **STOP: not identifiable from public sightings alone**.
- If only the authors' guild **summed** calling index exists but no species-level original call categories: **STOP species×site chorus-history claim**; an aggregate community-level prediction might be a distinct, narrower study.
- If hydroperiod and metamorph follow-up are not linkable at the same real physical wetland with an interpretable lag: **STOP payoff hypothesis**; calling and hydrology associations remain descriptive.
- If eligible species/history variation or genuinely independent validation years/sites do not exist: **STOP out-of-block replication claim**.
- No unstated zero filling, arbitrary new rain windows, pseudo-replication of repeated same-site visits or double-counting other NSW programme reports.
- **RC6 JAE main is unchanged**. No unauthorized data request, external email or experimental animal manipulation has occurred.
