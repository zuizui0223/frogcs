# Frozen experiment-level analysis plan: Fish × aquatic plants × guild
2026-10-22. Predeclared **after verifying only source headers and before opening numeric response columns** in Figshare v2, source SHA256 `86944f2d06b7e2739342a7b42ec4ff383df92d2cb8600a3d9c9c5de1f70758ae`, MD5 `e2d27edffb6c75b7208a609fafc79447`, 70,127 bytes.

## Experiment source
Šigutová et al. (2021), Scientific Reports doi:10.1038/s41598-021-98632-2; openly published workbook doi:10.6084/m9.figshare.16627561.v2, file 30796897. Four original worksheets with **first-row exact column labels**:

- `Bufonidae`: `species,date,block,plot,vegetation,predator,individuals,sexmale,sexfemale` (A1:I325)
- `Odonata`: `species,date,block,plot,vegetation,predator,tandemID,number of dips` (A1:H385)
- `Notonectidae`: `species,date,block,plot,vegetation,predator,individuals,sexfemale,sexmale,sexNA` (A1:K577)
- `Dytiscidae`: `species,date,block,plot,vegetation,predator,individuals,sexmale,sexfemale,sexNA` (A1:J265).

Source header-only QA 39787757063 PASS, result `exploration/FISH_MACROPHYTE_SOURCE_SCHEMA_RECEIPT_V0_1.json`.

The original article randomizes **six fish×plant combinations within each of four tank blocks**, then repeatedly measures organism use of the same tank/plot across dates. Inverts and amphibians were studied in different times and have different choice sampling and response scales. Fish is `predator` and may be merely a *perceived/non-consumptive risk* in the choice experiment. Toad male count does not measure tadpole survival.

## Exact source and analysis-population QA
1. Require official source original checksums and workbook sheets/header columns unchanged. Decode string/numeric workbook cells from XLSX XML, never silently coerce a string `na` to zero. Restrict vegetation to **`no`, `aq`, `aq_lit`** and predator to **`fish`, `no_fish`**; if other levels emerge, fail-closed and document.
2. Construct `species×block×date×plot` counts. For `Bufonidae`, the *primary frog outcome is `sexmale`*, following the paper's reported male habitat selection; keep `individuals` for an independent descriptive QA, never substitute. For `Odonata`, sum **`number of dips`** across tandemID rows for the same plot/date/species; for bug and beetle taxa, **`individuals`** in each plot/date/species. Negative/noninteger cell counts invalid; missing counts remain missing and gate out that species×block×date, no silent zeros. CSV not exported.
3. A species×block×date choice-event is complete only if **all six experimental treatments** appear exactly once after pool/plot aggregation; all six plotted tanks are identifiable and map to a stable fish/vegetation combination across dates. Any incomplete event excluded with counts/denominators logged before interpreting treatment sign.
4. Normalize each complete event's six counts to six **choice fractions** `p_t = count_t / sum(count_6)` if the sum is positive. Events with zero animals/egg dips across all six tanks are **unobserved-choice opportunities**, not experimental absences and excluded from the normalized choice analysis; report how many.
5. **Effective independent experimental replication = number of spatial `block` identifiers**, not date/plot/tandem individuals. For a species, average each contrast across its valid dates *within each block first*, then average equally across the blocks. All treatment assignments are fixed across the experiment; do not re-randomize each date.
6. Species with <3 independently represented experimental blocks, <3 dates or <12 complete block-date events are **underpowered** for block-level inferential claims. Dataset columns are not direct observations of true frog interspecific interactions or fish eating dragonfly larvae.

## Frozen H1: direct macrophyte manipulation for toads (primary)
For `Bufo bufo` and `Bufotes viridis`, each block/date has six treatments. In **fishless** tanks compare normalized male use at:
- `aq` (submerged+floating plants) **versus no plants**, and
- `aq_lit` (including additional emergent littoral plants) **versus no plants**.

Effect is equal-block average of the within-event fraction difference: `p(no_fish, plant) − p(no_fish, no)`, in percentage points of choice share; *not* survival, fecundity or frog abundance.

