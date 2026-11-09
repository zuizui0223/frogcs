# Food webs that reproduce frog–predator association signs need not benefit frogs

**C (observation) → D (mechanism) author-review candidate · 9 November 2026 · not submitted or coauthor-approved**

## Abstract

Continental frog choruses index adult breeding-associated activity, not directly observed tadpole hatching or survival. We asked whether food webs reproducing analogous frog–predator association patterns also benefit frogs. At 4,248 North American listening sites, strong frog calling was context-dependent on odonate, caudate and landscape-vegetation suitability. Among 20,000 synthetic food-web proposals, 794 (3.97%) generated four idealized association directions, representing 647 canonical structures versus 712 expected under a rate/context-conditioned null. Two disjoint samples of 256 model structures crossed with 27 hypothetical rate combinations showed that two vegetation functions increased pattern compatibility by 2.71 and 2.75 percentage points while reducing mean simulated frog log-cohort abundance by 0.040 and 0.041. Independently varying salamander arrival and aquatic-stage duration reversed vegetation’s demographic effect: early arrival and prolonged aquatic exposure benefited frogs. Thus, generating an interaction-like spatial signature need not yield demographic benefit, which depends on predator developmental context.



**Keywords:** amphibian calling; caudate guild; dragonfly larvae; conditional associations; ontogeny; vegetation refuge; stage-structured food webs; finite-population persistence

## Introduction

Broad geographical associations can suggest biotic interactions, but also reflect shared environments and observation processes (Blanchet, Cazelles & Gravel, 2020). Even when a food web reproduces the direction of a spatial association, the consequences for the focal population may be different. We therefore ask whether mechanisms generating frog–predator association signs necessarily benefit frogs, and whether developmental conditions can reverse the effects of aquatic vegetation.

Calling at a monitored site indicates **adult breeding-associated activity and an opportunity for offspring production**, not confirmed egg laying, tadpole hatching, juvenile survival or the number of recruits. Independently collected INBO and USGS datasets relate recorded calls to subsequent or concurrent larval detections, but do not establish reliable cross-year recruitment prediction (Supplementary Methods S20 and S22). These sources justify asking about aquatic stages; they do **not** equate the acoustic response to tadpole birth. Predation on an offspring cohort later in a breeding season also cannot cause that cohort’s parents to have called earlier in the same season. A demographic feedback from previous offspring to future calling would require additional multiyear observations.

Aquatic vegetation can shelter frog larvae from predators while also supporting odonate foraging (Hossie & Murray, 2010; Mocq et al., 2021), and arrival priority and predator developmental stages can change interaction effects (Alford & Wilbur, 1985; Rasmussen et al., 2014). We first characterize the continental association between frog calling, odonate suitability, caudate suitability and landscape vegetation. We then use source-audited stage-structured simulations to manipulate frog refuges, vegetation-supported odonate attacks and salamander arrival/aquatic duration independently. Our central question is **whether a vegetation configuration that generates an observed-like association pattern also benefits simulated frog cohorts**, not whether we have identified an actual natural pond food web.


## Materials and methods




### C. Continental acoustic associations and geographic controls

We used NAAMP observations from **4,248 repeated listening sites**, **63,180 completed visits in 2001–2015** and 432 routes (Foreman et al., 2017). The response was the fraction of visits with strong frog calling (36,554 strong events), not tadpole density. Environmental suitability for an odonate guild (**O**) and pond-breeding caudates (**S**) was modelled from 28 eligible frog, caudate and odonate taxa, with **uniform** and **target-group** SDM backgrounds analyzed separately. Landscape flooded vegetation (**V**) was presence within 3 km, not actual submerged stems at the listening pond (Tuanmu & Jetz, 2014).

We retained the original geographical O×S, O×V, S×V and O×S×V rank interactions as descriptive coefficients and compared odonate–calling Spearman correlations between high- and low-caudate suitability tertiles using route-cluster bootstrap intervals. Within-route and geographically held-out comparisons used 56 two-degree geographic blocks and five folds, with survey, climate, land cover and location covariates, including nonlinear shared-environment alternatives. Pre-fixed acoustic-strength definitions and the original two-part, source-constrained and background-sensitivity tests remain in Supplementary Methods S2–S3 and S16–S19. Suitability does not measure predator density and no field mechanistic posterior was fitted.

