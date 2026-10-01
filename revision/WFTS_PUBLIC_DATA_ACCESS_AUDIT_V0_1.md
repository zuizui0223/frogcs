# WFTS public data-access audit v0.1

**Date:** 2026-10-01  
**Status:** DATA_ACCESS_PENDING  
**Outcome boundary:** no species × station × year concentration endpoint inspected.

## Question

Can the traditional Wisconsin Frog and Toad Survey be obtained as a public row-level dataset with the fields required by the frozen confirmatory design?

Required minimum response fields:
- RouteID;
- station/SiteID;
- survey date;
- survey period;
- taxon identity;
- call index or station-level detection;
- repeated years.

## Public-source audit

The official WFTS pages confirm the survey design and the fact that analyses use station-level call records.

Publicly available official material includes:
- Survey Overview;
- Survey Manual;
- blank/sample field forms;
- individual route maps;
- statewide route map;
- Annual WFTS Summaries;
- programme analysis description.

The public Analysis page states that:
- occurrence is based on species calls at each listening station;
- abundance is represented by average call index;
- annual analyses use the survey-period records.

The public Annual Summaries page exposes year-level summaries, not a visible row-level CSV/Excel export.

A targeted web search of official Wisconsin DNR / WFTS sources on 2026-10-01 did **not** identify a public station-level historical download suitable for the frozen replication.

This is absence of an identified public download, not evidence that the raw data cannot be obtained from WFTS staff.

## Contact

Current official traditional-WFTS manual contact:

`WFTS@wisconsin.gov`

The outcome-blind request text is frozen in:

`revision/WFTS_DATA_REQUEST_TEMPLATE_V0_1.md`

## Decision

WFTS remains:

**DESIGN_ELIGIBLE / DATA_ACCESS_PENDING**

Do not move to the Iowa fallback unless:
1. WFTS staff confirm that the required repeated station-level data are unavailable/inaccessible; or
2. supplied files fail the frozen structural/data-access gate before the concentration endpoint is opened.

## Public sources checked

- https://wiatri.net/inventory/frogtoadsurvey/SurveyInfo/overview.cfm
- https://wiatri.net/inventory/frogtoadsurvey/SurveyInfo/analysis.cfm
- https://wiatri.net/inventory/Frogtoadsurvey/SurveyInfo/summaries.cfm
- https://wiatri.net/inventory/frogtoadsurvey/Volunteer/manual.cfm
- https://wiatri.net/inventory/frogtoadsurvey/Volunteer/PDFs/WFTS_manual.pdf

No public response matrix was downloaded or inspected during this audit.
