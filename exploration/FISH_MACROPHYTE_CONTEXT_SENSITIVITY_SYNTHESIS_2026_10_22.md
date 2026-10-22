# Fish-stratum macrophyte choice: independently repeated conditional permutation checks (exploratory)

**2026-10-22.** Separate branch descended from the exact source-pinned four-block Šigutová et al. 2021 Figshare 2×3 experiment. This is **after-response-readback sensitivity**, not a new independent study, preregistered discovery, or causal mechanism proof. JAE RC6/manuscript/SI/main untouched.

## Executed new check
Derived each **fish-present** macrophyte-minus-bare contrast at each original randomized physical block as:
`(no_fish plant-minus-bare) + (fish×plant difference-in-differences)`.

Conditional on the assigned fish-status tank set, enumerate all **(3!)^4=1,296 exact** plant-label permutations across four original blocks, with the treatment assignment held fixed over all repeated dates. Read the frozen aggregate block vectors and independently reproduce all four original fishless exact tests before interpreting any new fish-present test. In each stratum compute the 4-contrast BH statistic, explicitly **exploratory for the newly inspected fish-present stratum**. Also leave each block out in turn (3!=6 permutations in 3 blocks -> 216 configurations); leave-one-out P is **a sensitivity diagnostic, not a separate multiplicity-adjusted confirmation**.

| Original toad species | Fish stratum | Aquatic submerged+floating vs bare difference | Two-sided exact P | Four-comparison BH q | Consistent positive blocks |
|---|---|---:|---:|---:|---:|
| *Bufotes viridis* | no fish | **+45.86 pp** | 0.00617 | 0.02469 | 4/4 |
| *Bufotes viridis* | fish present | +1.19 pp | 0.88889 | 0.88889 | 1/4 |
| *Bufo bufo* | no fish | +12.40 pp | 0.23457 | 0.34568 | 3/4 |
| *Bufo bufo* | fish present | **+21.84 pp** | **0.00309** | **0.01235 exploratory** | **4/4** |

Fish-present *B. bufo* `aq−no` leave-one-out: **+17.24 to +24.49 pp** and conditional P **0.00926 to 0.01852** across all four omissions. Fishless *B. viridis* LOBO: **+34.17 to +56.98 pp**, P **0.01852–0.03704**. LOBO preserves the sign and relative magnitude but does not create new independent replicates.

## Interpretation and proof boundary
The notable pattern is that two toad taxa allocate male visits among the six offered pools differently, and their **within-fish-stratum** plant contrasts differ. The newly inspected fish-present *B. bufo* plant preference is a **post-hoc potentially positive experimental contrast**, worthy of predeclared external replication. The existing original fish×plant **difference-in-differences is NOT supported after four-test BH correction**, and separate significance within one stratum but not another **is not evidence of interaction**. No plant modification of frog-to-frog competition, no plant→fish/insect→frog mediation, no true simultaneous ≥3-biotaxon causal interaction has been demonstrated.

Choice shares are fractions of visits across the **six simultaneously available tank options**, not survival, fecundity or NAAMP adult frog-call probability. Independent randomized units are only **four physical blocks**, not 22–23 visit dates or the individual toads. No claim of novelty relative to the published experiment.

Code: `exploration/run_fish_macrophyte_context_sensitivity_v0_1.py`. Numerical receipt: `exploration/FISH_MACROPHYTE_CONTEXT_SENSITIVITY_RESULT_V0_1.json`. Frozen source: `exploration/FISH_MACROPHYTE_FACTORIAL_BLOCK_RESULT_V0_1.json`, experimental study [doi:10.1038/s41598-021-98632-2](https://doi.org/10.1038/s41598-021-98632-2).
