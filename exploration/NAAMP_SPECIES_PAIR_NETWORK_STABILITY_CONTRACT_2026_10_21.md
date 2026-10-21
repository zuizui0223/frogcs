# Post-result robustness of the vegetation-conditioned frog acoustic pair network

This diagnostic was specified AFTER the original network output became visible and is **post-hoc sensitivity, NOT independent confirmation**. The primary result is frozen at workflow 39520831924: 112 eligible co-calling taxon pairs, 21 BH q<0.05 (14 residual sharing and 7 residual spatial segregation).

Input: the frozen per-run `all_same_route_acoustic_pair_nulls.csv` and per-pair `all_species_pairs_BH_ledger.csv` from run 39520831924. Do NOT refit/retune species-specific plant effects or redo the weighted Curveball null to select favorable pairs.

Check **every** original eligible pair, with deterministic:
1. **Time**: source NAAMP `SurveyYear<=2008` versus `SurveyYear>=2009`; require at least 12 survey matrices from 7 routes in EACH period for sign comparison, otherwise label insufficient. Report means and independent-route cluster CIs for each half and total.
2. **Geographic route fold**: same original SHA256 A/B fold; require >=12 matrices in >=7 routes in each, otherwise insufficient. Report signs, mean and route-clustered intervals.
3. **State leverage**: leave one State out for each original BH edge, provided >=30 remaining matrices and >=15 remaining routes. Count how many omit-one-state estimates have same sign; do not select exclusions for stronger outcome.
4. **Broad classification**: call a detected pair `direction_stable` only if both temporal and both geographic halves are sample-eligible and share the primary residual sign. Call `interval_stable` only if every half has a 95% route-clustered CI excluding zero in the primary residual direction; do not expect this to hold with limited data. If insufficient, do not relabel positive/negative pair as absent.
5. FDR list remains the **original all-eligible-pairs BH q**, not newly selected holdout p.

Treat `Hyla chrysoscelis` vs `Hyla versicolor` and any species-complex-labelled pairs cautiously due to acoustic taxonomic identification and sibling/complex coding, even if such an edge is stable. No pair result establishes biological competition, facilitation or attraction.

Report all original 112 eligible pair units including those without BH significance, and a compact primary-network supported edge stability summary. Do not change RC6 manuscript, SI or submission evidence.
