# v3.1 completed original USGS NAAMP stop-schema audit — 2026-10-08

## Decision: local-water-state test blocked in the *released national tables*

**Status: observed and closed for this source.** [GitHub Actions run 37774857243](https://github.com/zuizui0223/frogcs/actions/runs/37774857243) completed **SUCCESS**, including checksum verification and artifact upload. [Original source-only artifact 11549248353](https://github.com/zuizui0223/frogcs/actions/runs/37774857243/artifacts/11549248353) is the authoritative machine-readable receipt (`NAAMP_ORIGINAL_STOP_HYDROLOGY_HEADER_ACTUAL_V31.json`); workflow ZIP SHA256 `7dfc8161b58eb156f144a5e228efea6f645be58970074a10ff8abfa18ffdb00e`. Its underlying tabular row counts were **21,934 Runs** and **219,340 Stops**. `Counts.csv` was **not accessed**.

### Actual original USGS `Stops.csv` fields

```text
RunID
StopNumber
SiteID
AirTemp
Moon
SkippedStop
TimeOut
Noise
MassNoiseIndex
StartTime
SnowCover
CarCount
DateCreated
DateLastUpdated
```

**Exactly zero candidate stop-level hydrology column names** matched the predetermined `wet|dry|hydro|inund|flood|water|pond|pool|moist|substrate|flow|depth` vocabulary. The genuine `AirTemp`, `Moon`, `SnowCover` or route-wide recent-rain fields are **not equivalent** to direct local wetness/inundation. Therefore **no direct local wet/dry, water level or standing-water measure can be joined from this original USGS Stops.csv**. Reconstructing the ecological mechanism from this export alone is not possible. Absence from a national standardized export says nothing about preservation of state-native data.

### Source versus analysis-population boundary

The script included every original row linked by `RunID` to raw focal RouteNumber 360104/360412 within 2010–2015 to inventory headers and candidate values. The logged `focal_years` are merely years for which raw source rows exist. **They are not the standardized v2.1 eligible acoustic/environmental cohort.** For example, v2.1 has no eligible pre-2011 standardized survey for 360104, while the raw header audit lists 360104/2010. Do not substitute the raw inventory for run-cohort counts, or use it to redefine the 2012 study breakpoint.

### Independent state-native archive evidence

- The [Iowa DNR 1995–2003 program report](https://publications.iowa.gov/18993/1/2005_FrogToad_rpt.pdf) (Methods, page 1) explicitly records historical *traditional-route* wet/dry status and water temperature at each wetland. These historical routes generally had five volunteer-selected sites; they are **not the same cohort** as the NAAMP ten-stop standardized routes.
- The [current Iowa DNR two-page survey form](https://www.iowadnr.gov/media/1759/download?inline=) clearly provides `Site Wet or Dry (W/D)` for each of the ten stops and distinguishes NAAMP numbered stops from traditional named sites. This establishes **current state form capability**, not its 2010–2015 availability.
- The [Iowa DNR survey webpage](https://www.iowadnr.gov/programs-services/volunteer-opportunities/wildlife-monitoring/frogs-and-toads/survey) instructs volunteers to both **enter surveys online and mail paper survey sheets** to the state. This is evidence of a **paper-plus-online custody workflow now**, not that specific 2010–2015 sheets survive or are digitized.
- The [national USGS release](https://www.usgs.gov/data/north-american-amphibian-monitoring-program-naamp-anuran-detection-data-eastern-and-central) is a harmonized multi-partner monitoring data product. Its `Stops.csv` cannot be used to falsify whether Iowa's original state records captured additional fields.

### What would close the mechanism gap

**Do not repeat the NAAMP `Stops.csv` extraction.** Request / retrieve **Iowa-native 2010–2015 source records**, first at *schema and completeness level only*, with:
1. Original blank state form(s) and annual protocol versions specifically used for **ten-stop NAAMP routes** in 2010–2015.
2. Raw event-level W/D or any water-temperature / inundation columns **by year and route type**, including whether the paper-form field was actually transcribed into the online database.
3. A route/run/site crosswalk, with exact dates, numbered stops and missing-data codes; initial request can explicitly exclude species counts and personal volunteer details.
4. Dated **stop establishment, relocation and mapped waypoint history** for 360104 stop 3 (SiteID 6613) and 360412 stop 7 (SiteID 7247).
5. If field or sheets were never retained, an **explicit no-archive / no-field confirmation** from source custodian, not an assumed negative.

**Gate:** Only a true state-native response-blind hydro/site-identity audit that passes temporal/physical-site coverage would justify designing a *separate* locked hydrological analysis. Even a successful W/D match does not identify water depth, spawning, individual movement, or a causal canopy effect; it may track detectability and local selection.

## QA and project isolation

The first workflow attempt [37774551987](https://github.com/zuizui0223/frogcs/actions/runs/37774551987) failed due absent Python `numpy`, not bad data. The dependency was added and the second run [37774857243](https://github.com/zuizui0223/frogcs/actions/runs/37774857243) **succeeded**. No additional frog-response analysis, ecological null-model retuning or results were generated. RC6 `main` and the frozen scientific submission candidate are unaffected.

**Decision:** Released-USGS local hydrology test = **BLOCKED, because requisite stop-event water-state field is absent**. Iowa-native historical data archive = **existence/availability unverified**. 2012 environmental-to-calling causal effect = **not established**. Continue archival source discovery only, not outcome fitting.
