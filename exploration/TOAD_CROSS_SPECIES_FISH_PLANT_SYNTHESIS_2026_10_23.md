# Two toads respond differently to the same fish×plant tank design — post-hoc between-taxon audit

**2026-10-23.** External Šigutová et al. 2021 source-verified 2 fish ×3 vegetation experiment, four physical blocks, but **toad species were observed in different experimental windows**. This is a *treatment response heterogeneity* question; it cannot identify a direct `B. bufo × B. viridis` biotic interaction, a fish→dragonfly→frog mechanism, or a ≥3-species causal interaction.

## New matched-block contrast (computed and multiplicity-controlled)
For each original physical tank block, separately obtain the existing fish×plant difference-in-differences `I_sp,v=[fish,v−no_fish,v]−[fish,no−no_fish,no]` (in six-tank use shares). Compare `I_Bufo bufo−I_Bufotes viridis` across blocks and calculate the equal-block mean and t(df=3) interval. Apply Benjamini–Hochberg FDR over **two** retrospectively selected vegetation levels. One observation = independent *block*, never a date or organism.

| Plant contrast | Cross-taxon difference in fish×plant response | Block-t 95% interval, pp (unadjusted) | Nominal P | BH q (2 comparisons) | Judgment |
|---|---:|---:|---:|---:|---|
| submerged+floating (aq) | **+54.11 pp** | 10.53 to +97.70 | 0.02893 | **0.05785** | **FDR not supported** |
| submerged+floating+emergent (aq_lit) | +16.83 pp | -21.87 to +55.54 | 0.26035 | 0.26035 | FDR not supported |

The `aq` sign is positive in 4/4 matched physical blocks; omit-one-block point estimates remain positive. Nevertheless the nominal P of ≈0.029 is **not evidence for confirmatory heterogeneity after 2-contrast FDR**, and the four-block confidence interval is NOT multiplicity-corrected.

The original fishless *Bufotes viridis* plant-choice response remains +45.86 pp (exact permutation BH q=0.0247), while the fish-present *Bufo bufo* plant preference was a **post-response-inspection** contrast of +21.84 pp (BH q≈0.01235 for the separate fish-present four-test family). Within-taxon fish×plant interaction H2 remained **0/4 BH supported** (strongest q≈0.171). Comparing significance levels between strata or taxa is invalid as a formal interaction test.

## Original experimental replication and bounded interpretation
- Original source: Šigutová et al., *Scientific Reports* 2021, https://doi.org/10.1038/s41598-021-98632-2, data DOI https://doi.org/10.6084/m9.figshare.16627561.v2, source SHA256 `86944f2d06b7e2739342a7b42ec4ff383df92d2cb8600a3d9c9c5de1f70758ae`.
- Numerators and denominators: allocation of observed **male use records** among 6 simultaneously available pools, averaged first over dates **within each randomized block**, then across four blocks. No abundance, survival, tadpole recruitment, fish–dragonfly consumption or NAAMP acoustic mechanism.
- Between-species trials at different times mean taxon and time are partly confounded; hence these differences are not simultaneous competition effects.

## Independent external higher-order claim audit (important)
Warfe & Barmuta 2004, *Oecologia*, DOI https://doi.org/10.1007/s00442-004-1644-x, randomized plant *analog shape* × density × fish predator × damselfly predator; **mosquito larvae**, not tadpoles, were prey. The published 4-way ANOVA identifies the **plant-analogue shape main effect** (P=0.005) but **not plant density** (P=0.383), and a substantial fish×damselfly term (F=41.856, printed P<0.001); however, the targeted **shape×fish×damselfly interaction was P=0.382**, and density×fish×damselfly P=0.823. Thus structural **shape, not just amount/cover, should be experimentally measured**, but this is not formal evidence that shape changes predator–predator interaction strength. Their Myriophyllum-only observed-vs-additive combined predator contrast P=0.034 and overall deviation P=0.043 are *different tests*, not evidence that structural shape formally changes the fish×damselfly factorial term. The species were simultaneously present in the factorial tanks, unlike the toad choice experiments. This original experiment supplies a genuine **two-predator non-additivity** context, not a confirmed structure-modified three-factor interaction.

Dryad DiGiacopo & Hua 2022 published toad/parasite leaf-litter study was externally source-verified only through metadata, with HTTP 401 and 403 access blocks; see [branch record](https://github.com/zuizui0223/frogcs/blob/exploration/leaf-litter-host-parasite-source-2026-10-22/exploration/LEAF_LITTER_DRYAD_ACCESS_BLOCK_2026_10_23.md). There is **no frogcs numerical reanalysis** of those data.

## Remaining gate
To prove genuine plant-mediated frog higher-order ecology, synchronously and independently manipulate plants (P), fish (F), odonates (O), and another frog competitor (C) while holding the focal tadpole species and baseline density fixed. Predeclare the risk/survival contrast scale, independent tank blocks, mediator intervention, and the fish×odonate×competitor (`D_FOC`) and plant modification (`D_PFOC`) contrasts. A nonzero cross-taxon **different-experiments** difference does not close this gate. JAE RC6 main and submission untouched.

Script `exploration/run_fish_plant_between_toad_responses_v0_1.py`; numerical audit `exploration/TOAD_CROSS_SPECIES_FISH_PLANT_HETEROGENEITY_V0_1.json`.
