# NPS GLKN independent fixed-site historical chorus prediction — analysis contract v0.1

Date: 2026-10-25. Defined **after inspecting source schema, before reading any NPS call-status outcome estimates.** Independent external monitoring dataset; not frogcs RC6 submission data or NAAMP matched rainfall test.

## Source

- US National Park Service public-domain GLKN amphibian acoustic dataset DOI 10.57830/2320505, main CSV: https://irma.nps.gov/DataStore/DownloadFile/763377?Reference=2320505 (2026-09-30 edition).
- [Blind schema audit receipt](results/nps_glkn_schema/schema_receipt.json): downloaded 68,581,307 bytes, SHA256 `b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2`, **147,913** species×recording rows, 66 site identifiers, 7 parks, 8 years, 13 scientific-name tokens. Direct columns `ManualCIV` (0,1,2,3), `SurveyorDetectedStatus`, `FileName`, `SiteLocation`, `EventYear`, `ScientificName`, `Hydroperiod`, date, quality/noise/duration and temperature.
- Program includes hourly 5-minute recorder intervals during frog-breeding season and manual verification. Recordings differ in availability/effort by site/year. Some rare species may be under-detected. Data source should be pinned by SHA256 and parsing checks. No licence ambiguity: U.S. government public-domain source.

## Biological hypotheses

**Q3 prospective independent species×physical-site history:** a species historically chorusing strongly (CI≥2) at a fixed listening station has elevated probability of CI≥2 at that station in a later year, conditional on **species×park×year** and exposure/effort. This is acoustic recurrence, not same individual returning to a pond or reproductive success.

**Site-common alternative:** general attractiveness of a station shared across frog taxa (prior *other-taxon* strong history, local hydroperiod) explains the relation, so same-species history should contribute little after explicit generic-site controls. Do not claim causal conspecific facilitation if same species history remains.

**Hydroperiod alternative:** stable wetland hydroperiod classes differentiate site suitability and modify persistence. Emergent vegetation not measured in the source; cannot test plant density or stem structure.

## Frozen observables and analysis

1. Exclude missing/invalid `SiteLocation`, `ScientificName`, `EventYear` or `ManualCIV`. Keep `ManualCIV∈{0,1,2,3}`; fail if unexpected valid coding. Collapse duplicate `FileName×ScientificName` records at same site/year using **maximum** observed CI (logging duplicates). Main census grain: `ParkCode×SiteLocation×EventYear×ScientificName`; calculate the **maximum manually scored CI in that year**, plus the number of distinct audio files and distinct survey dates.
2. To ensure comparable opportunities for calling, construct a full site×year×taxon panel only where a site-year has at least one scored recording; zeros represent **no recorded strong call among scored files** and should not be labelled true demographic absence.
3. Use years **2017–2023**, requiring strictly prior recordings at the same site, and record `history_years_observed`, prior total visits, `own_ever_strong_prior`, `other_taxa_prior_strong_fraction` formed strictly before focal year (exclude target species). Compare with `Hydroperiod` and `log1p(current_year_recordings)` to account for maximum-CI sampling effort. Report presence (CI≥1) as sensitivity, CI3 as stronger endpoint; do not replace primary threshold post-hoc.
4. Primary stratified **site-selection contrast**: within `park×taxon×current_year` groups with ≥4 observed stations, at least 1 historically strong and 1 historically non-strong station, calculate the difference in proportion with annual CI≥2 between these historical categories. Count informative strata, sites, species and years. Use a group-fixed-effect linear probability slope on `own_ever_strong_prior`. Rows from groups lacking exposure variation contribute zero. Include `other_taxa_prior_strong_fraction`, hydroperiod categories, and log recording effort for stronger adjusted comparison.
5. Uncertainty: resample entire **park×taxon** trajectories to retain repeated years per taxon and sites; 2,000 cluster bootstrap replications of precomputed sufficient statistics (never independent row SE). Also report park-level directional spread; only 7 parks so avoid treating these 7 as infinite-population units.
6. Temporal split: report early **2017–2020** and later **2021–2023** using identical history construction; latter is held-out descriptive temporal evaluation, not independent of earlier years in predictor history and not an untouched external programme.
7. Predatory/fish/vegetation claims: none; prior other-taxa calling is **acoustic common-site structure**, not predator-community measurement. `Hydroperiod` class is broad and does not measure current water level or plant architecture.
8. No search for alternative thresholds/vegetation/rain windows based on results. Differences from NAAMP 4,236 matched wetter-drier pairs: NPS is asynchronous recordings and annual summaries; does **not** test rainfall-conditioned ten-stop spatial concentration C, or causal rain effect.

## Outcomes and interpretation

- Strong own-history association after generic-site/hydroperiod/effort control: supports **external reproducibility of species-specific historical acoustic site selectivity**, not proof of behavior/plant cause.
- Association fully attenuated: suggests local stable environment/general station attractiveness can suffice in NPS; strengthens environmental filtering alternative.
- Strong heterogeneity among park/taxa or opposite early/late: external-generalization claim must be limited.
- If dataset cannot support ≥4-site within-species×park×year strata with historical exposure variation: declare **non-estimable**, no arbitrary fallback to unstratified pseudo-replication.

The source's apparent sample size of >147k is not 147k independent wetland-site-year contrasts; restrict inference to sites/parks/taxa/time as appropriate.
