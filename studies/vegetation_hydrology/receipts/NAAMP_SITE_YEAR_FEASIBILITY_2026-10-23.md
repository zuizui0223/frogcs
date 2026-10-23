# Pinned NAAMP coordinate and site-year feasibility receipt — 2026-10-23

## Provenance and status
- Branch: `research/vegetation-hydrology-feasibility-2026-10` (**independent; RC6 and main unchanged**)
- Successful public-source / geometry / calendar / site-year audit: [GitHub Actions run 39932617107](https://github.com/zuizui0223/frogcs/actions/runs/39932617107)
- Synthetic preprocessing workflow: [GitHub Actions run 39932587521](https://github.com/zuizui0223/frogcs/actions/runs/39932587521), **10/10 tests passing**
- USGS files downloaded and verified: `Runs.csv` SHA256 `ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730` (2,194,381 bytes); `Stops.csv` SHA256 `28138cdaab43a56ecad8df3b523060c812edfad018c20c67b14581c569a84b0f` (14,070,232 bytes); site coordinates SHA256 `f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83` (405,339 bytes).
- `Counts.csv`: **NOT DOWNLOADED, NOT READ**. No CallingIndex, taxon/site-outcome model or environmental response coefficient used.

## Measured outcome-blind geometry and calendar coverage
- Original coordinate rows and unique RouteNumber×SiteID keys: **12,064**
- Accepted coordinates: **11,668**; held/reviewed: **396**. Status is a *review gate*, not proof of true coordinate error.
- Geometry flags: 33 route spans over 25 km; 7 over 50 km. Reasons among held keys (overlapping): near-coincident distinct sites 48; one out-of-bounds longitude; 280 records on >25 km review routes; 70 on >50 km quarantine routes.
- Complete joined site-calendar: **185,221** valid station visits; **18,778** run IDs; **1,145** routes; **11,588** unique physical sites (across **25** states).
- **64,779 observed physical-site × survey-year combinations** during 2001–2015, against **173,820** full 15-year site-grid cells (37.2679% of all possible cells; 62.7321% fewer extraction operations when restricting to surveyed site-years).
- **10,158** sites sampled in at least 2 years; **8,913** in at least 3 years; **6,401** in at least 5 years; median **5 years per surveyed physical site**.
- The state-year CSV and JSON are retained in [artifact 12492462018](https://github.com/zuizui0223/frogcs/actions/runs/39932617107/artifacts/12492462018); site-calendar SHA256: `e6fc079ace3642a0ed4330dc05a4b8770fdf89cefabfaca0e490dcb3fd8c45cf`.

## What this establishes
A 2001–2015 outcome-blind environmental sample frame can be constructed from original fixed-station histories, and broad repeated-year coverage exists. It is more efficient to group remote-sensing work by the **64,779 observed site-year keys** than to process the 173,820-site/year full grid.

## What this does NOT establish
No real NLCD class fraction, Landsat DSWE inundation fraction, vegetation × rainfall effect, breeding habitat selection, frog response, or independent confirmation has been computed. These metadata include *all calendar-eligible runs*, not just the paper's 7,848 eligible runs or 4,236 matched wetter/drier pairs; the count of 25 states is **not** the JAE analysis sample of 21. A future matched-pair outcome sample will be smaller and must be independently verified.

## Next authorized step
Verify small-area access to a **named NLCD collection/version with raw categorical pixels** (no RGB-rendered WMS substitutions), create an outcome-blind state/year coverage and missingness audit, then obtain temporally matched local surface-water scenes. Only afterward freeze an independent frog-outcome analysis.
