# v3.1 — Iowa historical station / local-water-state source gate

**Date:** 2026-10-08. **Classification:** source-only, response-blind follow-up to v3.0. **Scientific authority:** this is a separate exploratory climate–landscape study; it does not amend, reanalyse, or provide confirmation for locked JAE RC6.

## Why this gate precedes another raster or acoustic test

The frozen 2011–2013 Collection 1.0 screen found only five forest→nonforest 30 m cells within 250 m of 2/70 nominal Iowa stations (three near 360104 stop 3, SiteID 6613; two near 360412 stop 7, SiteID 7247). The subsequent original USDA Science TCC v2025.6 comparison found modeled 2011→2013 canopy differences of −15, −29, and −7 percentage points at the three 360104 cells, versus 0 and 0 at the two 360412 cells. These cells were selected **after inspection of categorical changes**; the comparisons do not establish a region-wide disturbance, calibrated image accuracy, loss of breeding water, or an effect on frogs. See the frozen v2.2, v2.3 and v3.0 reports.

The independently published **Iowa DNR Frog and Toad Call Survey Results for Iowa, 2025** describes:
- Iowa's participation in USGS NAAMP beginning in 2010 and the adoption of 84 NAAMP routes, with the state continuing routes after the national program ended in 2015;
- ten approximately fixed stops on NAAMP-style routes, contrasted with traditional volunteer-selected routes;
- **site-specific wet/dry status collected in its contemporary protocol** together with calling and observation covariates;
- earlier protocol changes, notably five-minute listening starting in 2008 and species-identification changes around 2009.

The contemporary 2025 wet/dry field is an important **data-availability lead**, *not proof that the original USGS 2009–2015 Stops.csv contains a usable wet/dry variable*. Equally, the Iowa DNR public 2021 station maps/description sheets are useful habitat-context documents but do not alone verify 2010–2015 stop continuity. The route-description sheets for 360104 and 360412 have blank route-establishment dates.

An additional provenance issue must remain visible: the original NAAMP source metadata used in v2.1 include **2009** for route 360110, despite the later Iowa DNR report's broad statement that participation in NAAMP began in **2010**. This is a **record-provenance question**, not evidence of an invalid 2009 survey; reconcile the source date and route type before treating all early Iowa route records as a homogeneous program.

## Frozen sources to reconcile

