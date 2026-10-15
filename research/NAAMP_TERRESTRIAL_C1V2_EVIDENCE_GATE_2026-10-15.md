# Terrestrial context evidence gate — 2026-10-15

**Study status: SOURCE / METHOD ONLY, NO NEW FROG RESULT.**

This memo advances the separate exploratory landscape proposal without modifying the
frozen JAE submission or treating exposed landscape contrasts as confirmation.

## 1. Exact cohort × coordinate gate (real original data)

[Successful SHA-verified Runs/Stops-only action](https://github.com/zuizui0223/frogcs/actions/runs/38703262483) — [full outcome-blind source receipt](https://github.com/zuizui0223/frogcs/actions/runs/38703262483/artifacts/11957282049).

- Pinned original NAAMP \`Runs.csv\` SHA256: \`ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730\`.
- Pinned original NAAMP \`Stops.csv\` SHA256: \`28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f\`.
- Pinned coordinate SHA256: \`f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83\`.
- Using only survey times, visit effort, route and run numbers, temperature, days since rain and repeated physical SiteIDs, the metadata-only implementation reproduced the original sample: **4,236 comparisons / 585 routes / 21 States** and the paper's history subset: **2,916 comparisons / 439 routes / 20 States**.
- Intersecting with the previously fixed strict ten-coordinate route gate leaves **2,422 comparisons / 358 routes / 20 States**, i.e. **83.059% of focal pairs and 81.549% of focal routes**.
- **494 focal pairs and 81 focal routes are excluded** by the exact-ten coordinate rule, without reference to CallingIndex, species or paper effect sizes.
- Six synthetic boundary/identity tests passed. A subsequent run adds **state-specific route and pair retention fractions** to the immutable report; report those before any ecological subgroup comparison.
- These 358 candidate routes have not passed original C1V2 pixel coverage, independent historical station continuity, or 300-m coordinate positional truth. Results cannot be interpreted as 358 verified forest/pond localities.

The complete route/pair keys are stored in the attached Actions artifact, not in the manuscript. Source route overlap alone is not outcome validation.



## 1b. Unequal state retention: IMPORTANT macroecological selection caveat

A second SHA-verified metadata-only workflow (six synthetic tests PASS, [original Actions run](https://github.com/zuizui0223/frogcs/actions/runs/38704933550), [full state-stratified receipt](https://github.com/zuizui0223/frogcs/actions/runs/38704933550/artifacts/11957987407)) reproduced the same global 2,422 pairs / 358 routes and measured complete-case retention by State:

| State | Focal pairs | Source exact-ten pairs | Pair retention | Focal routes | Source exact-ten routes |
|---|---:|---:|---:|---:|---:|
| Kentucky | 26 | 1 | **3.8%** | 2 | 1 |
| Indiana | 233 | 124 | **53.2%** | 39 | 25 |
| Iowa | 120 | 77 | **64.2%** | 29 | 22 |
| Tennessee | 30 | 23 | 76.7% | 11 | 9 |
| North Carolina | 246 | 233 | 94.7% | 47 | 43 |
| South Carolina | 148 | 147 | **99.3%** | 24 | 23 |

All 20 paper States retain some data, but **their weights are not preserved**. This is selection on existing coordinate geometry, not on a frog outcome, but missing coordinates or route layout may associate with geography, habitat and taxon composition. Accordingly:

- Do not equate retaining 83.1% of pairs with an unbiased regional or continental macroecological sample.
- Report source-eligible versus excluded geography / route metadata and state-balanced effects **before** any spatial or species-guild mechanism inference.
- Do not interpret the one Kentucky pair or one Texas route as state-general evidence. If State × guild overlap is inadequate, mark the moderator unidentifiable instead of optimizing subsets.
- Any future model must carry the response-blind source selection and its spatial coverage limitation into inference, and must not claim a geographically uniform mechanism.

## 2. Official 2012 C1V2 landcover + confidence source gate

[Source-only USGS audit success](https://github.com/zuizui0223/frogcs/actions/runs/38703861726) — [original machine receipt](https://github.com/zuizui0223/frogcs/actions/runs/38703861726/artifacts/11956974035).

| Product | USGS official ScienceBase item | 2012 original archive | Catalog ZIP bytes |
|---|---|---|---:|
| Land-cover categorical | \`697b9279b66b0197c3043cc3\` | \`Annual_NLCD_LndCov_2012_CU_C1V2.zip\` | 1,388,935,096 |
| Land-cover model confidence | \`697b92b8b66b0197c3043cc7\` | \`Annual_NLCD_LndCnf_2012_CU_C1V2.zip\` | 7,696,467,112 |

A bounded official ScienceBase Range attempt for **both** returned HTTP 206 with \`Content-Type: text/html\` and Content-Range \`bytes 159-4254/4255\`: neither returned ZIP bytes. The previous 2026-10-08 study had already found this false-206 HTML condition for cover; the new audit reproduced it and additionally checked confidence.

The official MRLC WMS endpoints returned valid capability XML (225,983 and 226,082 bytes, respectively) but no explicit year-labelled C1V2 name in the parsed layer list. The WMS capability response **does not prove** that a requested raster is the original C1V2 numeric categorical product. We never interpreted PNG/RGB WMS output as category codes.

**Decision:** \`C1V2_RAW_RASTER_NOT_ACQUIRED\` (source access blocker). No ecological forest coefficient can be computed. Do not substitute old C1V0 (incomparable classifier version), WMS display colours, unverified STAC C1V1, or fee-bearing requester-pays S3 access for the stated C1V2 experiment.

Official source guidance (public):
- https://www.usgs.gov/centers/eros/science/annual-nlcd-data-access
- https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-12-land-cover
- https://doi.org/10.5066/P94UXNTS

The official product offers EarthExplorer, the MRLC mosaic viewer/direct download and USGS AWS S3 (Oregon requester pays). A small AOI original categorical+confidence GeoTIFF can be provided to the tested extraction script, but its **source identity and hash must be pinned** before any frog outcome joining.

## 3. Forest-patch extraction method

The separate \`research/scripts/nlcd_c1v2_forest_patch_features_v0_1.py\` uses:
- class codes **41,42,43** (deciduous, evergreen, mixed forest) and explicitly excludes woody wetland class 90 from the *forest* definition; this is not a claim that woody wetlands are biologically unimportant;
- ten georeferenced stop centres, 30-m native unrotated classified pixels with exactly matching confidence grid;
- 300-m stop-centred forest fractions, with >=70% valid category pixels and >=95% confidence-field completeness. **Confidence scores are reported, not treated as independently calibrated accuracy probabilities or used to select a favourable numerical cutoff.**
- a predeclared 1,000-m buffer around the **convex hull of the ten stops** as the route-wide forest-patch domain;
- 8-neighbour forest components and a pairwise 10×10 Boolean matrix: a pair is linked only when a **single mapped forest component touches both 300-m stop buffers**. Overlapping circles or short route lag are NOT enough.
- fail-closed source manifest (original item ID, original archive year, C1V2 version, actual local GeoTIFF SHA256), 30-m native CRS/transform, completeness, route-domain containment.

This is a **terrestrial cover/connectivity proxy**; it is not movement, local population gene flow, pond-bed moisture or breeding success. The downstream placement model still requires a separate SAME-threshold independently trained acoustic baseline; NLCD features alone do not reproduce the JAE conditional-concentration residual.

## 4. Explicit stop

Do not:
1. change buffer radii, forest classes or source versions to seek significant frog effects;
2. treat 2,422 coordinate-eligible pairs as 2,422 forest pixels / 2,422 complete landcover samples;
3. turn the current metadata preparation into independent replication of the manuscript;
4. fit NAAMP frog response outcomes before original C1V2 class+confidence local pixels and spatial/source QC are documented;
5. claim hydric state × historical-site interaction: the archived September 30 primary tests were **not supported**.

**Next strictly necessary source action:** produce a small verified original C1.2 **class+confidence** GeoTIFF pair covering a single independently selected, non-outcome-selected 10-stop route hull+1km, then verify class histogram and forest-patch features before scaling to 358 candidate routes. If unavailable, report source limitation and prioritise an independent fixed-site field dataset over additional covariate fishing.
