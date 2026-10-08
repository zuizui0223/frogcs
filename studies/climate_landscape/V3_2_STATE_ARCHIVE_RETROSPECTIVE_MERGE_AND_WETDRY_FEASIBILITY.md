# v3.2 — Iowa state-native NAAMP archive provenance and hydrology feasibility

**Date:** 2026-10-08. **Status:** independently researched archival evidence and a response-blind *future-data* feasibility specification. **No 2010–2015 Iowa-native wet/dry values have been seen**. JAE RC6 is frozen and unchanged.

## What new original Iowa sources establish

### 2013: contemporaneous NAAMP data existed separately

[Iowa DNR, *Iowa's Frog and Toad Call Survey 2013*](https://publications.iowa.gov/19011/56/Iowa%27s%20frog%20and%20toad%20survey%202013.pdf) describes **NAAMP monitoring separately from the traditional survey**, and its Table 2a explicitly summarizes **NAAMP species-detection records for 2010, 2011, 2012 and 2013**. The same report gives 37 NAAMP routes reporting data in 2013 (33 with three runs). This is contemporaneous evidence of an archived NAAMP-era *species-response programme*, **not evidence of stop-event water-state retention or a downloadable raw table**.

### 2014: partial collection-protocol overlap, but no variable guarantee

[Iowa DNR, *Iowa's Frog and Toad Call Survey 2014*](https://publications.iowa.gov/19011/2/Iowa%27s%20frog%20and%20toad%20call%20survey%202014.pdf) states that the ten-stop NAAMP routes were added in 2010 and that **most of the information collected overlapped** with the traditional survey; the report nevertheless presented the two survey types separately. The report lists environmental variables such as air and water temperature for the *traditional* survey, but does **not** individually prove that wet/dry or water temperature was captured, retained and joinable for every NAAMP route/stop/run from 2010 through 2015.

### 2023: NAAMP and traditional programme data were joined retrospectively

[Shepherd (2023), *Frog and Toad Call Survey Results for Iowa, 2023*](https://www.iowadnr.gov/media/1751/download?inline=), Methods p. 2, explicitly describes volunteers recording whether the wetland stop was **wet or dry**. Results p. 3 states that work **has been done to combine** formerly separate NAAMP and traditional records back towards the 2010 NAAMP start, enabling a ten-year trend assessment. However, its actual plotted long-term trends begin around **2013**, and Discussion p. 6 says the programme is **still gradually adding years of combined data**. Consequently this publication does **not** establish a fully harmonized 2010–2015 event-level table, much less the retention of original stop-event wet/dry or water-temperature fields. It is a valuable lead for a **state-native historical crosswalk or source archive**, not verification of its coverage.

### Contemporary public database and archive custody

The [VWMP public portal](https://programs.iowadnr.gov/vwmp/) displays a county-select **Download Report** control; the public landing page describes volunteer login for data entry. The visible landing page alone does **not** establish historical row-level data downloads or the inclusion of wet/dry in downloaded reports. No login bypass, protected endpoint use, county-level report download or volunteer data retrieval was attempted.

The [current Iowa DNR survey page](https://www.iowadnr.gov/programs-services/volunteer-opportunities/wildlife-monitoring/frogs-and-toads/survey) says monitors must **submit data online and mail paper datasheets**. Again, this establishes current handling rather than verified historical sheet preservation. Official custodian contact: **vwmp@dnr.iowa.gov**.

### USGS export remains a definite negative

The checksum-verified original [USGS `Stops.csv` schema audit](https://github.com/zuizui0223/frogcs/actions/runs/37774857243) counted **21,934 Runs** and **219,340 Stops** and found **zero direct wet/dry / local hydrology field names** in the 14-column national stop table. No `Counts.csv` was accessed. This result is unchanged.

## The decisive custodian question is now narrower

**Was per-stop wet/dry recorded and retained in Iowa's original 2010–2015 ten-stop NAAMP surveys, and were any such raw fields included in the later **partially assembled** traditional+NAAMP combined database (rather than only response/date/route IDs)?** Ask for:
1. Annual blank survey sheets / instructions **specifically used on NAAMP ten-stop routes** in 2010, 2011, 2012, 2013, 2014 and 2015, especially the definitions of `Site Wet or Dry`.
2. The native merged database **field list / dictionary** and the 2010–2015 old-to-new **route/stop/event identifier crosswalk**. If wet/dry was not included in the merge, ask whether pre-merge state spreadsheets or scanned paper forms survived.
3. **Year × route type × event × stop metadata-only completeness**: number of observed W/D values, missing/unknown records, duplicate event keys, and whether the same stop is W and D on different visits.
4. Stop establishment and relocation history; a 2021 route map cannot alone validate physical continuity during 2010–2015.
5. Source-use restrictions, if any. No species call records or observer PII in the first enquiry.

**Crucial distinction:** being present on a blank form is not evidence that a volunteer filled it in, data entry transcribed it, it survived the merge, or it varied sufficiently to discriminate environmental mechanisms.

## Frozen acceptance workflow if Iowa-native source exists

Before reading frog outcomes, ingest only a field-whitelisted environmental extract. The prescribed summary is **descriptive**, not a fitted frog model:
- rows with verified original ten-stop NAAMP route type and 2010–2015 dates;
- route-year / stop-event count and W/D completeness; missing/unknown stays **missing**, never coded dry;
- frequency of W and D at each stable physical listening site, including **within-site W↔D changes** across visits;
- **within-route-night mixtures** of wet and dry stops, needed to test the local environment hypothesis against a single common route-night state;
- geography and time support; flag mismatched route/stop IDs, stop relocation, duplicated event keys and protocol changes;
- evaluate *coverage of all available eligible routes*, not only the two sites previously highlighted by postselected satellite pixels.

**If the same site is always wet (or always dry)**, its W/D value is confounded with stable site differences and **cannot test dynamic within-site local hydrology filtering**. If every route-night has uniform W/D, the data **cannot distinguish** shared weather activation from within-route local hydrological filtering. If W/D changes within sites but is a coarse observation, it is still not hydroperiod, water depth, breeding success or a movement observation.

No arbitrary favourable minimum threshold is set before seeing the coverage distribution; before any outcome analysis, record a defensible prospective sample-size/informativeness rule **from metadata only**, then freeze it and prevent adaptive tuning.

## Completed implementation and QA — 2026-10-08

State-native W/D availability remains **UNVERIFIED**. However, the future-data **metadata-only** adapter is now executable and has passed its source-independent synthetic QA:

- `scripts/audit_iowa_state_native_wetdry_feasibility_v32.py` admits only `route_id, route_type, stop_number, event_id, survey_date, wetdry` with optional `site_id, source_form_version`. No species or `CallingIndex` column is allowed.
- Rejects pre-2010/post-2015 dates, non-NAAMP route type, stop positions outside 1–10, duplicated route-event-stop entries, inconsistent survey dates, and unrecognized W/D codes; **no missing value is recoded dry**.
- Reports 10 **recorded stop rows** separately from 10 **nonmissing observed W/D statuses**. Primary input adequacy for a complete spatial W/D configuration requires the latter; 10 header rows with missing W/D are insufficient.
- Reports both within-event W/D contrasts and a separate count of nominal route–stop locations observed as W on some dates and D on others. Neither proves stable 2010–2015 physical sites or a response mechanism.
- [Original v3.2 smoke QA](https://github.com/zuizui0223/frogcs/actions/runs/37778362584) **SUCCESS**; expanded [full-10-vs-complete-W/D synthetic QA](https://github.com/zuizui0223/frogcs/actions/runs/37779133163) **SUCCESS** after fixing a test-fixture newline bug that caused the intervening attempt [37779090147](https://github.com/zuizui0223/frogcs/actions/runs/37779090147) to fail. No real historical state-native observations were involved in any of these test runs.

### Ecological decision matrix (necessary contrasts, not claimed support)

| Source-only finding | Consequence |
| --- | --- |
| No historical event-level state-native W/D recovered | **Local hydrology mechanism untested**; close this Iowa mechanism route |
| W/D present but all sites have a fixed status | Stable habitat filter only; short-term within-site hydrostate switching **not identifiable** |
| W/D varies through time but every surveyed route-event is all wet or all dry | Route-wide hydrostate could mimic a broad shared state; **no within-route local contrast** on those nights |
| Full ten-stop route-events show both W and D, and at least some physical stations switch status over comparable visits | Dynamic local-state filtering becomes a **testable competing generator**, conditional on provenance, sufficient independent data and a separately frozen outcome design |
| Wet/dry status plus historical stop relocation evidence missing | Nominal stop W/D changes could reflect relocation or inconsistent coding; **no physical-site causal interpretation** |

Across-run wet/dry differences may be driven by breeding season, observation, rain timing or form-version changes. Before any frog endpoint, freeze how **run window, calendar date, observer and site ID** will be controlled, and check year/route coverage. Do not interpret wet/dry alone as water depth, hydroperiod, successful spawning or an experiment. **No p-value, model fit or mechanism claim is generated by this metadata QA.**

## v3.3 source-integrity correction — 2026-10-08

A critical source-identity error is now explicitly guarded against: **a route stop number is not a stable physical wetland identifier**, and **ten submitted row records do not mean ten stops were surveyed**.

The [metadata-only feasibility script](scripts/audit_iowa_state_native_wetdry_feasibility_v32.py) now permits **optional, whitelisted** `site_id` and `stop_surveyed` source fields, but never invents either field if absent. It distinguishes:

- `n_fully_observed_10_stop_route_events`: ten rows with actual nonmissing W/D; descriptive only if skip information is absent;
- `n_complete_wd_events_with_explicit_all_ten_stops_surveyed`: all ten W/D are present **and** a source field explicitly confirms all ten stops were surveyed; zero if `stop_surveyed` is missing;
- `n_nominal_route_stops_with_within_stop_wet_and_dry`: a nominal stop number showed both water states over multiple records, **not** a proof of the same physical listening location;
- `n_recorded_site_id_consistent_switches`: the nominal stop showed W/D switching while the supplied SiteID value is nonmissing and identical across its records. This is only a necessary database-consistency condition, not independent historical site confirmation;
- `n_switches_with_missing_or_conflicting_recorded_site_id`: apparent switching that must be withheld from any physical-site interpretation.

A reported `stop_surveyed=N` with an observed W/D value is rejected as an inconsistent canonical input rather than silently used. If the raw source does not carry a survey-status field, stop-level opportunity completeness is **not independently established** and must be audited using original form status/record rules.

**Further statistical boundary:** even with reliable W/D, it is observed contemporaneously with the calling survey and can share observer and site-selection processes. It is not randomized hydrological manipulation; individual movement, direct rainfall causality and reproductive success remain unmeasured. Any subsequent wet/dry–chorus association requires strict event/season/observer adjustment and out-of-block validation before a mechanistic claim.

**Public portal limit:** the [VWMP landing page](https://programs.iowadnr.gov/vwmp/) publicly advertises a county-level "Download Report" control, but this page does not establish its file type, contents, data-year scope, environmental schema, or access to original NAAMP stop-event data. No historical W/D table was fetched and no login/credential or private endpoint was used. The custodian enquiry remains the correct next step.

### Test status

The extended synthetic test now covers full-ten W/D, missing W/D, skip contradictions, stable versus conflicting recorded SiteIDs and absent SiteID. **A passing workflow run must be confirmed before treating the updated parser as validated.** It uses no actual Iowa-native W/D values or frog species counts.

## Stop decisions

- **National USGS source:** permanently insufficient for direct stop wet/dry.
- **State-native Iowa source:** possible, **not retrieved**; specific retrospective data merger is a promising enquiry target.
- **Forest canopy → frog relocation:** still unestablished, with original Annual NLCD C1.2 and independently dated 2010–2015 site continuity unavailable.
- **Further NAAMP frog-outcome fitting:** not authorized; independent JAE RC6 unchanged.
- **External email:** current branch has an **UNSENT** draft; no contact made by this audit.
