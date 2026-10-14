# v7.1 — Pre-outcome original public frog assemblage seasonal recurrence analysis contract

**Frozen 2026-10-13 JST BEFORE accessing this source's `scientific.name` detection identities and computing similarity results.** Separate independent public-ecology addendum on frogcs draft PR #135, NOT a JAE RC6 extension, NOT the 2016–2025 Flow-MER acoustic/water archive, and NOT a causal wetland/hydrological study.

## Origin and verified observation grain

[Hoefer et al. (2026) Zenodo v2.0](https://zenodo.org/records/21634473); original [public CSV](https://github.com/cheloniax/repo_PAM_frogs/blob/v.2.0/data/frog_data_season.csv) source Git blob SHA1 `e5a419574be5e3f9922989f9aa6001fbb7f09d01`. Original [data dictionary](https://github.com/cheloniax/repo_PAM_frogs/blob/v.2.0/data/ReadMeDataFiles.txt). [Response-blind actual source checks v7.0](https://github.com/zuizui0223/frogcs/actions/runs/38350097992) established **13,577 positive detection rows**, **6 source site labels × 4 plot labels = 24 physical plot keys**, positive reports in **95/96 site-plot × season combinations**, source `assessment.method` **PAM.all only**, seasons autumn/spring/summer/winter, original detection dates across **2019–2023**, with every site having positive records in **3–5 calendar years** and all four author seasons. **73 site–plot–season keys have positive records from 2+ years**. The source field is lower-case `sampling.trip`, unlike the data dictionary's `Sampling.trip`; no inference is made from this uncertain field's site×year meaning.

**Published rows are detections, NOT complete survey opportunities.** A cell without listed detections can be missing recording coverage, not an acoustic zero or species absence. One site-plot-season positivity cell is absent; do not construct it as a confirmed all-frog-zero survey. Multiple source records per species/day are not independent replicates. No coordinates or names of source sites should enter output.

## Biological question (observed detections, no exposure mechanism)

> Within the same surveyed plot, do **species lists detected in the same season in adjacent calendar years** resemble each other more than species lists in **different seasons of the same calendar year**, relative to within-season, between-plot differences inside the same site?

This is a **descriptive seasonal recurrence of *detected frog assemblages***, not individual frog site fidelity, adaptation, local moisture hysteresis or recolonisation. The source paper already examines PAM detection advantages; this analysis is about separable time/site axes of the published PAM.all detected species lists, not an independent duplication of their observer-versus-PAM sensitivity result.

### Fixed unit and similarity

Define nonempty `S(site, plot, source-season, calendar-year)` as the set of **distinct nonblank `scientific.name`** strings among `PAM.all` positive rows. Parse calendar year from published `date` with a valid YYYY-MM-DD date, and require season one of `autumn,winter,spring,summer`. For those positively represented cells only, use binary **Jaccard similarity** `J(A,B)=|A∩B|/|A∪B|`; repeat day/row detections are collapsed to single cell×species presence *in the reported detections*, not converted into an abundance estimate.

Use these **predeclared** pair categories, all within the same source site, with both cells containing ≥1 named detected species:

- **A — annual same-season recurrence:** same site, same plot, **same season, immediately adjacent calendar years** (year difference exactly 1);
- **T — within-year seasonal turnover:** same site, same plot, same calendar year, **different seasons**;
- **P — same-year within-site spatial comparison:** same site, same year, same season, **different plots**.

Calculate average J per pair category **within each of the six source site IDs**. Primary descriptive contrast `Δrec = mean_site[J_A − J_T]` across **equal-weight sites**. Positive means the same author-season community detected in adjacent years is more similar than different author-seasons within year, despite longer time separation. Secondary `Δplot = mean_site[J_P − J_T]` describes spatial vs temporal detected assemblage structure. Direction is unknown before results. Do not change categories or weighting after seeing detection results.

If a site has zero eligible A or T pairs, exclude that site from the *paired* primary contrast but report the number of excluded sites. If fewer than 3 sites remain, report descriptive pair counts only, not a cross-site pooled effect. Do not silently assume all scheduled plots/seasons recorded.

### Source exposure sensitivity, frozen with the primary plan

Compare primary all-eligible-cell result to a **positive-date-support sensitivity** requiring **at least 5 distinct dates with any positive frog record in EACH member cell**. This is a deliberately conservative *detection-date* support check, **NOT genuine standardized acoustic recording effort** (because no explicit scheduled/valid negative recording denominator exists). Report number of source sites and cell-pairs still evaluable. If the sensitivity changes direction or eliminates most sites, label **INSUFFICIENT_OR_SUPPORT_SENSITIVE**. Do not tune the threshold to retain a preferred result.

### Uncertainty/reporting

Treat six original sites, NOT 13,577 rows or hundreds of overlapping pairs, as the broadest independently sampled contrast units. Report primary/secondary equal-site-weight averages, 6 site mean differences in aggregate as range and direction counts **without source site labels**; nonparametric percentile **site-bootstrap 95% descriptive intervals, 5000 replicates with fixed seed 20261013**, flagged unstable at n≈6 and **NOT proof of biological mechanism or survey-design CI**. Site names, precise coordinates, event dates and species identity lists are not to be exported. Use no p-value as confirmatory evidence. Report the source pair counts and number of eligible sites so the source scope is visible.

No species-level multiple-testing, best-species searches, water associations, annual colonization/extinction, structural occupancy, acoustic intensity, reproduction/larval fitness or extrapolation to the CEWH Murrumbidgee sites.

## Source and code audit

- Retrieve ONLY pinned public source `frog_data_season.csv` over allowlisted official raw GitHub HTTPS (≤4 MB); fail closed on blob mismatch/schema drift.
- Validate source row count, methodology, six sites, 24 site×plot keys, 4 seasons and correct nonblank species/date data; any change in source SHA stops.
- Write one aggregate-only JSON receipt with raw source SHA and code commit, omit record/site/species IDs; do not commit the raw CSV.
- Keep source README/README.md and PR status updated **only after actual CI output**. A successful workflow means the analytical code ran; it does not turn positive-only detections into complete monitoring effort.

The separate hydrological Q-A/Q-B analysis remains **NOT IDENTIFIED** without physical wetland↔recorder↔depth logger and valid source opportunities. The CEWH source request remains **UNSENT**. No TinyFish, paid browser, private datasets or new synthetic ecology.