### D. Source-defined stage-structured food webs and vegetation counterfactuals



The original mechanistic space comprised **3,600 canonical stage-structured food-web models** encoding direct and indirect trophic links, vegetation functions, developmental timing and feeding responses. A genuine seasonal predator–prey model was embedded in an **80-year delayed-recruitment model**. For each model/parameter proposal, we evaluated eight source conditions formed by two vegetation levels and low/high caudate and odonate supply. The response was the mean aquatic frog cohort over the final 20 years. The original model-native four-sign criterion required **OS−, OV−, SV+ and OSV+** on the log aquatic frog response, using the frozen \(10^{-6}\) sign threshold. The rejection ABC-style screen targets idealized model signs, **not a field-conditioned posterior for NAAMP calls**.

We reaggregated all **20,000 originally simulated structure–development–rate proposals**, reporting proposal denominators and signs in the complete 3×3×3 grid of synthetic attack coefficient (0.5, 1.5, 3), local recruitment fraction (0.25, 0.50, 0.75) and maturation conversion (2, 4, 8). An artificial 5% survival floor was retained. G12 reweighted all proposals under nine illustrative synthetic rate priors and varied sign thresholds and response scale (Supplementary Methods S14). The historically selected low-attack/high-recruitment region is exploratory, not field-calibrated.

