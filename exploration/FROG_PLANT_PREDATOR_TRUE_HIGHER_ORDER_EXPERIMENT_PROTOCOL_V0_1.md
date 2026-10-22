# True plant-mediated amphibian biotic hierarchy — identified causal interventions, v0.1
2026-10-22, future experiment **protocol only**, not field results or user-authorized animal experiment. Remains independent of submitted RC6.

## What existing data prove, and what is still missing

**Completed:** independent published 2021 randomized 2 fish×3 macrophyte experiment reanalysed from source-verified data. Fishless macrophytes change adult male `Bufotes viridis` habitat-choice shares (`aq` vs `no` **+45.86 percentage points**, exact block-preserving P **0.00617**, four-test BH q **0.02469**). Fish×aq modification large negative but **not** BH significant (q **0.1706**) and cannot be promoted. Frogcs NAAMP is a separate, nonrandom observational frog calling archive.

**Missing:** trophic mediation (plant → fish/odonate predator → frog), direct frog-to-frog behavioral effects, and irreducible higher-order **biotic** interactions. Cross-sectional NWI × acoustic associations, even complex network moments, cannot identify them.

Separately published examples:
- Adams, Pearl & Bury (2003), doi:10.1046/j.1461-0248.2003.00435.x: non-native fish reduced dragonfly larval predation, increasing invasive bullfrog tadpole survival, experimentally, **without an aquatic plant manipulation**.
- Arribas et al. (2018), doi:10.3389/fevo.2018.00028: an 80-tank randomized 2 competitor-frog presence×5 predator type/caging study found **predation × competition × prey taxon heterogeneity** in growth and stable isotope outcomes; it does **not** demonstrate a macrophyte-mediated causal chain.
- Šigutová et al. (2021), doi:10.1038/s41598-021-98632-2: fish×macrophyte manipulation changes breeding habitat choices of toads, odonates and aquatic insects; experiments by guild are not simultaneous ecological 3-species interactions.

These studies show causal links *can exist* in nature, but no released dataset tested in this frogcs project jointly intervenes on all desired causal nodes.

## Trial A (adult acoustic mechanism): plant structures modify the response to heterospecific calls

**Question:** Does vegetation structure causally modify how `Lithobates clamitans` males change their calling location/activity upon hearing `L. catesbeianus`? Avoid interpreting mere acoustic transmission differences as behavior.

2×2 factorial:
- (P): randomized standardized artificial/native emergent structure low/high at a consenting experimental wetland or fenced enclosure, standardized surface area, same sound-absorbing materials documented;
- (A): randomized calibrated bullfrog acoustic playback versus matched background/silent playback.
- Use genuine biological response `Y`: focal green-frog subminute acoustic detection time/CallingIndex or matched site-movement observations, with independent continuous recorder measurements of sound pressure and propagation *and pre-playback baseline*.
- Site/wetland is biological replication; at least four randomized matched independent sites per plant×playback combination for feasibility, but confirmatory sample size must be defined from pilot variance. Do not count each second of audio as an independent animal.
- Avoid playback habituation: predeclared washout, balanced ABBA order and non-treatment controls; no mixing false calls/automated species detectors before blind manual audit.
- Primary **plant×bullfrog-call effect modification**:
  `[Y(high plant, playback) - Y(high plant, control)] - [Y(low plant, playback) - Y(low plant, control)]`.
  Use block-wise signed paired contrasts across replicate ponds, not a naive count of second-by-second observations. A nonzero randomized coefficient would support *vegetation-modified acoustic behavioral response*, not direct long-term interspecific competition.

**Permissions:** amphibian playback, acoustic recording and plant manipulation must follow local animal welfare, conservation, access and wetland management approvals. No field deployment or live-animal exposure initiated by this protocol.

## Trial B (larval trophic hierarchy): randomized P×F×O×C experiment

