# NAAMP terrestrial mechanism — 15 Oct 2026 audited handoff

**Status:** Separate exploratory research branch; original JAE \`main\` frozen.
**No new biological effect has been established.** This document separates a genuine
geographical cohort from a real forest raster, and fixed-site placement from
the nontrivial multi-taxon concentration statistic.

## A. Source cohort verified with outcomes closed

- Original NAAMP Runs/Stops/physical coordinate SHA256 locked.
- Frozen-paper population reproduced without \`Counts.csv\`:
  4,236 pairs / 585 routes / 21 States;
  prior-physical-site-history subset 2,916 pairs / 439 routes / 20 States.
- Exact-ten-source-coordinate gate: **2,422 / 2,916 focal pairs** and
  **358 / 439 focal routes**, all 20 States. Important selection heterogeneity:
  Kentucky 1/26 pairs; Indiana 124/233; Iowa 77/120; South Carolina 147/148.
- Source-only archive and state representation:
  [Actions 38704933550](https://github.com/zuizui0223/frogcs/actions/runs/38704933550).
- No independent historical field-station relocation check or 300-m positional accuracy
  was established; no C1.2 per-stop forest pixel values were extracted.

## B. Official C1.2 source — verified availability, *not* numerical acquisition

Official USGS Collection 1.2 ScienceBase catalog items:
- Land Cover 2012, \`697b9279b66b0197c3043cc3\`, archive
  \`Annual_NLCD_LndCov_2012_CU_C1V2.zip\`.
- Land Cover Confidence 2012, \`697b92b8b66b0197c3043cc7\`, archive
  \`Annual_NLCD_LndCnf_2012_CU_C1V2.zip\`.

[October 15 capped ScienceBase and WMS audit](https://github.com/zuizui0223/frogcs/actions/runs/38703861726):
official ZIP URLs returned HTTP 206 but an **HTML range response** (\`bytes 159-4254/4255\`), not an original TIFF. WMS capabilities alone do not authorize the styled image as numerical land-cover categories.

Official **WCS 2.0.1** is available for **both** landcover and confidence:
- [OGC capabilities](https://github.com/zuizui0223/frogcs/actions/runs/38716521997) fetched valid official source XML.
- [WCS2 DescribeCoverage](https://github.com/zuizui0223/frogcs/actions/runs/38718113617) used the **exact advertised double-underscore coverage IDs**, not guessed WCS1 colon names, and found 1985–2025 time stamps; 30-m grid; axes X/Y/time; \`EPSG:5070\`.
- [Bounded numerical GeoTIFF probe](https://github.com/zuizui0223/frogcs/actions/runs/38718248838) **did not return numeric pixels** for a preselected non-NAAMP, 64×64 technical canary: official server replied XML
  \`Failed to read the coverage ... Cannot invoke Object.getClass() because startTime is null\`. WCS 1.0 was rejected with \`Could not understand version:1.0.0\`.
- The WCS catalog did not expose a defensible original C1V2 archive checksum or Collection 1.2-specific source identity. Temporal extent matching the C1.2 release does **not** independently prove original pixel equivalence.

**Decision:** Source remains \`C1V2_ORIGINAL_RAW_PIXEL_NOT_VERIFIED\`. No ecological vegetation or connectivity effect computed. Do not re-label WCS image tiles, Esri C1V0, Earth Engine community assets, or response-coloured maps as verified original C1V2.

## C. Concrete non-outcome-selected access alternative

The USGS [Annual NLCD Data Access guidance](https://www.usgs.gov/centers/eros/science/annual-nlcd-data-access) explicitly supports **AOI-defined GeoJSON** export of categorical GeoTIFF from the official [MRLC NLCD Viewer](https://www.mrlc.gov/tools) with email delivery. Request matched **2012 Land Cover and Land Cover Confidence** from Collection 1.2; verify collection/version in every delivered metadata file and original GeoTIFF. The source-only script \`research/scripts/create_source_only_mrlc_viewer_aoi_v0_1.py\` produces one deterministic, first lexicographically eligible route convex-hull +1,000 m GeoJSON without viewing CallingIndex, species or environmental outcomes. Its artifact status is independently recorded in GitHub Actions. This is technical readiness, **not** random biological replication.

If the official Viewer delivers a version other than C1V2, **stop** rather than silently change this preregistered hypothesis.

## D. Separate two statistical objects; crucial correction

The manuscript's within-taxon concentration for route-new taxa is

\`C = sum_s choose(max(k_s-1,0),2)\`.

### D1. Fixed per-species k: where?

\`research/scripts/exact_k_placement_kernel_v0_1.py\` conditions on each species' observed \`k_s\` and tests historic-site and forest-linked placement. It **cannot test C**, because C is fixed algebraically when all \`k_s\` are fixed. Previously implied direct-concentration capability is **withdrawn**. [8/8 synthetic QA](https://github.com/zuizui0223/frogcs/actions/runs/38563866657).

### D2. Fixed total K and route-new N: how concentrated across taxa?

\`research/scripts/conditional_kn_concentration_kernel_v0_1.py\` instead
conditions on the whole event's total wet species×stop incidence \`K\` and
the number \`N\` of taxa silent across the dry survey yet wet-positive.
Individual \`k_s\` may vary. An exact dynamic-programming normalizer
and conditional sampler permit posterior-predictive C testing.

A **generic within-species active-pair term** must be compared first with
independent-\`q\`; a **forest-linked same-taxon pair term** must demonstrate
additional out-of-block predictive value over this generic dependence.
Otherwise forest is merely a proxy for chorus concentration. Complete
forest-pair graphs make the two terms identical and unidentifiable.

[Latest exact-(K,N) synthetic tests](https://github.com/zuizui0223/frogcs/actions/runs/38718484567): **10/10 pass**, including demonstrations that C varies at fixed total K,N and that complete forest connectivity is indistinguishable from generic taxon-wide coactivation.

The new exact-(K,N) likelihood is **not the JAE original conditional concentration regression-beta/null**, and tests on reused NAAMP remain exploratory. For independent validation, require route-block training of all coefficients, same-threshold frozen \`q\`, actual forest patch GeoTIFF and predetermined guild labels, geographically held-out log scores and calibrated C simulations.

## E. Stop rule

There is no scientifically authorized claim that forest connectivity causes, predicts, or closes the focal unexplained frog concentration until **original matched categorical C1V2 and confidence pixels** exist for a source-eligible route and the mechanism survives **generic coactivation** and geographical holdout. No new taxon thresholds, forest radii or lag windows may be post-selected to rescue the result.

**main:** no changes. **This branch:** audited source feasibility, mathematical null implementation, tests and source-only AOI preparation only.
