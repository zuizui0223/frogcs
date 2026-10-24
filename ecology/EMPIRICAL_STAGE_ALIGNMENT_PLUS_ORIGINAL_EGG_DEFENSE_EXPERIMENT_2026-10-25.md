# NEW field stage-overlap result + VERIFIED previously published egg-predation experiment
Date: 2026-10-25. **Ecology-first evidence synthesis; no false claim of a new lab experiment.**

## Source tier A — new exploratory empirical result from independent Mohonk field monitoring
Mohonk Preserve CC0 Darwin Core Archive, DOI `10.15468/dypfbs`, **original publisher ZIP SHA256** `0309abd9afa4a224287d6853d79ae1f7111a3a7bb19b0d2337f05c280ef12b34` and internal occurrence TSV SHA256 `d52b288608a40c3b721f3561a57ace34728975522892a4fdc1d0b4f6ffb3610e`.

Study frame: **2016–2021**, 11 physical ponds, 59 pond-years, 240 original pond-date surveys; **235** dates where both target wood-frog tadpole and spotted-salamander egg stages were explicitly assessed.

- Both species' egg stages positively detected in 44 pond-years: **29** wood-frog egg first-positive earlier, **14** first detected on same date, **1** salamander first. The first-positive interval is *not* true oviposition delay.
- Wood-frog tadpoles and spotted-salamander eggs on the same sampled pond-date: **31** detections in **29 pond-years**.
- Within each pond-year, preserve n assessed sampling dates and positive-day totals for each species stage. Under an exact `Hypergeometric(n,a,b)` conditional date-alignment benchmark, expected co-detection **23.8690**, observed/expected **1.29875**, central 95% reference 19–29 co-detection dates, **one-sided conditional tail 0.00507345**.
- Circular rotation of each within-pond-year stage series (preserving local clustering but wrapping spring season endpoints): tail **0.00525744**. This is a sensitivity *sampling-time* null, not a realistic generative model for egg-laying.
- Strong between-year variation: 2020 **10 observed vs 5.967 expected**, 2021 **9 vs 6.567**; 2018 **1 vs 2.152** and 2019 **2 vs 2.733**. **Exclude 2020**: observed **21 vs 17.902**, ratio **1.173**, conditional reference tail **0.11827**. Therefore do NOT claim the overlap effect is stable across years.
- Jefferson salamander egg × wood-frog tadpole co-detection: **9 observed vs 8.1 expected**, reference tail **0.39834**. It is a different species and phenology, not a proof of absence of predation.

All overlap statistics are **post-hoc/exploratory conditional reference scores**. Data were seen before the new null test was specified and repeated pond-years within 11 ponds are clustered. **No attack, egg consumption, developmental fitness or predation rate was recorded.** The hypothesis "nonrandom phenological opportunity for previously documented tadpole–egg trophic interaction" is narrower than observed interaction-network rewiring.

