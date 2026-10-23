# Frozen post-readback ecological source audit: taxonomic contributions to positive PEM seasonal acoustic complementarity

**Created 2026-10-23 AFTER the original two-round complementarity analysis passed its predeclared route/State/FDR gates.** Its real fixed result is: 1,115 physical route×year communities across 274 physical routes and 20 States, 2,475 source round pairs, zero reselected taxon labels; PEM−nonPEM CI>=1 absolute temporal bonus +0.127796 taxon units per matched site group (95% route CI +0.076801 to +0.178792; 4-test BH q=1.405e-6); strong +0.128263. This follow-up is purely **decomposition and fragility diagnosis after seeing these values**; it cannot be represented as independent hypothesis testing, significance discovery or phenological species interactions.

## Questions

1. How many monitored frog taxon labels have **positive or negative arithmetic contributions** to the verified `PEM−otherwetland` absolute two-round bonus?
2. Does one dominant taxon label account for most of the new absolute PEM complementarity difference, or is it broadly distributed across source taxa and genus prefixes?
3. When matched within the SAME route-year and same pair of monitored rounds, is the **proportional** temporal bonus `B/G_two` larger at PEM mapped stations, or does the observed absolute increase mainly co-vary with the already larger total PEM taxon pool?
4. Does the bonus surplus come mainly from acoustic labels found only in the later observation round versus ones found only in the earlier observation round? These are detection categories; **do not** say biological arrivals or extinctions.

## Locked source, full original cohort, and source unit

Re-open the identical 2001–2015 original NAAMP+NWI crosswalk through the already verified `source()` + `build_rounds()` functions in `exploration/run_naamp_vegetation_withinyear_round_hierarchy_v0_1.py`. No changes to 7,848 normalized NAAMP source nights, 6,236 complete NWI source nights, 5,147 original physical NWI SiteIDs, same 2,869 eligible survey visits /1,115 physical route×years /274 physical routes/20 States. Use original recorded calling taxon labels, including complexes, in all 2,475 pairs of rounds. Exact same m>=2 physical site subset rarefaction shared across rounds, within NWI-mapped PEM+ vs other mapped wetland sites only. Require source 1,115/2,475/274/20 to fail closed if drifted. Never select a taxon because its estimate has a favorable sign.

## Exact taxon contribution (NO new taxon-level P tests)

For taxon label s and habitat h, define:
`b_s,h = 0.5[P0_early(s,h)+P0_late(s,h)]−P0_union(s,h)`,
where `P0_x=C(n−k_x,m)/C(n,m)` and union k uses **same physical site across the two rounds**. Then `Σ_s b_s,h = B_h`. Difference `d_s=b_s,PEM−b_s,otherwetland` can be positive or negative.

Compute every `d_s` per source pair of rounds; sum/average FIRST within route×year (1/3/6 round combos), THEN physical route across years, THEN equal-weight physical route. **Absent taxa contribute zero in each group** (never divide only by route-years where that taxon is active). Hard invariant `sum_s d_s = +0.12779625975522307` (CI>=1) / `+0.12826328471249396` (CI>=2) to 1e-10. Report top 10 positive and negative, positive vs negative signed counts, total positive and negative components, fraction of positive sum due to largest one and five, and arithmetic net after subtracting largest taxon. Taxon complexes retain source labels, and grouping genus prefixes is only an exploratory bookkeeping summary, not a phylogeny. No BH, p values, independent taxon tests or new primary global significance.

## Proportional bonus, descriptive only

For each source exact route-year-roundpair and each habitat, if `G_two>0` compute `B/G_two`; if zero, mark undefined, not 0. Calculate **within matched paired round-pair differences** `(B/G_two)_PEM − (B/G_two)_other` ONLY when both are defined. Average these valid differences within route-year and then route; retain count/fraction of pair comparisons excluded (zeros). Report route-equal and State-equal descriptive means and sign distribution, **no inferential significance** because the proportional question was chosen after observing the original absolute result. Do not claim that the absolute increase implies a stronger proportional rate of ecological turnover.

## Temporal direction and source consistency

For each habitat separately sum taxon `new_later_s = P0_earlier−P0_union` and `early_only_s=P0_later−P0_union`; exact identities `B=(new_later+early_only)/2` and `G_two=G_mean_single+B`. Compare signed PEM minus other wetland arithmetic components, but these are detection windows, not frog colonization/extinction or species replacement over ecological generations. If the main numeric result cannot be reconstructed to 1e−10, do not publish a biological interpretation.

**No prediction, outside paper reanalysis, geographic radius tuning or plant/animal causal interpretation.** The frozen original JAE RC6 manuscript/SI/main and original prior positive/nonsupported macro results are untouched.
