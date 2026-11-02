# Frozen new-seed source validation: vegetation reallocates relative F-predation hazard? (2026-11-02)

**Design frozen before examining any new simulation outcomes.** Draft follow-up to PR #160. Original `main` and all original data, positive/negative results and source kernel untouched. Biological claim is hypothetical and *model-native*, not an empirically fitted predator effect.

## Question and exact null

Historical exploratory R2 found: under artificial attack=0.5, rho=0.75, `support_DF=1` (wetland vegetation facilitates odonate→frog consumption) with `cover_SF=1` (vegetation shelters frogs against salamander→frog predation) was associated with four-sign success in **106/675** source proposals, versus **12/424** with both OFF, after **rate-dependent** historical selection. These were comparisons of **different model IDs**, so model composition and catalog multiplicity could create the difference.

**Independent new-seed question:** In previously unsimulated legal canonical model backgrounds, when *exactly the same model's other 11 features, original context, biological rate vector and 80-year seasonal kernel* are held fixed, does switching both plant functions ON improve the generation of OS−/OV−/SV+/OSV+ relative to switching both OFF? Does their combination exceed the sum of each feature's isolated effect (interaction/synergy), and are opposite predator-specific per-larva F hazards actually shifted? No readjustment of parameters or selection on new success.

The unit is a **base canonical model/background plus independently drawn hypothetical nuisance rates**, not an accepted draw. All three original developmental contexts are evaluated for each base, so stage-specific comparisons are *within-background repeated measures*, not three independent ecological sites.

## Precommitted new seed, source, rate regime, and legal counterfactuals

- **Immutable original main:** `5e2f0a87c639df373fa2700b29403d2ab417a1cc`. Unchanged original `final_mechanism_common.catalog`, `evaluate`, `CONTEXTS`, and `abc_pom_main3600.corner_contrasts/accepted_signs` with epsilon `1e-6`; 120-day season nested in genuine **80 years**, last **20-year** source mean, `dt=.5`. Original 8-factorial vertices V∈{0,1}, S/D source each∈{0.25,2}.
- **Independent fresh sampling RNG:** `20261123` (**different** from old structure-rate draw seed 20261101 and the 96-accepted-source sample 20261102); choose **256 DISTINCT** legal canonical *base* structures sampled uniformly without replacement from original catalog rows with `cover_SF=0`, `support_DF=0`, and `behavior != risk_refuge` (the latter would be structurally illegal if cover_SF is OFF).
- **Original paired biology nuisance:** All base models have fixed `attack=0.5`, `rho=0.75`; `conversion∈{2,4,8}`, `strength∈{0.5,1.0}`, `refuge_order∈{S,equal,D}`, and original size gate `None / 0.5`, drawn once per base under independent uniform original rates. No field calibration. Preserve rates and all other canonical structure flags through **3 original developmental contexts × 4 plant feature combinations**.
- **Four exact legal arms:** `00`: neither F-from-S refuge nor vegetation-assisted D→F predation; `10`: frog refuge only; `01`: dragonfly feeding support only; `11`: both. All quartet variants must be *separately present in the original 3,600 canonical catalog* with unchanged other features (including original `litter`, `cover_DF`, `edge_SD`, `edge_DS`, `cover_DS`, `support_DS`, `survival`, `timing`, `reverse`, `behavior`). Requiring existing IDs, not inventing new processes, fails closed on any invalid quartet.
- **Size of genuine new experiment:** 256 distinct original base structures × 3 developmental contexts × 4 treatments = **3,072 new 80-year proposals** × eight original factorial corners = **24,576 actual simulated V×S×D source responses**; partition into 8 shards by original base-source ID (each 32 sources×3×4=384 proposals, with all matching arms in same shard). These are model simulations, **not 24,576 wild observations**. Never use the old 794 accepted proposal IDs as input model selection.
- New models may share parameter values with prior experiments (a finite discrete prior) but the **draw identities, model background sampling and paired combinations are independent**. Avoid claiming held-out wild ecological validation.

## Primary estimands and predeclared scientific decision rules

For every base M×θ and three contexts, calculate `log(F_B)` OS/OV/SV/OSV original four signs and zero/one acceptance for all four plant arms.

