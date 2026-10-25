# Ecological macro synthesis: adult calling does not uniformly date larval enemy exposure
**2026-10-25 — TWO SOURCE-VERIFIED EXPERIMENTAL/HISTORICAL SCALE ANALYSES, exploratory.** Frozen JAE RC6 `main` unchanged.

## Central biological question
Are breeding-associated male frog choruses a reliable temporal marker for when offspring enter aquatic communities and become potential prey/competitors of salamander larvae, odonate naiads and fish? More specifically, **does developmental carry-over from prior breeding seasons uncouple current-year acoustic signals from larval interaction windows**? How does the phenomenon compare with a broad regional stage-by-stage seasonal macro pattern?

## Independent original eight-pond acoustic × larval time series: REAL ecological observation

Carroll, Saenz & Rudolf (2023), original 2001–2006 **weekly funnel trap** records, Dryad DOI `10.25338/B8G92P`, original `funneltrapdata.xlsx` **SHA256 `302f1d976725ff926c682331a34e302262adbdb3be1f80fc67c1ccc990343f6f`** (196,918 bytes). Eight pond sheets, 296 rows per pond. Companion original Carter, Saenz & Rudolf (2018), original 2001–2015 **daily male acoustic recordings**, Dryad DOI `10.5061/dryad.84fq2vh`, original `dailycalls_dryad.xlsx` **MD5 `37dd4dc8289f0c1ce8d249791b3df558`** and **SHA256 `6a6cf3990080ef6b164aed4228e6a93c42c529d0d28e526eeedf8e1bd486aa8c`** (14,777,689 bytes).