For each contrast, run an **exact block-preserving conditional randomization test**: keeping the three fishless physical plot outcome vectors across all dates fixed, enumerate all **six permutations of plant treatment assignments** within fishless plots in each participating block (for four blocks, `6^4=1,296` configurations; exact min two-sided P possible). Calculate two-sided P as fraction with `abs(T*) >= abs(T_obs)`, no Monte Carlo denominator shortcuts. For <3 blocks, do not promote statistical significance. Across the four focal H1 tests apply BH FDR q<0.05. Require at least 3 blocks, q<0.05 and the observed mean direction identical across ≥75% of blocks for a `manipulated_plant_choice_effect_supported` classification. Report each block's sign and all treatment mean choice shares. Test is conditional on fish-free assigned tank set and the exchangeable randomized vegetation labels in the original factorial block.

## Frozen H2: fish × vegetation modification (secondary)
For the same two frog taxa, compute **two interaction contrasts** per block:
`I_aq = [p(fish,aq)-p(no_fish,aq)] - [p(fish,no)-p(no_fish,no)]`;
`I_aq_lit = [p(fish,aq_lit)-p(no_fish,aq_lit)] - [p(fish,no)-p(no_fish,no)]`.

Within each species, for every block first average event-level I over dates and calculate grand mean across independent blocks with **t(df=blocks−1) 95% interval**, plus sign count. BH FDR across 4 secondary contrasts only if valid inferential estimates; no inflated n from visits or dates. A 4-block interval will be wide; if intervals include zero, label `vegetation_modification_not_established`. A nonzero fish×vegetation **factorial interaction** can be caused by altered perception/choice and does **not** identify mediation via dragonfly/other insects.

Also report **primary fish risk effect per species**: mean across three vegetation treatments of fish minus no-fish choice share, with block-level interval, plus descriptive fish/vegetation 2×3 treatment grid. Interpret fish effects as manipulated fish presence on selection choices, not survival.

## Frozen H3: taxonomic guild contrast (secondary context, not causal 3-body interaction)
Compute the same six-treatment *normalized choice fractions and block-level H2 contrasts* for Odonata, Notonectidae, and Dytiscidae, aggregating correctly by count metric, and retain each taxon identity. Aggregate descriptive group/guild contrasts only after showing per-species estimates and 4-block coverage. A guild-level contrast comparing frogs, dragonflies, bugs and beetles is a **difference in behavioral response to assigned treatments across experiments with different recording units/dates**, not simultaneous direct species×species interaction.

Predeclared cross-guild question: fish risk and added emergent plants have *heterogeneous sign* across 8 taxa; report whether any two taxon units' block-level response signs differ and each one's within-block repeatability, but **do not claim a universal guild causal 3-way interaction** from a non-random taxon sample of 8 species and different observation designs.

## Falsification and mechanistic interpretation gates
- **Only fish presence and plant architecture were manipulated.** The intermediate density of fish-consuming dragonfly larvae and subsequent frog survival was NOT factorially randomized with fish/plant choices in this experiment. Therefore H2 mediation through insect predators and a genuine contemporaneous **plant×fish×insect×frog causal path remain untestable here**. Do not use co-varying guild responses to infer trophic mediation.
- If a primary H1 plant contrast is significantly nonzero, it is an experimental effect on *male toad site selection under specific tanks*, **not** evidence that plants caused NAAMP *L. clamitans* strong acoustic detection.
- This previously published dataset reanalysis is **external mechanism evidence**, not a newly collected independent replication of NAAMP, and not a novel ecological discovery without new test outcomes beyond original paper.
- Stop if source QA sample units do not map to the original randomized 2×3 design; do not rescue by changing taxa, fish doses, plant levels, date windows, radii, treatment definitions, significance threshold or number of independent units.
- Raw copyrighted/attributed source workbook never committed; write only aggregate result JSON, auditable code and scientific note on independent exploration branch. JAE RC6 unchanged.
