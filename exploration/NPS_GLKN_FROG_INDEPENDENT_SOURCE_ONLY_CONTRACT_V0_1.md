# Independent NPS GLKN amphibian bioacoustic data — source-only prereadback QA

Frozen 2026-10-22, before opening NPS frog detections. User-directed continuation of NAAMP positive partner information research. **Separate from original JAE RC6** and from the failed 2025 Dryad CWMP ingestion.

## Source
U.S. National Park Service, Great Lakes Inventory and Monitoring Network (GLKN), *Great Lakes Amphibian Monitoring Bioacoustics Data Package by the Great Lakes Inventory and Monitoring Network*, publication **2026-09-30**. Source catalogue https://catalog.data.gov/dataset/great-lakes-amphibian-monitoring-bioacoustics-data-package-by-the-great-lakes-inventory-an. Original IRMA DataStore reference **2320505**, public domain / US Gov record.

Three immutable named official NPS distributions:
- `GLKN_AmphibianMonitoringData_2016-2023.csv` — https://irma.nps.gov/DataStore/DownloadFile/763377?Reference=2320505 ; frog detections, call intensity and survey metadata;
- `GLKN_AmphibianTemperatureData_2016-2023.csv` — https://irma.nps.gov/DataStore/DownloadFile/763378?Reference=2320505 ; air temperature hourly at monitoring equipment stations;
- `GLKN_Amphibians_2016-2023_metadata.xml` — https://irma.nps.gov/DataStore/DownloadFile/763466?Reference=2320505 ; survey protocol and field dictionary.

The source describes 14 calling-anuran taxa monitored at wetlands in seven national park units during 2016–2023. Published data may be wide or long; **do not assume a long table, site IDs or complete negative detections** until source-only schema QA is verified.

## Required retrieval and data integrity before biological readback
1. Download **only** those NPS-owned official distribution URLs. Limit each file to 60 MB and total to 120 MB. Validate CSV/metadata magic and reasonableness; store exact byte size, SHA256 and final host; no third-party mirror. The downloaded SHA256 values will be frozen by the first successful source-only audit before outcomes.
2. Before examining a single frog detection value, inspect only column names and species/taxon identifiers (not occurrence or call-intensity measures). Identify park, wetland station, point, survey event/time, year, taxon field, missingness of keys, repeated keys and survey grouping. Confirm which unit counts as a **distinct visit** and whether the same station was visited repeatedly. Do not treat missing taxon rows as nondetection.
3. Count independent park units, station/site locations, years, visits and distinct species labels (identifiers are allowed; outcome values not), duplicates by the verified grain, and temperature join candidates. Report all source-only eligibility gates before choosing an analysis.
4. Explicitly check occurrence of **both named focal species taxonomic units** `Lithobates clamitans` and `Lithobates catesbeianus` (including synonyms `Rana clamitans` / `Rana catesbeiana` only when documented by source metadata). If either absent, the *same named partner* independent test is impossible. Do not select an alternate favorable pair after reading frog outcomes.
5. Site/time independent replication requires ≥60 independently surveyed **site×survey-event** units with both named taxa included in a defined species-detection panel, ≥20 distinct stations and ≥2 park units. For the stronger NAAMP-style within-event placement comparison, additionally require ≥40 surveys with ≥3 fixed listening stations and non-degenerate frog incidence margins; without a multi-stop event, **do not describe a frog community fixed-margin null replication**.
6. If both response and temperature tables can be joined safely by station/time, evaluate how much coverage remains; do not assume species-specific plant cover is provided. Actual aquatic plants, predator fish and odonate larvae are **not verified** in these distributions. Species×plant mediated interaction is beyond scope unless new independent synchronized evidence appears.

## Original NAAMP observation as external falsification target

The corrected nested route-holdout finding from NAAMP (v0.3; source Actions 39713551897) is that **bullfrog `L. catesbeianus` calling locations have incremental predictive information** for green frog `L. clamitans` placement beyond NWI/earlier physical SiteID and generic chorus richness. Strong acoustic chorus endpoint is underpowered. Neither `Anaxyrus fowleri` nor `Hyla versicolor` has confirmed incremental negative-partner prediction after adding bullfrog presence, and no causal interaction is demonstrated.

**No frog outcome test may proceed** until NPS QA validates the source. If a compatible complete presence/absence panel exists, freeze a separate prospective independent held-out NPS model: wetland/station, year, season, temperature, survey effort and partner calling status, with park/site-group splits. Do not reuse NAAMP fitted coefficients and do not infer equivalence of survey protocols.

## Stop conditions
- Official NPS source access fails or only HTML/error body returned;
- field names do not establish unique site and survey event;
- unavailable detection/absence panel; no records for named pair;
- fewer than specified independent eligible site×event opportunities;
- no coordinate/temporal linkage for environmental data.

In every case archive exact source-provenance receipt and label `independent_validation_unavailable`, never a biological negative result. Do not ask the user to provide credentials if the source is genuinely public but temporarily unavailable. No edit to main, paper, SI or journal submission.