Both original sources were obtained from the documented official Dryad version ZIP endpoints and independently byte-verified. Source-only [Carroll workflow 40158682712](https://github.com/zuizui0223/frogcs/actions/runs/40158682712); [Carter workflow 40152198914](https://github.com/zuizui0223/frogcs/actions/runs/40152198914). Original Carter daily workbook has >124MB uncompressed worksheet XML, so analysis used **incremental original XML row parsing**, not lossy Excel-to-image/chart export. All species code meanings checked against the two original workbook documentation sources.

**Overlapping years 2002–2006** (exclude partial 2001 trap start): **8 ponds × 5 years = 40 pond-years**, **2,080 weekly aquatic trap samples**, **13,045 distinct original pond-days with at least one valid species calling score**, **20,141 pond-week × frog taxon matched weekly observations** (source score completeness gate >=5 of seven preceding daily observations, by species). **102 pond×year×frog taxon** cases contained both positive male acoustic activity and an observed positive tadpole trap catch.

**First-positive acoustic signal to first-positive larval catch, not actual laying-to-hatching lag:**

| Original frog taxon (adult audio code) | Matched pond×years | Median days, first larval capture minus first adult calling | Cases larva first |
|---|---:|---:|---:|
| `Hyla versicolor` (HV) | **18** | **+38** | 0 |
| `Bufo woodhousii` (BW; now `Anaxyrus woodhousii`) | **12** | **+30.5** | 0 |
| `Rana sphenocephala` (RS) | 22 | +2.5 | 10 |
| `Rana clamitans` (RCL; now `Lithobates clamitans`) | **28** | **−61** | **20** |
| `Pseudacris crucifer` (PC) | 9 | +75 | 0 |

Source data contain further low-n species that are retained in the original derived CSV (RCA n=5, HC n=3, BV n=2, and a few n=1). **Across all 102 cases**, median lag +29 days, but **32/102** tadpole first-positive events were before first positive annual male calls. For `R. clamitans`, **nine of 28** first positive tadpole events fell exactly on the first aquatic sample of that year, suggesting left-censoring; excluding those still leaves **11/19** with tadpoles observed BEFORE the first annual male call (median −26 days). **All 18 HV and 12 BW** first tadpole records were after the first documented male call, with no larval onset exactly at the first aquatic sample.

**Matched habitat-year comparison** (same physical pond and calendar year, not new independent sites): BW and RCL overlap in **12 pond×years**. The BW-minus-RCL larval-detection lag is positive in **11/12**, median **+88.5 days**. This supports different timing relationships despite sharing an aquatic environment, although sampling and species histories can confound the comparison.

**Ecological meaning:** Adult chorusing is breeding-associated but not a universal marker of the *existing* tadpole cohort. `R. clamitans` can overwinter as larvae, so aquatic enemy exposure may be present before the current-year breeding chorus; `H. versicolor` and `A. woodhousii` exhibit an onset pattern consistent with larvae appearing AFTER the calling season begins. Calling onset ≠ fertilization, egg laying, or hatching; positive trap catches are a biased local catchability index, not individual recruitment. Original recordings occasionally contained blanks/invalid scores and year/date mismatches, excluded from the matched analysis rather than filled with zeros.

## Actual simultaneous weekly aquatic life-stage occurrence, not predation

The same 2,080 trap weeks report frog larvae (aggregated across 11 original amphibian taxa), `Naiad` (dragonfly aquatic larvae), `mole.sala.larvae` (Ambystoma talpoideum), and trapped fish. For each of 40 **pond×year** groups, fix sampled trap dates and marginal positive-week counts of frog and partner; under a hypergeometric within-pond-year sampled-week alignment benchmark, the expected co-positive weeks are `Σ(n_frog_positive×n_partner_positive/n_trap_weeks)`. Results:

| Potential partner captured on same week | Frog×partner co-positive weeks | Source-conditioned expected | Ratio | Exact one-sided upper tail | Circular-shift sensitivity |
|---|---:|---:|---:|---:|---:|
| Odonate aquatic naiads | **303** | **294.263** | 1.030 | **0.111** | 0.170 |
| Mole salamander larvae | **22** | **26.186** | 0.840 | No excess indicated | No excess indicated |
| Fish (bass or green sunfish in traps) | **26** | **23.777** | 1.093 | 0.295 | 0.302 |

The fixed-marginal and cyclic reference laws are *sampling-time* nulls; pond-years within 8 ponds and seasonal week patterns are not ecological iid replicates. Neither naiad nor fish co-capture convincingly exceeds the original pond-year stage-prevalence baseline. Salamander larvae were recorded in only two of the eight ponds; no universal amphibian competition effect follows.

**Why this matters:** A real stage-dependent aquatic exposure landscape occurs at the SAME ponds where male chorusing is observed. But a conspicuous frog–naiad presence overlap, even 303 simultaneous capture weeks, does not imply exceptional synchronization or direct feeding. The **call-to-larva lag differs biologically by amphibian life-history strategy**, while broad enemy stage overlap appears mostly compatible with stage occurrence prevalence. This distinguishes *reproductive acoustic timing* from *trophic opportunity*.

## Macro-scale independent stage window: 2015–2025
Across **21,979 original iNaturalist/GBIF stage-annotated records** in five North American latitude bands, **37/37 eligible region×years** show greater frog-tadpole ↔ salamander-*larval* seasonal overlap than frog-tadpole ↔ salamander-*egg* overlap (mean +0.292 on the 0–1 monthly overlap scale). Species-balanced and calendar-phase sensitivities remain positive overall (31/37 phase-adjusted region years). At 0.5° grid×year×month the frog-larva stage was recorded in 2,969 cells, of which 417 co-recorded salamander larvae and 275 co-recorded salamander eggs. These are **landscape-scale opportunity windows**, not same-pond interactions.

Together these two independently sourced scales strengthen the ecological hypothesis that **developmental stage, especially persistent larval cohorts, matters when mapping adult reproductive signals to potential antagonistic encounters**. They do NOT prove tadpole predation, reproductive survival or adult frog movement, nor can 2002–06 Texas observations be treated as temporal replication of 2015–25 GBIF habitats.

## Where vegetation fits — do not falsely claim a measured effect
The original eight-pond source reports **two forest complexes**, and its trap data contain fish/odonates/salamanders, but **neither original XLSX measures submerged/emergent vegetation fraction, pond-level canopy, water depth or hydroperiod**. The Carter workbook maps pond IDs 1–4 to Davy Crockett and 5–8 to Stephen F. Austin; fish capture occurred mostly in pond IDs 6–8. This requires care: published geographic forest/fish descriptions are not a paired manipulation, and `no fish captured` is not proven `fish absent`. Forest identity is perfectly confounded with numerous pond-level variables; do not estimate a causal vegetation effect from forest label or fish presence. Vegetation remains a **plausible modifier** of naiad habitat, egg placement and larval detectability but is **not empirically tested** with these sources.

## Source validity, inference boundaries and next direct ecological test
- Source workbooks from earlier peer-reviewed studies, not a new experimental frog/habitat manipulation. This is an **exploratory reanalysis** after broad stage-window hypotheses have been inspected, not preregistered verification.
- `R. clamitans` and some other species have long/overwintering larval periods; a negative annual first-detection lag is not evidence of eggs laid before males call during that same season.
- Larval trap series are weekly, breeding calls daily and some `dailysum` scores are missing. Period starts and source documentation must be honoured; *observed* zero is distinct from missing.
- Measured adult male calling intensity is linked to breeding behaviour but cannot identify actual laying dates, successful reproduction, number of larvae produced or density-dependent trophic response.
- `Naiad`, salamander larval and fish records are **co-captures**, not feeding/competition events. An interaction requires direct predation, feeding, growth or offspring survival outcomes.
- To test vegetation×calling×trophic mechanism, the decisive study must record vegetation or canopy at exactly these dated ponds and aquatic enemy stages, or use independent monitored wetlands with both *actual vegetation and aquatic interactions*.

## Reproducibility
All source checksums, streaming OOXML code, original-year group summary, 2,080 weekly source catches, 20,141 source-matched taxon-week rows, 102 first-positive acoustic↔larval-stage lags and exact pond-year co-detection nulls are supplied in the conversation analysis archive `frog_chorus_larvae_macro_reanalysis_2026_10_25.zip`. Source originals from GitHub action [Carter 40152198914](https://github.com/zuizui0223/frogcs/actions/runs/40152198914), [Carroll 40158682712](https://github.com/zuizui0223/frogcs/actions/runs/40158682712). Full regional stage results and scripts under `ecology/macro_stage/` and [original GBIF 40150271511](https://github.com/zuizui0223/frogcs/actions/runs/40150271511).

Frozen JAE RC6 `main` unchanged.