**Source/test receipts:** [Mohonk source GitHub Actions success 40111669598](https://github.com/zuizui0223/frogcs/actions/runs/40111669598) and [stage-alignment 5-test success 40114746815](https://github.com/zuizui0223/frogcs/actions/runs/40114746815), artifact 12567632774. Code `ecology/data/mohonk/analyze_stage_overlap_null.py`, fixed exploratory contract `ecology/mohonk/EXPLORATORY_STAGE_ALIGNMENT_NULL_CONTRACT_V0_1.md`.

## Historical field sensitivity — NOT equal-effort longitudinal inference
Prior to 2016 the Mohonk original archive mostly reported positive-event stages without corresponding zeros. Among **129** pond-years from 1931–2015 where both species' eggs were positively recorded, **26** wood frog first, **98** same first survey date, **5** salamander first. For ≥3 distinct pond-year visits, **22/47** wood first, **21/47** ties, **4/47** salamander first. These confirm the detection-order *direction* appears in older records, not true exact laying chronology or changing risk under climate change. Source-only [GH Actions 40115372841](https://github.com/zuizui0223/frogcs/actions/runs/40115372841). Do not merge pre-2016 reporting with 2016–2021 null-model denominators.

## Source tier B — independent published factorial laboratory experiment, now verified from ORIGINAL DATA
Takahashi & Ruszala (2023), *Ecology and Evolution*, DOI `10.1002/ece3.10427`, original Dryad DOI `10.5061/dryad.bnzs7h4gn` v4; individual egg-mass-level **`Hatch_w.csv` SHA256** `8bf8166185fb1607710bd3bfd9a81d9f82ea34c1d8ae8874f562d5bee70076db`, 1,017 bytes.

The original file was successfully obtained via the **official Dryad version-archive endpoint** (`https://datadryad.org/api/v2/versions/253812/download`), NOT guessed from paper means. **32 independent egg masses** randomly assigned to **eight groups, n=4 masses per group**, with predator treatments no/low/medium/high tadpole density and outer protective egg jelly intact/removed:

| Tadpole predation treatment | Intact jelly: mass-mean hatch % | Removed jelly: mass-mean hatch % |
|---|---:|---:|
| No tadpoles | **72.26** | **90.69** |
| Low | **63.29** | **32.76** |
| Medium | **77.19** | **0.00** |
| High | **91.11** | **0.00** |

Between no tadpoles and high predator density, intact-jelly mean increased by **+18.8549 percentage points** and removed-jelly mean decreased by **−90.6940 pp**. Their mass-level factorial interaction on the mean scale was **+109.5489 pp**, with a descriptive 20,000-resample *egg-mass-stratified* bootstrap interval **[90.58,125.56] pp** (seed 2840223; only four masses per cell, so not guaranteed robust field-level coverage). Original published paper already reported a significant jelly × predator interaction and these treatment patterns. One experimentally estimated hatching proportion was corrected from >1 to 1 by the original authors and remains corrected in the public CSV. In removed-jelly medium/high cells, 0 masses hatched; incubation `Days=na` must remain missing, not 0 days.

The paper proposes that partial jelly removal can relieve oxygen-diffusion costs, but the public CSV contains **no oxygen measurements or direct individual attack rate variable**, so this proposed mediation is **not** independently tested by our reanalysis.

**Receipts:** [Dryad source direct sha-verified 40114789868](https://github.com/zuizui0223/frogcs/actions/runs/40114789868) (artifact 12568290831); [factorial 32-mass original-data reanalysis 40115055827](https://github.com/zuizui0223/frogcs/actions/runs/40115055827) (artifact 12568580191). Code `ecology/dryad_takahashi/reanalyse_original_factorial.py`, source contract `ecology/dryad_takahashi/EXPERIMENTAL_SOURCE_AND_CAUSAL_BOUNDARY_2026-10-25.md`.

## What science these levels justify
**Empirical opportunity:** an independently sampled pair of relevant frog tadpole and salamander egg stages occurs together in vernal pools more often than their within-pond-year recorded frequencies predict, **but the pattern is heterogeneous across years**.

**Experimentally known consequence in a distinct setting:** when these stages are forced together under controlled conditions, the effect on spotted-salamander egg hatching changes greatly with protective jelly state and predator density.

**Not established:** adult chorus→actual egg-laying lag, a site-level causal effect of tadpole phenology on salamander survival, realized egg predation in Mohonk, water/oxygen mediation, dragonfly indirect trophic cascades, or a multi-guild network changing signs across stages. Cross-dataset effect-multiplication is invalid.

## Research manuscript
[Ecology-first revised integrative natural-history note](../DRAFT_INTEGRATED_STAGE_TIMING_PREDATION_NATURAL_HISTORY_2026-10-25.md). This is a **draft**: the current genuinely new effect is a survey-date *temporal-overlap benchmark*, not a confirmed multi-species trophic-network causal effect. The manuscript must be submitted with accurate novelty and missingness disclosures; a higher-impact mechanism paper needs same-pond observed predation and embryo survival.

**Isolation:** branch `research/ontogenetic-interaction-phenology-2026-10`, completely independent of frozen `frogcs` `main` RC6 and its NAAMP source.
