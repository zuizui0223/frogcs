# v4.6 — The 29-site / 343-survey / 95-night total does NOT identify nightly spatial opportunity

**Date:** 2026-10-09. **Status:** mathematically demonstrated *study-design non-identifiability*, NOT a novel frog behavioural result. Locked JAE RC6 `main` unchanged; no new original frog calling, animal records, survey visits, water levels or metamorphs read.

## 1. New decisive finding from the published margins

[Ocock et al. (2024)](https://doi.org/10.1071/MF23181) report **29 physical study wetlands**, **343 site-level completed frog surveys**, **95 survey nights** across 2015–2020. This is only **343 / 95 ≈ 3.61 site surveys per survey-night** on average. The source does **not** report, in these three totals alone, the actual number of different *physical ponds sampled on each same night*, nor the number of species with enough genuinely observed opportunities for a frogcs-like deep `k ≥ 4` multi-wetland state.

This is not merely a matter of statistical power. The target **outcome does not exist as a measurable within-night configuration** on a night when fewer than four independent wetlands were genuinely surveyed.

Let `n_t` be the **number of distinct successfully sampled physical wetlands** on survey night `t`, with 95 nights each containing at least one sampled site. Let `M` count nights where `n_t ≥ 4`. The absolute published visit count limits `sum(n_t) ≤ 343`, so `343 ≥ 95 + 3*M`, yielding **M ≤ 82**. (This is only a mathematical loose **upper bound**, not an estimate of actual nights. It does not establish acoustic independence or source-code history.)

## 2. Actual synthetic proof: identical 29 / 343 / 95 margins admit radically different designs

The updated [source-independent v4.5 opportunity manifest QA](scripts/audit_ocock_visit_opportunity_manifest_v45.py) constructs **three fabricated** 2015-design CSV fixtures, with precisely **29 site IDs, 343 completed 5-min source opportunities, and 95 survey-night IDs**. In all three, source-provenance flags are **FALSE**.

| Fabricated scheme | Completed DISTINCT wetlands per night | Nights able to observe four or more separate sites |
| --- | --- | ---: |
| Concentrated visits | 2 nights × 29 sites, 1 night × 9 sites, 92 nights × 3 sites | **3** |
| Moderate spread | 58 nights × 4 sites, 37 nights × 3 sites | **58** |
| Very broad temporal coverage | 1 night × 6 sites, 81 nights × 4 sites, 13 nights × 1 site | **82** |

All three totals are exactly `(29, 343, 95)`. Each passes the same **aggregate-source** count check, despite wildly different frogcs-relevant opportunity structure. This mathematical counterexample is a **synthetic design fact**; **NONE of these layouts was inferred from the real Ocock programme**.

[GitHub Actions 37896010971 (SUCCESS)](https://github.com/zuizui0223/frogcs/actions/runs/37896010971) independently executed the code on these fixtures and checked their `3 / 58 / 82` results. It also confirms that repeat visits to **one wetland on a night** count once for the spatial breadth, not as two different locations.

**Source-only contract now reports:** distribution of *distinct actually completed physical sites per source night*, count of nights with `≥4` distinct surveyed sites, count with `<4`, and explicitly `null` values for how many of those nights have actual verified `≥4` calling sites for one species or strict prior history+metamorph linkage.

## 3. What each data level could actually support

| Source grain actually authenticated | The defensible ecological question | The claim it cannot deliver |
| --- | --- | --- |
| Just the published `29/343/95` margins and species-level across-all-years range maps | Programme totals and possible survey effort; very loose breadth bound | Number of observed `k≥4` nights, rain-driven simultaneous landscape chorus, species-specific historical spatial template |
| Full **metadata-only site×night completed-visit ledger**, with verified site continuity | Is deep within-night spatial allocation **measurable** in enough nights and independent wetlands? | Whether actual frogs called, whether histories line up, hydrology or subsequent breeding success |
| Survey-ledger + raw **species×site×visit call classes**, explicit genuine no-call opportunities, strict earlier baseline | Held-out **calling-state configuration and recurrent strong-site placement** in the available geography/time | Actual event-specific sound/water causal path or reproductive success |
| All of those + site/visit true water/hydroperiod + later stage-specific metamorph observations (with lag/effort) | Does history-dependent acoustic spatial expression **predict later recruitment** beyond local habitat persistence? | Parentage, individual memory, causal rainfall mediation without a manipulation or stronger assumptions |

A **published species heard at 27 of 29 sites over multiple years** still does **not** mean the species called at 27 sites within one concurrent survey night. Similarly, a given physical wetland having 12 visits over six years does not alone imply sufficient **crossed and comparable environmental events** to identify rain × prior strong-chorus interaction.

**New practical consequence:** Before requesting expensive original frog response exports or fitting any model, ask the custodian only for **source-authoritative, non-sensitive site×survey-night *opportunity* counts**. They can disclose just the histogram `{number of distinct completed wetlands per night -> number of nights}`, counts of valid 5-minute audio opportunities, dates and source-version coverage **without disclosing any species records or sensitive coordinates**. This single metadata response can settle whether a frogcs-type `k≥4` within-night test has sufficient physical sampling support. If it does not, pivot to slower between-year recurrence or downstream hydroperiod/payoff prediction as a **separate** analysis (never call it a replication of original route-night concentration).

## 4. Independent published sources and environmental context

- Ocock, J. F. et al. (2024), *Marine and Freshwater Research* **75**, MF23181, [DOI](https://doi.org/10.1071/MF23181): 343 site-level surveys, 29 study locations, 95 nights; rainfall/inundation linked to **published guild-level** calling and later metamorph metrics.
- [NSW BioNet Systematic Fauna Survey data](https://www.environment.nsw.gov.au/topics/animals-and-plants/biodiversity/nsw-bionet/about-bionet-atlas/systematic-fauna-survey-data) is available for registered analysis/export, whereas public sighting-only data are **not confirmed to carry all absent-visit opportunities**.
- [Ocock v4.5 method and ledger audit](V4_5_ORIGINAL_5MIN_CI_VISIT_LEDGER_AND_PAYOFF_GATE.md) preserves original categorical frog calling and the absence of a verified source response join.
- [Historical NSW environmental flow monitoring public catalogue](https://data.nsw.gov.au/data/dataset/historic-environmental-flow-monitoring) describes an umbrella archive with **1998–2012** temporal coverage. That published temporal frame does **not** cover Ocock's core **2015–2020** site-surveys; it cannot silently supply original water-state time series for those specific visits.
- [WaterNSW public real-time river discharge portal](https://realtimedata.waternsw.com.au/) and the gauge numbers in Ocock's published Table 1 offer potential source-verifiable **regional river-flow inputs**. They are not, alone, each site's **pond depth, inundation duration or a physically valid 29-site join**.

## 5. Reviewer's exact decision hierarchy

1. **Before outcomes:** verify a true visit-census ledger with original physical wetland identities; report `n_t` and the number of nights with `n_t≥4`, plus actual survey effort/noise/skip metadata.
2. **Before causal language:** separate environmental cue timing from site water availability, use genuine simultaneous reference sites/no-flow periods and do not conflate rain and flow with before/after calendar changes.
3. **Before reproductive-payoff claims:** verify observed metamorphs at same independently identified wetland following plausible developmental lags with stage-survey opportunity/detection.
4. **Before “external replication”:** freeze an external taxon×site×night evaluation and only count independently observed site configurations. The original Ocock/Sarker/NSW monitoring sources can overlap and do not become independent datasets by renaming them.

**Current state:** synthetic non-identifiability proof **PASS**; the actual **29-wetland survey-night distribution** is **UNKNOWN**, not inferred from the published totals. The frogcs JAE RC6 findings remain intact. No credentials, emails, data-custodian contacts, raw frog records, protected coordinates or original ecological outcomes were accessed.