1. Original checksum-pinned USGS NAAMP Runs.csv and Stops.csv, and coordinate source already used by the source-only cohort; hashes in v2.1 receipt. **Do not open Counts.csv** for any of the new routes.
2. [Iowa DNR current survey and route map index](https://www.iowadnr.gov/programs-services/volunteer-opportunities/wildlife-monitoring/frogs-and-toads/survey); [official 360104 route description](https://www.iowadnr.gov/media/1953/download?inline=) and [360412 route description](https://www.iowadnr.gov/media/2011/download?inline=), both dated January 2021.
3. [Iowa DNR 2025 annual report](https://www.iowadnr.gov/media/9064/download?inline=). Its contemporary protocol should not be assumed backward-compatible.
4. [USGS NAAMP historical program/protocol](https://www.usgs.gov/centers/eesc/science/north-american-amphibian-monitoring-program) explicitly allows exceptional stop relocation and notes route-map updates were not always communicated.
5. [USGS Annual NLCD Collection 1.2 Land Cover](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-12-land-cover) and [Collection 1.2 Land Cover Confidence](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-1-land-cover-confidence); do not substitute Collection 1.0 or a masked TCC layer for those missing original C1.2 raster outputs.

## Source request / document search — narrowly scoped and not sent

For the **original 2010–2015 NAAMP-era stations**, seek from Iowa DNR's volunteer monitoring program or original field archives:

**A. Historical physical-site identity**
- dated first-established route/stop waypoints, field maps or stop descriptions for **360104 stop 3 (SiteID 6613)** and **360412 stop 7 (SiteID 7247)**;
- change logs for stop relocation, roadworks, inaccessible stops, renumbering or stop retirement during 2010–2015;
- which station/coordinate version was active in **2010–2011**, **2012**, and **2013–2015**;
- provenance for **360110's 2009** USGS source entry (if extending beyond the two focal source-QC sites).

**B. Repeated local water state**
- whether per-stop **wet/dry** (or standing-water presence, level, inundation, hydroperiod) was actually recorded **in the original 2010–2015 Iowa NAAMP surveys**, as distinct from current 2025 forms;
- if yes, whether observations can be linked **without species outcomes** to date, original route number, stop number, physical SiteID and run identifier;
- a field dictionary specifying unknown, skipped, missing, season and dry classifications; recording protocol changes, QA and archival coverage;
- if unavailable, explicit acknowledgement of missingness/non-retention rather than treating a present-day protocol as evidence of historical hydrology.

No request was sent by this audit; a public route PDF and stable archived SiteID remain **necessary but insufficient** for historical physical-site verification.

## Data gates before any additional frog-response readback

| Gate | Minimum verifiable result | If absent |
| --- | --- | --- |
| H1 historical site | Dated evidence that the *same physical listening stop* was occupied during the environmental and calling comparison years; relocation records accounted for | Station-level forest/canopy → calling inference prohibited |
| H2 annual source identity | Original **C1.2** land-cover and confidence at the same preselected five 30 m cells and their buffer context, 2011–2013, with year, tile/grid, layer identities and content hashes | Keep older C1V0/TCC disagreement descriptive; do not relabel it latest NLCD validation |
| H3 local water-state availability | Actual historical stop-event water state with a validated missingness policy, a source-only coverage table and no species-response columns | Do not claim a test of local hydrology; use only a future independently measured fixed-site study |
| H4 independent ecological design | A source/geometry-driven inclusion rule and sufficient independent route/year/site contrasts fixed **before** looking at any newly selected frog outcomes | No new-route Counts.csv inspection to rescue an environmental exposure pattern |

**Do not infer H3 from the 2025 Iowa survey document.** If future historical wet/dry data are obtained, treat them as an observation-process/hydrology proxy requiring validation, **not a measure of breeding success or water volume**. Freeze the response-blind input and coverage before specifying any acoustic allocation test.

The current source-only v2.1 eligibility table has just **one pre-2012 recorded survey year** for 360104 (three runs in 2011) and **two pre-2012 years** for 360412 (four runs in 2010–2011), which further limits pretrend identification. A single 2012 category change is not a confirmed natural experiment.

## Close-or-continue rule

**Present classification: insufficiently identified environmental-to-acoustic causal mechanism.** The source-selected canopy candidate at 360104 remains interesting as a *terrestrial edge/buffer exposure*, not evidence that the water in the roadside drainage ditch changed or that reproductive activity moved. At 360412 the nominal NLCD loss is not reproduced by the independent quantitative canopy-output comparison.

Continue only if new **historically dated station evidence** or **historical stop-event wetness data** are located, and if a C1.2 same-version source is independently verified. Otherwise, retain the five-pixel measurement caution as a method/quality note; do not deepen frog-outcome selection, retune 2012, re-open the negative climate prediction, or elevate either site to a published causal finding.

No new NAAMP species/call-index outcome was accessed for this document. No WFTS work was initiated. JAE RC6 remains unchanged.

## Historical field-protocol finding, 1995–2003 (new provenance evidence)

A much earlier primary public source corroborates that Iowa *actually collected* local water-state information long before the modern form:

- Iowa DNR Wildlife Diversity Program, *Iowa's Frog and Toad Survey, 1995–2003* (historical report, published in 2005), [official state-hosted PDF](https://publications.iowa.gov/18993/1/2005_FrogToad_rpt.pdf), Methods p.1: at each listening site observers recorded general wetland condition **wet/dry** and **water temperature**. The report states that its typical routes contained **five volunteer-selected wetlands**, and its 1995–2003 locations had been GIS digitized.
- The [current two-page Iowa DNR datasheet](https://www.iowadnr.gov/media/1759/download?inline=) explicitly includes **Site Wet or Dry (W/D)** at each numbered stop, including NAAMP route-format stops.
- Shepherd (2025), [official DNR annual report](https://www.iowadnr.gov/media/9064/download?inline=), Methods pp.1–2 states that NAAMP's 84 random-route framework was added to Iowa's effort in 2010 and was absorbed into the Iowa DNR program after the USGS ended national coordination in 2015.

**Important distinction:** the 1995–2003 historical evidence documents Iowa's **traditional volunteer-route recording practice**, not completeness of **2010–2015 USGS-delivered NAAMP Stops.csv** or Iowa's own original per-run digitized NAAMP exports. The original report's five-site route design is not interchangeable with NAAMP's ten-stop routes. This strengthens the case for **archive discovery**, *not* the inference that a matched hydrology-calling dataset is already usable.

### Source-only NAAMP schema test, no results presumed

Implementation: `scripts/audit_original_naamp_stop_hydrology_header_v31.py`; [GitHub Actions gate](https://github.com/zuizui0223/frogcs/actions/workflows/iowa_naamp_historical_wetness_schema_v31.yml). It downloads only checksum-pinned original `Runs.csv` and `Stops.csv`, inventories exact column names and any hydro/water/wet/dry candidates, and writes a source-only JSON receipt. No `Counts.csv` or calling response is accessed. A field with a suggestive name is *never* automatically treated as validated contemporaneous standing water.

If the USGS export has **no wet/dry field**, this only establishes *non-preservation in that particular USGS export*. It does **not** show the original Iowa DNR paper forms or state-run system never collected the field. The right next access question is a **source-record archive search**, not a new frog outcome test.

### Draft archival data request, not sent

Dear Iowa DNR Volunteer Wildlife Monitoring Program,

I am auditing historical site- and visit-level environmental metadata for the NAAMP-era frog and toad call survey in Iowa, especially 2010–2015. Historical Iowa DNR documentation (1995–2003 report) and the current datasheet mention wet/dry condition at each listening site. Could you tell me whether original 2010–2015 NAAMP-route forms, database tables, or archived exports retain the per-stop wet/dry field (and any recorded water temperature), including missing-data codes and protocol-year changes? I am particularly interested in source-only metadata and dated stop maps/relocation histories for Iowa routes 360104 (stop 3) and 360412 (stop 7). I do not need identifiable volunteer contact information or species call records for this first audit. Please also advise whether any original route-number to USGS RunID/SiteID crosswalk can be shared and under what data-use conditions.

Thank you for considering this historical-data availability enquiry.

**Contact verification:** the official 2025 report names Stephanie Shepherd and the current DNR survey page links its monitoring portal. Before actually sending a request, reconfirm the official programme contact and obtain author approval. This document does not authorize sending.

## National-versus-state form mismatch: independently verified protocol boundary

The [USGS national NAAMP protocol](https://www.usgs.gov/centers/eesc/science/north-american-amphibian-monitoring-program) specifies route-start/end weather, **air temperature** at stops, 5-minute calling index, traffic, moonlight, and disruptive background noise. It does **not list stop-level wet/dry as a required national field** in its data-collection section. The same protocol says that stop relocation should generally be for safety rather than disappearance of habitat and that written relocation records were kept in most cases, but route-map updates were not always transmitted.

**Inference, not a downloaded data result:** Iowa's state forms could include a valid extra W/D field that was omitted in the harmonized national archive. Therefore if the USGS `Stops.csv` lacks wet/dry, a targeted **state-native raw form/database export** is the only reliable route for recovering historic Iowa stop-event water condition. Never code "missing from USGS" as "all sites dry", "wetness not observed", or "field absent from the original Iowa survey".

## Completed v3.1 USGS source-only result — authoritative closure

[Successful original USGS `Runs.csv`/`Stops.csv` header audit 37774857243](https://github.com/zuizui0223/frogcs/actions/runs/37774857243) read the checksum-pinned original files (21,934 Runs; 219,340 Stops), without opening `Counts.csv`. It confirmed **zero stop-level wet/dry, water-level, inundation or related hydrology candidate column names** in the 14-column national Stops export. Actual list:

`RunID, StopNumber, SiteID, AirTemp, Moon, SkippedStop, TimeOut, Noise, MassNoiseIndex, StartTime, SnowCover, CarCount, DateCreated, DateLastUpdated`.

The machine-readable [Actions artifact 11549248353](https://github.com/zuizui0223/frogcs/actions/runs/37774857243/artifacts/11549248353) is frozen; see `V3_1_ACTUAL_USGS_WETNESS_SCHEMA_RESULT_2026-10-08.md`. This **closes the USGS export-only path** for directly testing local wetland water state. Do **not** treat raw-route/year header enumeration as the standardized eligible site-year cohort: 360104 raw records include 2010, whereas the separately screened v2.1 standardized cohort begins in 2011.

### Verified archive custodian and access boundary

- Current official program contact: **vwmp@dnr.iowa.gov**, on the [Iowa DNR Volunteer Wildlife Monitoring page](https://www.iowadnr.gov/programs-services/volunteer-opportunities/wildlife-monitoring) (also published in the [online program's About page](https://programs.iowadnr.gov/vwmp/Home/About)).
- [The publicly accessible VWMP database home](https://programs.iowadnr.gov/vwmp/) presents a county selector and **Download Report** control, but data entry requires login. The public page does **not establish** that 2010–2015 site-event wet/dry, physical stop history, or raw survey records can be publicly exported; no private account or dataset was accessed.
- The Iowa DNR instructs monitors both to enter surveys through the online portal **and** mail paper datasheets to the state. This demonstrates current original-paper custody workflow but **not historical record retention**.

**Updated decision:** `historical_USGS_Stop_wetdry = NOT_PRESENT`; `Iowa_native_2010_2015_wetdry = UNKNOWN`; `historical_stop_relocation_logs = UNKNOWN`; `original_NLCD_C1_2_five_cells = NOT_OBTAINED`. Source custodian enquiry is the only remaining reasonable Iowa-water-state path before considering new ecology analysis. No email has been sent.

Before drafting another analysis, first obtain a **yes/no records availability answer** and per-year schema coverage for NAAMP ten-stop routes, without personal details or calling responses. If historic stop-event wetness is absent, **stop this selected Iowa route hydrology mechanism line** instead of substituting atmospheric weather, contemporary wetness, or new satellite proxies as if direct historical hydroperiod.
