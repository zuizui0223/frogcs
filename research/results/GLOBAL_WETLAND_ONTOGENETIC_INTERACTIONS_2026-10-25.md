# Global wetland-structure × ontogenetic-stage × documented trophic opportunity — evidence report

**Date 2026-10-25. Status: source-backed exploratory negative/weak-positive results.** The global macroecology programme supersedes site-level literature reanalyses as the primary *research-branch* focus, not the frozen RC6 JAE `main`. No predation flux or vegetation causality is inferred.

## 1. Actual global environmental layer obtained — not simply "Phragmites appeared in GBIF"

[Source audit](earthenv_wetland_1deg/observed_results.json) | [code](../scripts/earthenv_global_flooded_vegetation_1deg.py) | [verified CI](https://github.com/zuizui0223/frogcs/actions/runs/40197871125).

Original source **EarthEnv 1-km Global Consensus Land Cover, full v1, Tuanmu & Jetz 2014** ([data](https://www.earthenv.org/landcover); CC BY-NC 4.0). Downloaded and SHA256-audited the actual approximately 65.6 MB **herbaceous class 6**, 22.1 MB **regularly flooded vegetation class 8** and 28.1 MB **open water class 12** GeoTIFFs, with source nodata=255. Aggregated percentage prevalence to **52,560 valid 1° grid cells**, from 90°N to ~56°S; 14,917 of those cells contain positive class-8 regularly flooded vegetation.

**Critical scientific boundary:** original inputs reflect 1990s–2000s historical land cover, not 2026 `Typha` stands or seasonal inundated stems. Class 8 is often a mix of aquatic/woody wetland vegetation, *not a direct emergent-plant stem-density measure*. Ocean, including cells with 100% open-water consensus, is represented in the original global raster and cannot be interpreted as "zero plant cover at a pond".

The first GBIF–EarthEnv comparison found exactly that confound. [Prespecified source and documented post-readback ocean correction](../EARTHENV_WETLAND_MACRO_ALIGNMENT_SPEC_V0_1.md) restricted ecological comparison to 1° cells with **<50% open water** (land dominant). A coastal wetland in a majority-ocean cell is then missing from *this comparison*, not classified as biological absence.

Land-dominant EarthEnv valid 1° cells by class-8 background:

| Old flooded vegetation consensus | Grid cells | Median class-8 % | Median open-water % |
|---|---:|---:|---:|
| Near zero (<0.01%) | 5,567 | 0 | 0.0185 |
| Low/intermediate (0.01 to <1%) | 7,190 | 0.140 | 0.808 |
| Relatively high (≥1%) | 2,494 | 2.510 | 3.313 |

## 2. Test A: Does flooded vegetation make GloBI's *documented prey* more seasonally aligned than a matched unindexed prey?

[QA-corrected full result](earthenv_gbif_matched_stage/observed_results.json) | [code](../scripts/earthenv_wetland_matched_stage_links.py) | [CI](https://github.com/zuizui0223/frogcs/actions/runs/40198683867).

- Source 2026-09 **complete GloBI 24,453,954 records** ([DOI 10.5281/zenodo.22691479](https://doi.org/10.5281/zenodo.22691479)) and GBIF August-2026 open taxon-partition full Anura/Odonata stage×1°×year×month sampling.
- Reused **56 already selected source-documented predator→prey stage associations** with 2–5 alternative same-guild/same-stage prey candidates matched on source reporting and predator-shared geography. Alternative prey are **undocumented in the curated selected GloBI stage subset**, *not* true negative or experimentally confirmed non-prey.
- Measured phase-co-report ratio `Q = (1+same-grid-year-month observations) / (1+mean of 11 cyclic prey-month-shift counts)`. Primary: minimum 1 recorded taxon-stage per 1° grid-month; sensitivity: minimum 5.
- **Actual primary results** (one or more GBIF reports per stage):

| Land-dominant background | Link patterns with adequate within-tier matched prey | Focal documented Q greater than matched-prey median | Median focal-minus-control Q |
|---|---:|---:|---:|
| Near zero flooded vegetation | 48 | 24 | +0.0084 |
| Low/intermediate flooded vegetation | 54 | 28 | +0.0211 |
| Relatively high flooded vegetation | 36 | 21 | +0.1313 |

- Comparing **the same 32 source-linked stage pairs** that have enough matched reporting in both near-zero and relatively high flooded vegetation, the **median high-minus-near-zero change in partner-specific Q is −0.0281**. Twenty distinct predator species contribute. This does **not** support a consistent global enhancement of documented prey-specific phase congruence under historical flooded-vegetation cover.
- Threshold five retains only **5 paired links, 3 predator species** across both extreme strata; even if their point estimate is positive (+0.686), it is **not sufficient** for a robust large-scale claim.
- Source rain QA joins existing monthly 2010–2024 WorldClim/CRU cells, but the rain cells come from an initial focal GBIF mask rather than all months/sites in the expanded set. Descriptive focal-minus-alternative monthly rainfall medians are weak/inconsistent (−1.19 mm near zero; −1.63 mm low/intermediate; +1.14 mm high), not actual rain-triggered predation.

**Conclusion A:** Across this source-defined taxon/stage subset and coarse historic 1° habitat background, a wetland-specific boost in seasonal co-reporting of documented prey **is not established**. Source-level sampling and prey alternative documentation remain confounders.

## 3. Test B: Do *the same species* show different land-cover backgrounds when GBIF sightings are labelled aquatic larvae versus adults?

[Observed result](global_ontogenetic_wetland/observed_results.json) | [code](../scripts/global_ontogenetic_earthenv_reporting.py) | [CI](https://github.com/zuizui0223/frogcs/actions/runs/40199128009).

- Eligibility fixed **before reading habitat outcome**: original GloBI-backed Anura/Odonata source taxa must have ≥30 1°×year×month GBIF reporting cells and ≥5 unique 1° cells in **each** of adult and larval/nymph stages. Excluded unknown/egg/juvenile stage, missing raster and open-water-majority ocean cells.
- Compare mean EarthEnv class-8, class-12 and class-6 at **unique geographic cells within the same taxon × 10° latitude band × calendar month**, requiring ≥3 distinct geographic cells per stage. This avoids interpreting repeated years of one citizen-observation hotspot as independent biodiversity replicates.
- **22 species** pass global age-reporting input-volume gates, **21 species** pass the same-species habitat comparison (19 Odonata, 2 Anura), with **179** usable species×latitude-band×month strata. A stricter within-the-same-calendar-year version yields **718** positive age-site strata, but that does not guarantee geographic/observation comparability or predator contact.

| GBIF reporting-stage association | Odonata (19 species, 152 strata) | Anura (2 species, 27 strata) |
|---|---:|---:|
| **Immature minus adult regularly flooded vegetation background**, equally weighted across species (percentage points) | **+0.099**, bootstrap 95% interval **−0.004 to +0.215** | +0.013 (cannot obtain meaningful species-bootstrap interval) |
| **Immature minus adult open-water background** | **+1.285**, bootstrap interval **+0.023 to +2.531** | +0.812 (insufficient independent species) |
| **Immature minus adult generic herbaceous background** | **+1.046**, interval **−1.137 to +3.278** | −0.464 (insufficient independent species) |
| Species with positive flooded-vegetation contrast | **11/19** | **1/2** |
| Species with positive open-water contrast | **13/19** | **1/2** |

**Conclusion B:** An exploratory, relatively weak but potentially reproducible signal is that *reported aquatic immature dragonflies* tend to occur in historical 1° background grids with slightly more open water than adults, even after matching same species, latitude bands and season. The corresponding more-specific regularly flooded vegetation contrast is heterogeneous, with an interval spanning zero. **This is stage-labelled reporting-environment association, not habitat selection, ontogenetic movement, larval recruitment or trophic flux.** Only two frog taxa meet the data gates so no global anuran conclusion is warranted.

## 4. How this informs the original frog chorus/rainfall programme

- Existing frozen NAAMP RC6 finds rain-associated chorus activation and a within-taxon concentrated multi-site residual **+0.2969** beyond its weather/history comparator; independent NPS 2016–2023 confirms species-specific historical strong-call site recurrence with adjusted acoustic coefficient **+0.4642** on a different outcome. These two datasets contain *actual acoustics*, unlike GBIF.
- Macro GloBI×GBIF tests show how a **stage-specific range of trophic opportunities can be geographically and seasonally constrained**, but *neither* the documented partner-specific seasonal signal nor historic flooded vegetation mediation is robustly established.
- Old EarthEnv wetlands and new GBIF stage records use **different epochs and grains**. The next serious ecological field-wide target is a spatially time-coincident panel with monthly water-body inundation, species or remotely derived emergent/submerged stem architecture, true predator-stage occurrence and acoustic frog activity; controls should include spatial sampling effort, introduced species and separate source-study blocks.
- A positive biological possibility remains **landscape environmental filtering of larval habitat** (e.g. physical water habitat) rather than direct plant-generated adult chorus memory. **No conclusion of causal "rain → emergent reed bed → tadpoles → predator → chorus" has been demonstrated.**

## 5. Remaining data and model gaps

1. Landcover class 8 **is not** a direct herbaceous emergent reed class; for modern structure validate ESA WorldCover **2021 herbaceous wetland class 90** with per-cell sampling (different snapshot/scale) or remotely mapped wetland-specific vegetation and stem-height observations.
2. Within-grid/year stage reporting only, not synchronized within an actual pond; lack of source-level GloBI ecological interaction confidence prevents a global *realized trophic reversal* estimate. Phase/predator-specific negative controls should remain mandatory.
3. GloBI full stages 881 complete nonself patterns, but GBIF experimental Anura/Odonata stage categories have only 77 matched stage pairs in the expanded sample. Caudata, Dytiscidae, fish and other aquatic guilds remain unscanned in globally complete GBIF taxon partitions.
4. Monthly CRU rain series on 1° GBIF grid has weak mechanistic comparability to the **72-hour rain pulse** in frogcs NAAMP. NAAMP route geometry also needs source-blind QC before attaching NWI or plant layers.
5. All confidence intervals are exploratory source-taxonomic bootstrap on imperfect observational sampling; no independent regional study or true demographic likelihood model yet.
