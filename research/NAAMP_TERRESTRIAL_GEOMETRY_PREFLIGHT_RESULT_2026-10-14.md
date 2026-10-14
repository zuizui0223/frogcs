# NAAMP terrestrial-landscape source-only geometry: real 2026-10-14 readout

**Result type:** SOURCE-ONLY ELIGIBILITY / TOPOLOGY. No NAAMP frog counts, climatic outcomes, taxon guilds, land-cover pixels or publication endpoints were read.

## Verified run and source

- [GitHub Actions SUCCESS, 8/8 offline tests](https://github.com/zuizui0223/frogcs/actions/runs/38563109769)
- [Original run artifact ZIP](https://github.com/zuizui0223/frogcs/actions/runs/38563109769/artifacts/11892718069): contains the full route-by-route geometry and eligibility report.
- Source: original USGS/NAAMP RouteNumber, SiteID, lat, lon coordinates; SHA256 \`f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83\`.
- 12,064 source rows, 1,183 RouteNumber identifiers.
- Reproduced the prior 8+-SiteID geometry-only eligibility result: **1,106** routes (source-hash and expected-count checks passed).
- **1,028** routes (86.90% of 1,183) further meet an unambiguous **exactly ten** distinct physical SiteIDs with complete coordinate geometry and no additional invalid source rows. This is a conservative *source-only* shortlist, not the 439-route principal paper cohort.

## Bounded geometric question

For those 1,028 exact-ten routes, count whether 300-m or 1,000-m circles centred on physical stop coordinates overlap in Euclidean/geodesic geometry. Pair distances are from great-circle distance and overlap if the distance is less than the sum of the radii. No actual vegetation, forest or wetland raster is used.

| Route-level quantity | Minimum | Q25 | Median | Q75 | Q90 | Maximum |
|---|---:|---:|---:|---:|---:|---:|
| 300-m buffer-overlap pairs among 45 | 0 | 0 | **0** | 0 | 1 | 21 |
| 1-km buffer-overlap pairs among 45 | 0 | 5 | **7** | 10 | 13 | 45 |
| Components of the 1-km buffer-overlap graph | 1 | 3 | **4** | 5 | 6 | 10 |

- **1,025/1,028** eligible routes have at least one overlapping pair of 1-km circles.
- **116/1,028** have all ten centres connected via the 1-km circle-overlap graph, allowing indirect links.
- \`median=4 components\` means this geometric graph is commonly disconnected; this **does not** mean four biologically isolated frog populations or forest patches.

## Scientific consequences

1. Landscape geometry varies enough among routes that a spatial hypothesis can be formulated. This is NOT evidence that landscape connectivity explains frog behaviour.
2. **300-m buffers almost never overlap:** their median, first and third quartiles are all zero. This makes within-stop forest composition vs between-stop forest-patch connectivity distinct exposures.
3. Proximity can create many 1-km circle overlaps while **not** indicating whether any two stops are connected by forest. Real connected-patch exposure requires land-cover pixels over a route-wide envelope; forest may connect stops separated by more than two kilometres.
4. The original geometry gate does not prove metre-level positional accuracy, historical station identity, or whether all ten SiteIDs were actually sampled at a given acoustic survey event.
5. The NAAMP focal comparator contains **2,916 pairs, 439 routes and 20 States**, not all 1,028 shortlisted source routes; next eligibility audit must intersect the frozen event/site IDs without changing the outcome or selecting on residual size.

## Fixed next source gate: official forest pixel access

Use a single **USGS Annual NLCD Collection 1.2** land-cover release, not mixed C1.0/C1.2 layers. The current USGS catalogue verifies annual CONUS 30-m land cover for 1985–2025; USGS product suite release is June 2026:

- [USGS Annual NLCD Land Cover](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-1-land-cover)
- [USGS dataset access](https://www.usgs.gov/centers/eros/science/annual-nlcd-data-access)
- USGS data release: https://doi.org/10.5066/P94UXNTS
- Land-cover classes 41 (deciduous forest), 42 (evergreen forest), 43 (mixed forest) are the predeclared forest category. Retain source class confidence and no-data; do not infer numeric classes from rendered WMS colours.

**Before frog outcomes are read:** obtain raw categorical GeoTIFF samples from a documented official C1.2 distribution, verify year/product identity, pixel classification (not RGB map output), original CRS and 30-m grid, source identity/checksums and paired land-cover confidence. If only WMS images or C1.0 rasters can be accessed, DO NOT call the planned C1.2 forest model executable.

For retrospective context use the **completed calendar year preceding an acoustic survey** as the draft candidate exposure, then freeze the precise historical reference rule *before* new outcome inspection. Annual NLCD is a retrospectively modelled 2026 product, so labelled-year selection does not prove that its estimation used only imagery available by that year; no prospective/no-future-information claim is allowed without a separate source audit.

The 300-m circle around a **listening stop** is not equivalent to a 300-m zone outward from the edge of a **verified wetland**. Semlitsch & Bodie (2003) concern terrestrial habitat around aquatic habitats; positional mismatch must be reported.

For patch connections, choose and preregister a route-wide raster domain (route convex hull plus a fixed margin, or an independently defined local watershed boundary) and a forest-pixel adjacency convention; restricting raster connectivity to the disjoint 1-km circles would artificially sever genuine external corridors.

## Mathematical method now testable, but not yet applied to frogs

- [Exact-k placement kernel](../scripts/exact_k_placement_kernel_v0_1.py)
- [Synthetic QA SUCCESS, 8/8 tests](https://github.com/zuizui0223/frogcs/actions/runs/38563866657)

Conditional on the exact observed number of active listening stations \`k\`, the likelihood enumerates at most C(10,5)=252 site subsets. Its baseline consists of original frozen \`q\` probabilities and adds only residual historical-site, soil-by-historical-site, canopy and taxon-guild-by-canopy, and linked-forest-pair features. **Do not feed the CI>=1 comparator q into a CI>=2 or CI=3 observed response:** the kernel checks matched outcome thresholds.

A route-constant soil-water level CANNOT have an identifiable additive placement effect once \`k\` is fixed; it can affect the amount of activity, or placement *through a site-specific interaction*. Testing connectivity requires real forest patch labels, not the geometric overlaps in this readout.

No new mechanism is supported at this stage: this work establishes technical readiness, boundaries and a falsifiable next test.