A **fully randomized four-factor 2×2×2×2 mesocosm** with 16 treatments:
- P = low/high experimentally standardized macrophyte structural complexity (real plants or nonnutritive structural mimics, source-standardized);
- F = fish absent/present (specified ecologically legal, ethical species; fish sizes and number fixed);
- O = predatory odonate larvae absent/present (initially equal density);
- C = other frog species tadpoles absent/present (e.g. locally native other taxon, not importing invasive bullfrogs);
- Every tank has the same baseline focal frog tadpole taxon/density, stage and age, in controlled water volume and hydroperiod.
- Assign all **16 cells independently within each spatial block**, e.g., a confirmatory *design proposal* of eight blocks×16 independent tanks = **128 tanks**. Run a smaller separate pilot **2 blocks×16=32** only to establish feasibility and variance. Do not claim 128 is statistically powered until a pilot-derived, specified minimal ecological effect and simulation-based power analysis is run.
- Record staged tadpole survival, growth, behavioral distribution (littoral vs open water), odonate survival/density, fish condition, actual plant structural coverage, water depth/temperature/oxygen and consumptive events over synchronized windows. Independent unit **tank**, with repeated measures nested in tank; block is randomization stratum.
- Bins of same taxa across blocks need consistent species identification; missing animal records != zero survival without complete fate tracking.

**Identifiable randomized contrasts**:
1. Direct plant moderation of competitor frog effect, with fish/odonate absent:
`D_PC=[Y(P1,F0,O0,C1)-Y(P1,F0,O0,C0)]-[Y(P0,F0,O0,C1)-Y(P0,F0,O0,C0)]`.
2. Effect of odonate presence as modified by fish at fixed plant/competitor levels:
`D_FO=[Y(P,F1,O1,C)-Y(P,F1,O0,C)]-[Y(P,F0,O1,C)-Y(P,F0,O0,C)]`.
   This is a **causal interaction of manipulated treatments**, *not* itself a natural indirect effect. Fish can prey on focal tadpoles and odonates; plant structure affects both encounter rate and frog choice.
3. **Genuine manipulated three-biotaxon effect modification** on focal survival at fixed P:
`D_FOC = Δ_fish Δ_odonate Δ_competitor Y`, the signed eight-cell alternating factorial contrast, with all pairwise treatment effects explicit. If this differs from zero under the planned block randomization test, biotic treatment effects cannot be represented solely by the additive main effects and 2-factor effects within that chosen response scale.
4. **Plant modification of the biotic triple**, a four-factor coefficient:
`D_PFOC = D_FOC(P1)-D_FOC(P0)`. At least 8 randomized blocks and registered biological effect threshold are needed before treating null and interval precision as sufficient.

**Distinguish mediation, not just interaction:** additionally randomize/restore odonate density after fish predation (e.g., odonates inaccessible to fish behind controlled, validated mesh, plus a no-odonate matched-sham arm) and *measure time-resolved odonate abundance and tadpole survival*. To claim fish effects are mediated by odonates, require an identified intervention on mediator density, temporal ordering and proper total/direct/indirect effect estimands. An observed fish×odonate interaction without the mediator intervention cannot uniquely identify fish → odonate → frog.

## Analysis/validation gates before any claim
- Predeclare which single focal frog life stage and site-use/survival endpoint constitutes the primary outcome; do not conflate calling adult females/males and tadpole fitness.
- Treatment randomization and experiment block assignment recorded before animal response collection; no replacement species post hoc.
- All contrast comparisons use **block-balanced tank-level** outcomes with clustered repeated measures (and appropriate binomial model for survival count); reassign only whole-tank treatments in permutation tests, **never observation timepoints**.
- Primary H1 **D_PC**, primary H2 **D_FO with mediator manipulation**, primary H3 **D_FOC**. Adjust across the three hypotheses rather than interpreting selected nominal P values. Fish/odonate/competitor/caged-treatment welfare protections approved before implementation.
- If 4-way interaction cannot be powered under available blocks, retain it as exploratory and focus directly on D_PC/D_FO; do not call noisy 4-way high-order effect supported.
- Compare field acoustic choice with larval survival only as **life-stage complementarity**, not identity of mechanism. A plant-induced change in adult calling position need not imply improved tadpole survival or population success.

## Current repository readiness
- Numeric 2021 source reanalysis and honest H1/H2/H3 evidence: `exploration/FISH_MACROPHYTE_FACTORIAL_BLOCK_RESULT_V0_1.json`.
- Interpretation: `exploration/FISH_MACROPHYTE_8_TAXON_EXPERIMENT_ECOLOGICAL_SYNTHESIS_2026_10_22.md`.
- No experimental animals, park services or human participants contacted, tested or deployed. Trial A/B are prospective design artifacts, **not completed experiments**.
- Frozen JAE RC6 protected, main untouched.
