# Experiment-backed aquatic plant hierarchy: randomized 2×3 fish × macrophyte factorial, eight taxa
**Date 2026-10-22.** Separate exploratory reanalysis of an already published 2021 experiment, **not** the frozen frogcs JAE RC6 manuscript and **not** new frogcs field experiments.

## Main evidence and strongest claim

**Manipulated aquatic plant habitat structure changed the male breeding-site choice allocation of fishless-habitat specialist `Bufotes viridis`.** The response is species- and fish-context dependent at the descriptive level; this result is substantially more direct than NAAMP's observational NWI vegetation correlates.

Source: Šigutová et al. 2021, *Scientific Reports* doi:10.1038/s41598-021-98632-2. Original 2021 experiment: 2 fish statuses × 3 macrophyte structures, 6 treatments randomized **within each of 4 physical experimental blocks**, recorded on repeated dates. Public data doi:10.6084/m9.figshare.16627561.v2 (original data file 30796897), 70,127 bytes, official MD5 `e2d27edffb6c75b7208a609fafc79447`, source SHA256 `86944f2d06b7e2739342a7b42ec4ff383df92d2cb8600a3d9c9c5de1f70758ae`. Full file checked before opening outcome values.

Taxonomic sampling in source workbook: **Bufonidae** 324 source records, Odonata 384, Notonectidae 192 nonempty records, Dytiscidae 264. Four sheets and original treatment labels verified before treatment readback in [Actions 39787757063](https://github.com/zuizui0223/frogcs/actions/runs/39787757063). Primary endpoint is **male toad counts** (not tadpole fitness), secondary is number of dragonfly oviposition dips or insects occupying the assigned pool. One datum is a pool-use observation and repeated dates/individuals are **not independent experimental units**.

## H1 — aquatic vegetation directly changes male toad habitat choice: one positive, properly bounded result

Treatments `no` (no macrophytes), `aq` (submerged+floating), `aq_lit` (submerged+floating+emergent littoral), each under `no_fish` and `fish`. For each species×block×date with all six treatments and a nonzero observed male count, compute the selected fraction for each tank `p(count_t / sum(count_6))`. Average date-specific fractions **within each independently replicated physical block**, then average equally across four blocks.

Four predeclared fishless comparisons (2 toads × 2 plant levels vs no plants), calculated as block-preserving **EXACT 3!^4=1,296 plant-label permutations** among assigned fish-free tanks, BH FDR across four. Source-verified, distinct scientific replicates: 4 blocks, *Bufo bufo* 23 positive-choice block-date occasions, *Bufotes viridis* 22.

| Species | Source manipulation at no fish | Difference in male choice share (pp) | Exact randomization P | BH q (4 contrasts) | Classification |
|---|---|---:|---:|---:|---|
| `Bufo bufo` | submerged+floating vs bare | **+12.40** | 0.2346 | 0.3457 | not supported |
| `Bufo bufo` | submerged+floating+emergent vs bare | **+10.25** | 0.3410 | 0.3457 | not supported |
| `Bufotes viridis` | submerged+floating vs bare | **+45.86** | **0.00617** | **0.02469** | **experimental plant-choice effect supported** |
| `Bufotes viridis` | submerged+floating+emergent vs bare | **+20.86** | 0.3457 | 0.3457 | not supported |

For `B. viridis`, average block-equal male choice fractions were:
- no fish + bare plants: **9.58%** of all six-tank male selections;
- no fish + submerged/floating plants: **55.45%**;
- no fish + added emergent littoral: **30.45%**;
- fish + submerged/floating: **1.19%**;
- fish + added littoral: **3.33%**;
- fish + bare: **0%**.

Those are **fractions of site-use observations across six simultaneously available choices**, not occupancy probabilities, mating outcomes, numbers of tadpoles, or probabilities of callers in NAAMP. The increase due to `aq` plants under no fish is specific to male *B. viridis* in the original experimental tanks; not evidence for universal macrophyte effects.

## H2 — does fish presence modify the plant effect?

For each toad species and plant level, compare the fish-minus-fishless choice share against the same fish effect under no plants. This is **the interaction contrast**, calculated at original independent block level with Student-t(df=3) CI and four predeclared H2 comparisons BH corrected.

| Taxon | Plant level | Fish×plant modification in share (pp) | 95% four-block CI (pp) | nominal P | BH q |
|---|---|---:|---|---:|---:|
| `Bufo bufo` | aq | +9.44 | −11.31 to +30.18 | 0.243 | 0.325 |
| `Bufo bufo` | aq_lit | −0.70 | −30.80 to +29.41 | 0.946 | 0.946 |
| `Bufotes viridis` | aq | **−44.67** | **−86.56 to −2.79** | 0.0426 | **0.171** |
| `Bufotes viridis` | aq_lit | −17.53 | −55.14 to +20.08 | 0.235 | 0.325 |

The *B. viridis* aq contrast was negative in **all four** independent blocks, strongly suggesting fish risk reduces the fishless-vegetation benefit, but **the four-test FDR criterion is not passed**. Do not claim a confirmed fish×plant interaction or use its nominal 95% interval as if multiplicity corrected.

A related **manipulated fish-presence main contrast** across the three vegetation levels for *B. viridis* was **−30.32 percentage points** (95% CI on four blocks −36.99 to −23.65; four of four block effects negative), whereas *B. bufo* showed +7.74 (CI −5.87 to +21.34). These CIs are descriptive independent-block intervals and do not by themselves identify a formal multiple-comparison-protected fish×vegetation mechanism. The published paper likewise reports stronger fish avoidance by specialist semiaquatic taxa; this is a **source-backed reanalysis of its known treatment response**, not independent discovery of fish avoidance.

## H3 — comparative life-history responses exist; true ecological higher-order interaction not identified

The same Figshare workbook contains toad males, Odonata oviposition dips, Notonectidae adults, Dytiscidae adults:

- `S. danae`: 14 complete normalized block-date events/4 blocks; descriptive fish-average effect **−13.56 pp** (block CI −21.87 to −5.25), suggesting fish avoidance in its original behavioral choice units.
- `A. sulcatus`: 22 complete events/4 blocks, fish-average **−4.22 pp** (CI −13.30 to +4.86); `D. marginalis`: 22 events/4 blocks, **−0.63 pp** (CI −15.60 to +14.35). No individually interpretable strong departure.
- `S. sanguineum`: only 8 valid independent block-date choice events, below the frozen ≥12 gate, so statistical inference is **underpowered**.
- `N. glauca` and `N. obliqua`: source records never supplied all six treatment cells in any species×block×date group under the frozen six-pool join; these taxa **cannot be treated as negative outcomes** under our strict same-choice-set design. Their inclusion in the original paper is not refuted; our data structure/eligibility test differs from their original GEE analysis.

Species and guild differences in fish×plant responses are **statistical response heterogeneity** across separately timed repeated experiments. There is no randomized third-species treatment in the present data, so this result does **not identify frog×frog competition, frog×dragonfly trophic mediation, or three-body causal interactions**.

## Hierarchy of actual evidence (not a complete inferred causal chain)

1. **PLANT → TOAD MALE CHOICE**: **experimentally supported** in `B. viridis` for submerged+floating vegetation in fish-free tanks (randomized contrast q=0.0247).
2. **FISH → TOAD MALE CHOICE**: strong blocked negative response in the specialist `B. viridis` (−30.3 pp, four of four negative), and very different descriptive response in generalist `B. bufo`.
3. **PLANT × FISH EFFECT MODIFICATION**: *plausible in one toad*, large nominal contrast but **no BH-supported fish×plant moderation in four predeclared tests** (q=0.171 for most promising).
4. **PLANT → FISH/ODONATE PREDATOR → FROG SURVIVAL**: not measured under factorial causal mediation. The separate Adams et al. 2003 experiment on invasive bullfrogs and sunfish showed fish suppressing dragonfly predation can indirectly facilitate tadpole survival (doi:10.1046/j.1461-0248.2003.00435.x), which is **published context**, not frogcs experimental data or mediation estimated here.
5. **≥3 simultaneous biotic species higher-order causal interaction**: not identifiable from data where species experiments are conducted sequentially and no three-species factorial manipulation exists. The measurable fish×plant×species-term is *treatment response heterogeneity*, not a third-party species interaction.

## Implication for frogcs and honest generalization

NAAMP shows plant-associated adult **frog calls** and residual spatial pairwise co-detection patterns. This 2021 European randomized mesocosm demonstrates in a separate experimental system that **some breeding male amphibians actively choose water-plant structure and react strongly to fish context**. It supplies a biologically plausible mechanism **in principle** but does **not confirm** that the NAAMP North American vocalization network arose via the same pathway. Likewise, plant context effects on a male toad's available-site choice cannot be extrapolated to a tadpole survival cascade or an irreducible three-species interaction.

A distinct, synchronized 2×2×2 (plant/fish/invertebrate predator) or 2×2×2×2 (add other frog species) factorial experiment with repeated same-species call/site-use and larval outcomes would identify the currently missing causal terms.

## Reproducibility

- Source + meaning prelock: `exploration/FISH_MACROPHYTE_MULTI_TAXON_SOURCE_CONTRACT_2026_10_22.md`.
- Response-blind source receipt: `exploration/FISH_MACROPHYTE_SOURCE_SCHEMA_RECEIPT_V0_1.json`; [success run 39787757063](https://github.com/zuizui0223/frogcs/actions/runs/39787757063).
- Frozen experiment contrast plan: `exploration/FISH_MACROPHYTE_FACTORIAL_CAUSAL_CONTRACT_V0_1.md`.
- Exact block permutation, blocked interaction code: `exploration/run_fish_macrophyte_factorial_block_contrasts_v0_1.py`.
- Full strict JSON model result `exploration/FISH_MACROPHYTE_FACTORIAL_BLOCK_RESULT_V0_1.json`; [success run 39789338419](https://github.com/zuizui0223/frogcs/actions/runs/39789338419) (artifact 12429668588).
- Original official Figshare workbook not committed/redistributed. New script and synthesis on isolated exploration branch; **JAE RC6, main, manuscript, SI and submission unchanged**.
