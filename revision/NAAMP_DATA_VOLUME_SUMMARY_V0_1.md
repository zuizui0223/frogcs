# NAAMP frog and rainfall data volume summary v0.1

Source of record:
- audit contract: `audit/NAAMP_DATA_VOLUME_AUDIT_CONTRACT_V0_1.json`
- audit receipt: `audit/NAAMP_DATA_VOLUME_AUDIT_RECEIPT_V0_1.json`
- canonical pair-side check: `audit/NAAMP_CANONICAL_PAIR_VOLUME_CHECK_V0_1.json`

## Raw USGS NAAMP release

Core frog tables contain:

| table | rows | file size |
|---|---:|---:|
| Runs.csv | 21,934 | 2.19 MB |
| Stops.csv | 219,340 | 14.07 MB |
| Counts.csv | 337,848 | 17.21 MB |
| Species.csv | 68 taxon-label rows | 0.003 MB |

The three core observation tables total **33.48 MB**.

Important: `Counts.csv` is sparse. Its **337,848 rows are positive CallingIndex 1–3 records**, not a dense matrix containing zeros.

## Current 2001–2015 analysis subset

After the current unified-protocol and run-quality filters:

- **7,848 eligible survey runs**
- **807 routes**
- **21 states**
- exactly **78,480 run × stop opportunities**
- **57 positive taxon labels** somewhere in the eligible survey set
- **115,638 observed positive run × stop × taxon cells**
- **59,434 active run × stop visits** containing at least one calling taxon

Across all eligible runs:

- mean positive taxon-stop cells per run = **14.73**
- median = **14**
- 5th–95th percentile = **3–30**
- mean taxa detected somewhere on a run = **3.77**
- median = **3**
- 5th–95th percentile = **1–8**

If the 57 eligible taxon labels are crossed with all 78,480 run-stop opportunities, the dense matrix would contain **4,473,360 potential cells**.

Only **2.59%** of those cells are observed positive CallingIndex 1–3 records.

This potential-cell count is a matrix representation, **not 4.47 million independent observations**.

The current manuscript's concentration decomposition contains **53 taxa**, a narrower inferential set than the 57 labels appearing somewhere in the complete eligible run set.

## Data actually entering the wetter–drier paired analysis

The main paired analysis contains:

- **4,236 wetter–drier pairs**
- **585 routes**
- **21 states**
- **8,472 pair-side survey instances**

Because adjacent-year pairing can reuse a survey run in two neighbouring pairs, those 8,472 pair sides correspond to only:

- **6,074 unique survey runs**
- **60,740 unique run × stop opportunities**
- **88,737 positive run × stop × taxon cells**

Among the 4,236 pairs:

- **2,693** are exact consecutive-year comparisons
- fraction consecutive-year = **63.6%**

Thus the inferential unit is not 88,737 independent call records. The paired design operates on **4,236 matched comparisons**, while the within-pair species × stop matrix supplies the spatial allocation information.

## Rain data

### NAAMP DaysSinceRain

The basic rain exposure is one `DaysSinceRain` value per eligible run:

- **7,848 run-level rain-recency values**

The matched-pair analysis uses:

- **6,074 unique runs** carrying DaysSinceRain;
- **8,472 pair-side rain values** when repeated use of a middle-year run in adjacent pairs is counted.

### ERA5 72-h precipitation

The post-hoc actual-rain analysis linked:

- **7,559 survey runs**
- **2,835 principal-history wetter–drier pairs**
- **428 routes**
- **20 states**

For every linked run, the script samples **72 hourly ERA5 total-precipitation values** before the survey midpoint.

Therefore the extraction used:

- **544,248 run-hour precipitation samples**
- summarized to **7,559 derived 72-h rainfall totals**

This run-hour count is not deduplicated for repeated use of the same ERA5 grid cell and hour.

Coverage is high:

- ERA5-linked runs / eligible runs = **96.3%**
- ERA5-linked principal-history pairs / all principal-history pairs = **97.2%**

## What the relative data volume means

The frog response is much higher-dimensional than the rainfall predictor.

For each survey night, rainfall contributes a small number of environmental quantities, whereas the frog survey contributes a **10-stop × multi-taxon acoustic-state matrix**.

That structure is why the paper can ask something beyond “does rain increase calling?”:

> the same night-level environmental context can be compared with how activity is allocated among taxa and among ten separated locations.

The information hierarchy is therefore:

1. **night / matched pair** — environmental contrast and inferential replication;
2. **10 route stops** — repeated spatial observations within each night;
3. **taxon × stop cells** — where each taxon's acoustic state is expressed.

The lower levels provide spatial structure, but they are clustered within nights/routes and cannot be counted as independent sample size.

## Recommended reader-facing scale description

Prefer:

> “The analysis was built from 7,848 standardized ten-stop surveys (78,480 stop visits); 6,074 unique surveys entered 4,236 wetter–drier matched comparisons, containing 88,737 positive taxon × stop acoustic records. ERA5 72-h precipitation was available for 7,559 survey runs and was constructed from 544,248 hourly run-level precipitation samples.”

Do not say:

> “We had 4.47 million observations.”

The latter is only the size of the implied dense taxon × stop × run matrix and would overstate independent information.
