# WFTS data request template — prospective replication

**Purpose:** request only the raw/schema information needed to determine whether the frozen external-replication design can be implemented.

**Important:** do not request or invite any summary of whether frog calling was stronger after rain, whether multi-site concentration appears positive, or which taxa appear to drive any effect.

## Recipient

Wisconsin Frog and Toad Survey  
Wisconsin Department of Natural Resources  
Official programme contact: WFTS@wisconsin.gov

## Suggested request

Subject: Request for station-level Wisconsin Frog and Toad Survey data for a prospective replication study

Dear Wisconsin Frog and Toad Survey team,

I am preparing a prospective replication analysis of spatial patterns in frog calling using a protocol that has been fixed before inspecting Wisconsin Frog and Toad Survey response outcomes.

The traditional WFTS design appears unusually well aligned because routes contain repeated permanent listening stations, are surveyed repeatedly through time, and use the 1–3 call-index scale.

I would like to ask whether station-level historical WFTS data are available for research use.

For eligibility assessment, the minimum fields needed are:

- route identifier;
- station/site identifier;
- survey date;
- survey period/run;
- species/taxon identity;
- call index (1–3), or station-level presence/absence if call index is unavailable;
- enough repeated years to reconstruct strictly prior taxon × station history.

Helpful but not essential fields would include:

- observer identifier;
- start/end time;
- air/water temperature;
- wind;
- sky/weather notes;
- station latitude/longitude or a stable link to the public route coordinates;
- flags for route/station replacement or invalid surveys.

I would be grateful for either:

1. the raw station-level dataset and data dictionary, or
2. information on the process required to request access if the records are not publicly downloadable.

To preserve the prospective nature of the replication, please **do not provide summaries of effect direction, rain associations, species-level trends, or any analysis of the endpoint of interest**. Raw records/schema are preferred.

The analysis plan will link survey dates/locations to an external rainfall product using a weather specification frozen before the frog-response endpoint is opened.

Thank you for maintaining this long-running monitoring programme and for considering the request.

Sincerely,

[NAME]
[AFFILIATION]
[CONTACT]

## Request boundary

Before WFTS response data are opened, the repository must freeze:

- exact received file names and SHA256 checksums;
- data dictionary/schema;
- rainfall product and extraction code;
- local-date handling;
- wet-day threshold and antecedent rainfall metric;
- route/site identity repair rules;
- missing-data exclusions;
- deterministic train/test route fold;
- minimum sample/coverage gate.

If WFTS cannot provide the required repeated station-level records or dates, classify WFTS as data-access ineligible before inspecting any concentration endpoint and only then consider the predeclared Iowa fallback.
