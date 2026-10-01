# WFTS Daymet weather adapter specification v0.1

**Status:** frozen before access to WFTS frog-response outcomes.

This specification implements the weather exposure already fixed in `WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_4.md`.

## Input grain

The adapter accepts a **response-free structural station-survey table** with exactly:

- `route_id`
- `survey_period`
- `survey_year`
- `survey_date`
- `station_order`
- `physical_site_id`
- `latitude`
- `longitude`

No taxon identity, call index, richness or frog-response column is permitted.

## Weather source

Primary source: **Daymet daily surface weather, Version 4 / current R1 delivery**, ORNL DAAC.

Dataset DOI: `10.3334/ORNLDAAC/2129`.

API base:

`https://daymet.ornl.gov/single-pixel/api/data`

Variables:
- `prcp`
- `tmin`
- `tmax`

Daymet is used because it provides approximately 1-km daily weather over continental North America from 1980 onward, covering the WFTS period.

## API query

For each unique physical site:

- latitude/longitude are rounded only for request serialization, not spatial aggregation;
- request `vars=prcp,tmin,tmax`;
- request all Gregorian years needed by that site's surveys plus any preceding year required by the 30-day dry-spell window;
- preserve the returned raw CSV bytes in a cache directory;
- record request URL, byte size and SHA256.

Do not use frog outcomes to decide which years/sites are queried.

## Daymet date reconstruction

Daymet returns `year` and `yday` on a 365-entry calendar.

For non-leap years:
- yday 1 = Jan 1
- yday 365 = Dec 31.

For leap years:
- Feb 29 is retained;
- Dec 31 is omitted;
- yday 365 = Dec 30.

Reconstruct Gregorian dates by iterating the actual Gregorian calendar from Jan 1 through Dec 31 and, in leap years, dropping Dec 31 before assigning Daymet yday 1..365.

Do **not** interpret Daymet yday using ordinary 365/366 Gregorian ordinal arithmetic.

## Frozen station-level exposure

For a survey date `d` at one physical station:

1. Ignore Daymet precipitation on `d`.
2. Start on `d - 1 day`.
3. Count consecutive complete Gregorian days with `prcp < 1.0 mm/day`.
4. Stop at the first day with `prcp >= 1.0 mm/day`.
5. Cap at 30 days.
6. If any required prior Daymet day is absent before the count terminates/caps, weather extraction for that station-survey is invalid.

Output:
- `dry_days`
- `log_dry_days = log(1 + dry_days)`
- `tmean = (tmin + tmax)/2` on the survey date.

Survey-date precipitation never enters the primary exposure.

## Frozen route-run aggregation

A canonical traditional WFTS route-run requires 10 stations.

For each `route_id × survey_period × survey_year`:

- `rain_recency = mean(log_dry_days)` across all 10 stations;
- `tmean_run = mean(tmean)` across all 10 stations.

If one of the 10 station weather records is invalid, the entire route-run is weather-ineligible for the primary analysis.

Do not switch from mean to median after frog outcomes are available.

## Coordinate identity

A `physical_site_id` must map to one latitude/longitude pair within the supplied structural table.

If coordinates differ for the same physical SiteID, fail closed rather than averaging them.

Station replacement/identity rules are handled before weather extraction by the structural WFTS adapter.

## Output files

1. canonical run-weather CSV with:
   - route_id
   - survey_period
   - survey_year
   - survey_date
   - rain_recency
   - tmean_run

2. station-weather audit CSV with:
   - all structural station identifiers
   - latitude/longitude
   - dry_days
   - log_dry_days
   - tmean
   - raw-cache SHA256

3. JSON provenance receipt containing:
   - Daymet DOI
   - API base
   - threshold/cap
   - input SHA256
   - output SHA256
   - raw cache file hashes
   - number of route-runs/station-surveys
   - invalid-weather counts.

## Fail-closed rules

The adapter must stop if:
- response-like columns such as `taxon_key`, `call_index`, `species`, `richness` or `concentration` appear in its input;
- a route-run does not have exactly 10 unique station orders;
- one SiteID maps to multiple coordinates;
- requested Daymet variables are missing;
- a Daymet year has other than 365 rows;
- reconstructed dates are duplicated;
- required prior days are missing.

## Synthetic QA

Synthetic QA must test:
- non-leap date mapping;
- leap-year Feb 29 mapping;
- leap-year Dec 31 absence;
- dry spell = 0 after prior-day wet event;
- dry spell cap = 30;
- survey-day precipitation ignored;
- exact 10-station route averaging;
- fail-closed duplicate coordinates;
- fail-closed forbidden frog-response columns.

Synthetic values have no ecological inferential role.
