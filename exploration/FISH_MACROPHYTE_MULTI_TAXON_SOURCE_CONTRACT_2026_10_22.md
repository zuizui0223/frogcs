# Fish × aquatic macrophytes × taxa: experimental mechanism study — source-only lock
2026-10-22. New independent user-directed experiment-analysis project on separate branch, not RC6.

## Scientific target and inference layers
Three distinct unverified frogcs hypotheses:
- H1 **Direct habitat engineering:** manipulating aquatic vegetation changes habitat-selection response in focal anurans (test species/vegetation main contrasts).
- H2 **Vegetation modifies biotic context:** whether experimentally present fish affect anuran choice differently among three structural plant treatments (fish×vegetation interaction). This is an interaction of **two manipulated abiotic/biotic factors**, not proof of ecological mediation through insects.
- H3 **Response hierarchy across interacting guilds:** do anurans, predatory odonates, aquatic bugs and diving beetles show different fish×plant responses, particularly semiaquatic vs aquatic life histories? This is a cross-taxon moderation, **not** genuine 3-species simultaneous causal interaction.
- Unobserved causal mediation **plant → predatory insects → tadpole** and irreducible simultaneous three-species interactions cannot be inferred from treatments absent manipulation of intermediary abundance. Explicitly **not tested** by this data.

## Independently published randomized experiment
Hana Šigutová et al. (2021), *Specialization directs habitat selection responses to a top predator in semiaquatic but not aquatic taxa*, Scientific Reports 11:18928, https://doi.org/10.1038/s41598-021-98632-2.
2×3 factorial fish/no fish × macrophyte structures (none / submerged+floating / submerged+floating+littoral emergent). **24 tanks in 4 experimental blocks**, six treatments per block. 8 animal species:
toads `Bufo bufo`, `Bufotes viridis`; odonates `Sympetrum sanguineum`, `S. danae`; hemipterans `Notonecta glauca`, `N. obliqua`; coleopterans `Dytiscus marginalis`, `Acilius sulcatus`. Experimental individuals often sampled repeatedly, only among tanks of one block. For dragonflies outcome is oviposition **dips**, for others counts of habitat-choice visits; these are **not identical measurement units** or direct abundance/survival effects. Species experiments may have occurred on different sampling dates/years, so do not interpret cross-guild response correlation as simultaneous species interaction.

Open Figshare version 2 https://doi.org/10.6084/m9.figshare.16627561.v2, item ID **16627561**, file **30796897** `Dataset_figshare.xlsx`, 70,127 bytes, supplied MD5 `e2d27edffb6c75b7208a609fafc79447`, official https://ndownloader.figshare.com/files/30796897.

## Phase 1: pre-outcome source-only gate (run first)
Download exact official xlsx and require the frozen byte size AND MD5. Inspect internal XML only to list worksheet names, each worksheet's header row, shape (maximum row/column), repeated block / tank / round / species metadata field candidates; do **not** read dependent-variable numbers before freezing the inferential protocol. If official file access fails or content differs, stop and preserve outcome-blind receipt.

## Phase 2: frozen measurement-aware experiment
Only after schema confirms treatment, experimental block, taxon identity, repeated observation occasion, choice/count outcome and denominators, predeclare:
- Experimental **tank/block** is spatial replication; repeated individuals/occasions are not independent replicates. Two main treatments are randomized within blocks.
- Compare treatment means with unit and exposure normalization if documented, account for block×year/taxon event clustering.
- Species-specific fish×vegetation contrasts; estimate interaction term and CIs using suitable negative-binomial/count GLMM or design-based permutation matching randomization. Do not claim a treatment sign without computing it from records.
- Combined life-history effect can be framed as species×fish×vegetation **statistical response heterogeneity**; do not conflate with true three-body interaction (fish×plant×frog species as environmental context).
- Positive ecological claims require stable sign across experimental blocks, nonzero interval and adequate randomization replicates; otherwise explicitly inconclusive.

## Boundaries
A past publication already studied this experiment. Any reanalysis is an **independent source-backed methodological reproduction**, not a new independent biological experiment or discovery within the user's NAAMP programme. Experimentally manipulating fish presence and macrophytes can identify their *total* effects on tested behavioral choice outcomes under design assumptions; it does not isolate insect-mediated paths, fitness, reproduction or direct frog-frog interactions. Use originally published conclusions as context and do not claim novelty until a new predeclared contrast with valid estimator is supported.

No change to frozen JAE RC6 manuscript, SI or main. All code+results on separate exploration branch.