**Primary selection-independent 2×2 contrasts (per context and averaged within source across contexts):**
1. `D_11_00 = accepted(11) - accepted(00)`, mean and **95% source-background bootstrap CI**. Model-native positive regeneration supported if interval strictly positive; not an observed field effect.
2. `D_interaction = accepted(11) - accepted(10) - accepted(01) + accepted(00)`, same source-resampled CI. **Positive interaction/synergy** asserted *only if lower 95% bootstrap bound >0*, not merely a greater 11 success fraction. Test main effects separately: `accepted(10)-accepted(00)`, `accepted(01)-accepted(00)`.
3. Same F and S **minimum source survival ≥5%** as a pre-specified *auxiliary sensitivity* for each arm. Report **joint four-sign-and-floor success over all initial source proposals**, not a post-treatment selected subset, and also expose arm-specific floor frequencies.
4. Absolute `mean_log_F_B` and `mean_F_B` ON/OFF responses and continuously estimated four interaction contrasts, not just sign success. Preserve sign reversals and zero changes.

**Predator switch mechanistic gate (separate from four-sign acceptance):**
1. At **V=1, S_source=D_source=2** (the exact original corner 7), from the original 80-year seasonal kernel calculate last20-year mean per-larva integrated `audit_H_SF` and `audit_H_DF`. In same-background paired comparisons, `cover_SF` should reduce model S→F hazard and `support_DF` should increase D→F hazard *if a realized rate-level shift occurs*. Report change of `H_DF/(H_SF+H_DF)` share across 00→10→01→11; it is a **hazard share**, not fraction of actual prey deaths or predator replacement in the natural wetland.
2. When V=0, both plant paths are mathematically absent: exact **negative control** requires all original source outcome/hazards identical across the four variants at all four S/D source corners and across each stage. Any V=0 discrepancy is a **failed experiment**, not new biology.
3. If the S or D active predator stage has zero overlap in a developmental context, record biologically zero hazards, do not replace by a positive value; no claim that switch works in all stages.
4. A direct hazard shift is partially built into the original **mechanistic assumptions**; the incremental finding is whether it generates nontrivial *response geometry, population-level F output and interactions* under independent new M×θ backgrounds. A successful hazard direction by itself does NOT validate the model's mechanisms with field data.

**Reporting:** Source-background resampling 10,000 replicates, fixed bootstrap seed `20261124`; 256 backgrounds are the resampling units, the three developmental contexts/4 arms stay paired. Retain complete original 256×3×4 output, model IDs, param tuple, counterfactual differences, hazards, survival and all zero/nonpositive results; no favorable-arm choice after outcome inspection.

## Stronger alternative and inferential boundary

The historic **15.7% vs 2.8%** is between-structure conditional success on a post hoc artificial attack/rho regime. This experiment tests **within-structure** plant-counterfactual effects using a fresh seeded base sample. Because the base sample conditions on `00`-legal canonical backgrounds, its reference structural distribution differs from the old 2,245-proposal mixture. **Do not require or expect a literal 5.5× replication**. A contrast may disappear with matched controls, in which case the earlier conditional structural association is retained *but the switched-mechanism generalization fails*.

No measured local S/D density, larval predator mortality, in-pond submerged refuge or larval→adult calling observation link is added by this numerical test. This independent numerical experiment cannot establish that vegetation *actually shifts predator dominance* at NAAMP ponds; at most it confirms a reproducible structural model mechanism under the fixed exploratory rate regime. PR #160's real-data environmental-null G1 and source-to-field adequacy failures remain visible.

## CI gates

1. Original canonical catalog and four-feature quartet identity; original 80-year run-subset replay on a small full quartet.
2. Independently seeded 256 backgrounds; all three original developmental contexts; all four arms; exactly 3,072 proper source result rows and 24,576 model source corners.
3. Exact V=0 identity across arms and source hazard/survival and original four-sign eps consistency.
4. Independent same-source 2×2 acceptance, continuous coefficients, survival and predator hazard audit with source-unit bootstrap; no missing original denominators.
5. Source files, full audit receipt, both positive and negative results, no merge/field inference.

Author a new stacked Draft PR on PR #160; do not edit the original main, historical positive source results or submit a paper.