To test the structural hypothesis without comparing different models that contain different hidden features, we next **froze a new sampling seed before inspecting any new result** and sampled **256 distinct legal original-catalogue backgrounds** without replacement. These backgrounds were chosen to permit the two specific vegetation features to be toggled while leaving all other model flags intact. Original hypothetical rates were held constant within each quartet, with attack=0.5 and local recruitment fraction=0.75 retained from the historical exploratory regime. Two features were crossed: **frog refuge from salamander attack** (\`cover_SF\`) and **vegetation-supported odonate attack on frogs** (\`support_DF\`). The four legal original-catalogue states were 00 (neither), 10 (frog refuge only), 01 (odonate feeding support only) and 11 (both). All three original developmental contexts were evaluated, yielding **3,072 genuine 80-year model proposals** and 24,576 vegetation×caudate×odonate source responses.

The prespecified contrasts were both-versus-neither compatibility (\(p_{11}-p_{00}\)) and nonadditive factorial compatibility (\(p_{11}-p_{10}-p_{01}+p_{00}\)). We used 10,000 bootstrap draws at the **256-background** unit; developmental contexts and four intervention arms remained paired. The auxiliary 5% minimum-survival result was reported alongside, not used to select favorable source backgrounds.

### G8–G11. Same-rate grid and disjoint structural replication

We extended the original paired vegetation-function factorial without retuning the biological kernel or selecting successful model structures. All 256 previously sampled legal backgrounds, three original developmental contexts and all four vegetation arms (00/10/01/11) were crossed with **27 fixed hypothetical rate cells**: attack coefficients 0.5/1.5/3, local recruitment fractions 0.25/0.50/0.75 and maturation conversion factors 2/4/8. This yielded **82,944 genuine 80-year model scenarios and 663,552 environmental vertices**. We compared paired four-sign acceptance, artificial 5%-survival compatibility and log frog cohorts across all sources. Ten thousand matched-background resamples yielded model-conditional 95% intervals. G8 and its disjoint G11 replication, both independently source-audited across 64 shards, are documented in Supplementary Methods S10 and S13.

### R3. Directly auditable model predator hazards and frog cohorts

For the same 256 backgrounds, we retained the original seasonal integrated per-frog hazards from salamander attack (**S→F**) and odonate attack (**D→F**) under vegetation-present/high-S/high-D source conditions. We calculated the model odonate share separately within each source as \(H_{DF}/(H_{SF}+H_{DF})\), conditional on the denominator being defined, then summarized source-level shares. Importantly, the **mean of source-specific hazard shares is not the ratio of the two separately averaged hazards**. These hazards measure modelled per-larva attack pressure, not numbers of real tadpoles eaten. All vegetation-function arms had to produce identical biological source outcomes when vegetation was absent, a preregistered numerical negative control.

We also compared the same matched model backgrounds for mean aquatic frog log cohorts and the conditional four-sign success indicator. The two outcomes use different scales: a higher compatibility rate need not correspond to a larger frog population.

### P1. Separating arrival order from aquatic-stage duration

In the original three-context experiment, the early-salamander setting altered both salamander arrival and its aquatic duration. We therefore froze a **new 2×2 developmental intervention** before calculating outcomes, retaining the same original 256 legal model backgrounds, attack and recruitment values, and all four vegetation treatments. Frog arrival (day 20), frog aquatic duration (45 days), odonate arrival (day 20) and odonate aquatic duration (60 days) were held constant. Salamander arrival was varied independently (early day 0 versus late day 40) of salamander aquatic duration (short 40 versus long 60 days). This generated **4,096 genuine 80-year model scenarios** and 32,768 original vegetation×salamander×odonate source responses. Late/short and early/long reproduced the prior original contexts 1 and 2 exactly across 2,048 source scenarios and 16,384 original eight-corner responses.

Within each background, we computed the both-functions-minus-neither difference in mean log aquatic frog abundance and four-sign compatibility under all four developmental settings. The pure arrival and pure duration moderators were averages across the opposite factor; their interaction was the usual difference-in-differences. All original 256 backgrounds remained in the analysis; **10,000 source-background bootstrap resamples** retained all timing and treatment comparisons paired. This separates two *model inputs*, not actual pond breeding chronology. A separate response-blind GBIF egg-stage eligibility audit did not meet the preregistered taxon-coverage threshold for a field breeding-lead analysis, which was therefore not performed.

After completing P1, we decomposed its net two-function effect into refuge-only, feeding-support-only and nonadditive components. All 256 backgrounds and four timings were retained, with shared source-bootstrap indices. This post-hoc explanation also counted background-level sign reversals (Supplementary Methods S8b).

Long-run stochastic R4 analyses and the R5 virtual-observer identifiability sensitivity remain entirely in Supplementary Methods S6 and S21, respectively; original observation diagnostics G1–G7 and G14–G17b are retained there without converting failure to positive field validation.

## Results




### C. The continental acoustic association depends on caudates and vegetation

In the original whole-region rank-interaction comparisons, odonate suitability was negatively associated with strong frog calling in the presence of higher caudate suitability (**O×S = −0.166**, 95% interval −0.229 to −0.108, under uniform background; **−0.086**, −0.151 to −0.023, under target-group). Vegetation also moderated the odonate association (**O×V = −0.087**, −0.124 to −0.048, uniform; **−0.064**, −0.115 to −0.014, target-group). These are *rank-model associations*, not directly observed predation effects.

The original high-minus-low caudate-suitability Spearman contrast was **−0.385** (route-bootstrap −0.509 to −0.240) under uniform and **−0.179** (−0.328 to −0.029) under target-group; within-route contrasts were −0.122 (−0.199 to −0.034) and −0.072 (−0.183 to +0.023). Incremental O×S terms did not improve geographically held-out strong-calling prediction over flexible shared-environment alternatives in either background. The subsequent G5/G7/G14/G15 model-shaped field predictors also failed their prespecified dual-background discrimination gates, and the G17 numerical replay failed. C therefore establishes a contextual **acoustic association that motivates** stage-structured models, not evidence that natural predator pathways were identified.

### D1. Food-web structure and vegetation functions determine which signatures can be generated



Of the 20,000 original 80-year model proposals, **794 (3.97%)** generated all four idealized interaction directions. Compatibility was higher at attack=0.5 (**421/6,555; 6.42%**) than attack=3 (**146/6,696; 2.18%**) and at recruitment=0.75 (**424/6,689; 6.34%**) than 0.25 (**106/6,607; 1.60%**). The weak-attack/high-recruitment region yielded **179/2,245 (7.97%)** versus **11/2,228 (0.49%)** for strong attack/low recruitment; the highest individual rate cell had *intermediate* attack (**78/710; 10.99%**). An artificial 5% survival condition reduced accepted proposals from 794 to **426**, with **none of 146** four-sign successes under attack=3 passing it. The 794 accepted proposals spanned **647 canonical IDs** (G13 rate/context-conditioned null: **712**, p=0.0002); G12 rate priors shifted acceptance to **1.09–6.85%**, while log-sign epsilon=0.01 retained **267**.

Within the historical low-attack/high-recruitment region, source models combining \`cover_SF\` and \`support_DF\` generated the four signs in **106/675 (15.70%)** proposals, compared with **12/424 (2.83%)** when both flags were absent. Across the full prior, G13 found **support_DF=1** enriched by **17.47 points** after rate/context adjustment (familywise p=0.0002); these cross-model associations still cannot identify a wild causal mechanism.

The prospective 256-background same-model intervention resolved that ambiguity at the model level. Across 256 structures and three original developmental contexts, compatibility was **27/768 (3.52%)** with neither function, **44/768 (5.73%)** with only frog shelter, **60/768 (7.81%)** with only odonate feeding support, and **108/768 (14.06%)** with both. The matched both-minus-neither increase was **+10.55 percentage points** (source-background Monte Carlo interval +7.68 to +13.67), while the **nonadditive factorial contrast was +4.04 points** (+0.91 to +7.29). These contrasts also remained positive under the source's artificial 5% survival sensitivity. However, the nonadditive effect differed by developmental setting: it was +7.42 and +7.81 points in contexts 0 and 1, but **−3.13 points** in the early-salamander context 2, where the negative interval did not remain distinct from zero after adding the 5% survival gate. Vegetation-function synergy was therefore not universal across source life histories.

### D2. Pattern-generating vegetation functions redistribute model hazards without a population benefit



The original model's seasonal hazards responded in opposite directions to the two vegetation manipulations. Under the vegetation-present/high-S/high-D source corner, mean S→F hazard declined from **0.624 to 0.376** when both functions were present, while mean D→F hazard rose from **0.488 to 0.945**. The *mean of separately calculated source-level* D→F hazard shares increased from **59.7% to 73.9%** (paired source-background difference +14.22 percentage points, interval +12.90 to +15.61). At vegetation=0, the four treatments gave identical original model states and hazards, satisfying the numerical negative control.

Despite generating the four-sign pattern more frequently, the combined plant functions **reduced mean log aquatic frog cohorts** relative to neither function by **−0.0841** (source-background interval −0.1128 to −0.0557). Frog refuge alone increased that mean, while odonate feeding support alone reduced it. The combined net effect was negative in developmental contexts 0 and 1 but positive in context 2. A vegetation function that improves the likelihood of an interaction *signature* thus need not benefit the focal frog cohort. The hazard-direction effect is partly built into the model's mechanism definitions; its joint consequences for interaction geometry and frog abundance are the tested simulation outcomes.

### D3. Rate and structure replication confirms a pattern–population mismatch



The complete 27-rate paired experiment increased four-sign compatibility from **2.252%** with both vegetation functions OFF to **4.958%** with both ON: a mean increase of **+2.705 percentage points** (source-bootstrap interval **+2.021 to +3.410**), equally weighted over all rates and three developmental contexts. The increase remained **+2.619 points** (+2.054 to +3.226) when compatibility also required the artificial 5% survival floor. Nevertheless, the same interventions **reduced mean log aquatic frog cohorts by −0.04030** (−0.04918 to −0.03109). The pooled factorial nonadditivity was **−0.709 points** (−1.461 to +0.010), showing that the positive interaction at the historically selected rate regime was not general across rates.

Across rates, compatibility improved in **15/27** cells, declined in seven and was unchanged in five; nine and three pointwise intervals were respectively positive and negative (unadjusted). All nine weak-attack cells improved (mean **+7.827 points**), versus +0.521 at attack 1.5 and −0.231 at attack 3. Mean frog-cohort effects were negative in **all 27 cells** when contexts were pooled.

The developmental context altered that conclusion for abundance. Pooling equally across all 27 rate cells, the original contexts 0 and 1 had mean log frog-cohort effects of **−0.07227** (−0.08327 to −0.06103) and **−0.07384** (−0.08525 to −0.06217); original context 2 instead had **+0.02521** (+0.01507 to +0.03543). Context 2 was positive in 20/27 cells; these original contexts jointly altered developmental features. P1 independently separated arrival and duration at its fixed rate (Supplementary Table S10a; Figure S4).

G9 counted **571/782 (73.0%)** newly sign-generating cases with lower frog cohorts; G10 found no clear rate×context-adjusted excess loss (**−4.93 points [−11.28,+0.83]**; S11–S12). In G11, **256 previously unused legal structures**, crossed with the same 27 rates, reproduced both pre-fixed directions: compatibility **+2.754 points [2.083,3.434]**, mean log frog cohorts **−0.04125 [−0.05018,−0.03202]**. Among **835** new-sign cases, **612 (73.3%)** lost cohorts; developmental context2 again showed a positive mean abundance effect (S13).

### D4. Salamander arrival and aquatic duration reverse the demographic vegetation effect



The controlled developmental factorial resolved the previously confounded early-salamander result. Relative to neither vegetation function, both functions changed mean log aquatic frog abundance by **−0.1864** (source-bootstrap 95% interval −0.2266 to −0.1464) under late arrival/short duration, **−0.1860** (−0.2271 to −0.1463) under late arrival/long duration, **+0.0021** (−0.0264 to +0.0317) under early arrival/short duration and **+0.1163** (+0.0787 to +0.1560) under early arrival/long duration. Thus earlier salamander arrival alone largely eliminated the negative vegetation effect, but **a reliably positive abundance effect required both early arrival and prolonged aquatic exposure** within this model. Across the two duration levels, early versus late arrival increased the vegetation effect on mean log F by **+0.2454** (+0.1967 to +0.2976). Longer versus shorter duration increased it by **+0.0574** (+0.0438 to +0.0714), with a positive arrival×duration interaction **+0.1138** (+0.0880 to +0.1409).

Yet vegetation's increase in four-sign compatibility was greatest when the effect on frog abundance was negative. Both-functions-minus-neither compatibility increments were **+13.28, +10.94, +9.38 and +2.34 percentage points** across late/short, late/long, early/short and early/long settings, respectively. Advancing arrival reduced this compatibility advantage by an average **6.25 points** (−10.74 to −1.95), and lengthening duration reduced it by **4.69 points** (−7.23 to −2.15). The model condition that most strongly benefited frog abundance therefore provided the **smallest incremental gain in producing the idealized signature**. This further separates compatibility from demographic benefit, while leaving actual natural breeding priority unverified.

The post-hoc decomposition attributed the late/short-to-early/long shift to increased refuge benefits (**+0.1719**, interval +0.1422 to +0.2042) and reduced feeding-support costs (**+0.1476**, +0.1157 to +0.1829), partly offset by nonadditivity (**−0.0167**, −0.0248 to −0.0093). Together these produced a **+0.3028** shift in the net vegetation effect. Of 256 backgrounds, **124 changed from negative to positive**, none changed in reverse, and 73 remained negative. Thus the mean reversal represents a broad, heterogeneous response within the sampled model family (Supplementary Methods S8b).

## Discussion

### Geographical association signs do not measure frog benefit

The continental result identifies context-dependent adult acoustic associations, not the actual predation network. The independent biological premises establish that calling and larval detection can be linked within breeding seasons, but do not calibrate adult calling to larval survival. In source-defined food webs, the same vegetation functions can generate these idealized association directions more frequently while decreasing simulated frog cohorts. The structural-selection null (G13) confirms that source-model structure matters after accounting for hypothetical rates and developmental context, but 647 distinct accepted networks remain, and acceptance is not a field posterior. G8/G11 reproduce the average mismatch in disjoint structural samples across 27 rates, whereas G10 shows that the high descriptive fraction of losses in newly sign-generating cases is not an excess after rate/context standardization. The general inference is the **non-equivalence** of pattern reproduction and focal demographic benefit, not that pattern-generating food webs intrinsically cause greater losses.

### Predator development changes the value of vegetation

Within the stipulated model family, the beneficial refuge function and the cost of vegetation-supported odonate attacks respond differently to salamander arrival and aquatic duration. Early arrival alone alleviated a negative vegetation effect; a long aquatic period after early arrival produced positive mean frog-cohort effects, even as the gain in pattern compatibility became smallest. Hence the same aquatic structure can have different demographic consequences under different predator developmental contexts. Such dependence could motivate future studies of shifts in breeding phenology, but **this analysis did not test climate warming, actual phenological shifts, or natural predator timing**. The pathway signs follow the model's encoded interactions; the net counterfactual effects, their rate sensitivity and their reproduction across source structures are the computed results.

### Why breeding-associated calls motivate—but cannot establish—a larval mechanism

Calls indicate adult breeding-associated activity but cannot verify that eggs were deposited or tadpoles hatched at a listening site. The independent INBO and USGS stage observations provide limited supporting associations without calibrated larval survival or forward-year recruitment prediction (S20, S22). Likewise, odonate/caudate SDM suitability and 3-km vegetation are not measured local predator densities, arrival times or submerged refuges. G1–G7 and G14–G17b did not identify the natural trophic pathway, and G17’s numerical replay failed. R5 illustrates how hypothetical proxy mismatch can obscure a known simulated source; it does not explain the original field prediction failures (S21). These gaps justify controlled counterfactual simulations of vegetation pathways and predator development **as a way to investigate possible population consequences**, rather than interpreting the observed acoustic pattern as actual tadpole birth or predator-mediated survival. Field identification would require local egg and larval cohorts, tadpole survival, predator densities and developmental stages, vegetation structure and observed predation or enclosure responses.


## Conclusion

**Food webs that reproduce frog–predator association signs need not benefit frogs.** The original vegetation functions increased four-sign compatibility but decreased mean simulated frog-cohort abundance across independent structural samples and 27 hypothetical rate conditions. Independently manipulating salamander arrival and aquatic duration identified conditions reversing the vegetation effect. The continental call data motivate the source-model pattern directions but do not measure tadpole birth or natural predation. The biological conclusion is a contrast between **pattern generation and demographic benefit**, with the sign of vegetation’s effect depending on predator developmental context.


## Figure captions and submission layout

**Figure 1 | Continental frog-calling associations across caudate and landscape-vegetation contexts (C).** Original 4,248-site NAAMP strong-calling correlations and signed O×S/O×V rank-model coefficients under uniform and target-group SDM backgrounds; 56 geographical blocks. Frog calling is adult breeding-associated activity; no panel claims observed egg deposition, tadpole hatching or local predator attack. **Reuse original audited Figure1_Observed_ThirdGuild_AcousticAssociation.png without modification.**

**Figure 2 | Vegetation functions redistribute model predation hazards and change pattern compatibility (D).** Source-verified original 256-background 2×2 plant-function manipulations and mean of source-specific odonate hazard shares. Feeding pathways are defined by the model; net outcomes are model-derived counterfactuals. **Reuse original audited Figure2_InteractionSignature_VsFrogAbundance.png without modification.**

**Figure 3 | Pattern–demography mismatch across structures and reversal with predator development (D).** Independently verified G8/G11 27-rate effects on four-sign compatibility versus mean log frog cohorts, and P1 salamander early/late arrival × short/long aquatic duration intervention, with 124/256 loss-to-benefit source reversals and zero opposite reversals. **Source-backed editorial Figure3_D_RateAndDevelopment_EDITORIAL.png, pending author figure approval.**

**Supplementary only:** B's INBO, USGS and Mohonk records and source limitations are reported in S20/S22, not a main-text results section. R4 original long-term patch figure is preserved in S5. R5 is in S21 and justifies the need for independently manipulated counterfactual models.


## Evidence, reproducibility and status

**C (observed calling patterns) → D (controlled mechanisms), editorial review candidate.** Original B sources are preserved in SI S20/S22 as biological rationale rather than a third primary result. Neither calling nor the INBO/USGS associations establish tadpole *birth*, same-cohort survival or natural predation. Unverified INBO φ=+0.262 and Mohonk 29/30 and 29/59 are not reported as numerical findings. Original source-matched negative field tests and all original simulations remain unchanged. Original three-figure candidates for this framing: observational Figure1, two-function mechanism Figure2, and G8/G11/P1 Figure3, with R4 supplementary S5. Coauthor approval and actual project DOI are missing; **NOT SUBMITTED**.
