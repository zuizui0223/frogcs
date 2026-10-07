# NAAMP MODIS DSWEmod source-availability repair v0.3 — 2026-10-07

**Status:** frozen after a response-blind source-access failure and before any DSWEmod-augmented frog endpoint was calculated.

## Source failure

The USGS ScienceBase child item for DSWEmod year 2004 lists `DSWEmod_US_2004.tif`, but its file metadata report size 0 and the direct download URI returns HTTP 404.

The parent 2003–2019 ZIP is 2,041,083,106 bytes and does not support HTTP Range requests, so extracting only the 2004 member would require downloading the entire 2.04-GB archive.

All other requested annual child GeoTIFFs in 2003 and 2005–2015 successfully downloaded in the first parallel extraction attempt.

No DSWEmod-augmented frog concentration or strong-chorus endpoint had been calculated when this repair was frozen.

## Fixed repair

Treat calendar year 2004 as **source-unavailable**.

Primary DSWEmod focal-pair eligibility therefore requires:
- both focal survey years belong to {2003, 2005, 2006, ..., 2015};
- neither focal survey is in 2004;
- all other v0.1/v0.2 geometry and hydrology validity rules remain unchanged.

Do not impute, substitute, or interpolate 2004 DSWEmod values.

For the M2/M3 temporal windows, any 3-month or 12-month sequence requiring a 2004 month simply counts that month as unavailable under the already frozen validity rules.

Thus:
- M1 can proceed on focal surveys with current-month data;
- M2 requires all three recent months and will exclude sequences crossing unavailable 2004 months;
- M3 retains the >=9 of 12 valid-month rule and may remain coverage-inconclusive.

## Unchanged analysis

Unchanged from v0.2:
- 500-m primary radius;
- 250-m named radius sensitivity;
- positive classes {1,2,3};
- valid classes {0,1,2,3,4};
- >=50% valid-buffer rule;
- same M0 comparator;
- opposite-route-fold species-specific training;
- SiteID then RunID centering;
- pair-level total-incidence matching;
- 1,500 pairs / 300 routes / 15 states coverage gates;
- concentration endpoint and simulation diagnostics.

## Anti-tuning

The year 2004 exclusion is justified solely by public-source unavailability. It may not be widened or narrowed after DSWEmod frog results are calculated.
