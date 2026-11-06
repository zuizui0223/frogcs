# Supplementary Information — third-guild acoustic context and stage-structured vegetation-mediated trophic pathways

**Source-preserving draft · 5 November 2026 · accompanies [shortened manuscript main text](MAIN_TEXT_R1_R4_SUBMISSION_CANDIDATE_2026-11-05.md)**

## Supplementary Methods S1. Evidence levels and non-interchangeable source units

| Evidence | Original scientific unit | Number of units | What it measures | What it does **not** establish |
|---|---|---:|---|---|
| R1 geographical association | NAAMP repeated acoustic listening site | 4,248 | Recorded adult frog calling fraction against predicted environmental suitability for odonates and pond caudates | Observed pond predator abundance, larval fecundity or predation |
| G1 environment vs guild prediction | Same physical site, clustered into whole 2-degree spatial blocks | 4,248 sites; 56 blocks; 63,180 completed visits | Conditional held-out improvement in acoustic probability | Independent natural-pond causal effect |
| G2 response definition | Completed frog acoustic visit, aggregated to original site | 63,180 original visits | Recorded any-call and strong-call events | True frog occupancy, separate detection probability |
| G2B factored acoustic observation | The *same* site/visit cohort and spatial block | 4,248 sites; 47,912 any-call visits; 56 blocks | Statistical factorization of adult recording strength | A juvenile-to-adult biological maturation model |
| R2 joint mechanism proposal | One original-catalogue structure×developmental context×synthetic rate draw | 20,000 original proposals, from 3,600 legal model IDs | Whether four idealized source model contrast signs occur | Probability that a particular food-web model is the cause of field acoustics |
| PR161 new-seed paired mechanism | One independent canonical background with four plant variants and three developmental repeats | **256 independently sampled backgrounds**, 3,072 biology proposals / 24,576 2×2×2 source vertices | Within-background response to model-coded vegetation pathway interventions | Wild predation or vegetation refuge rates |
| PR162 genuine finite-N | One original plant/stage biology scenario×q×movement×stochastic seed | **24,576 simulated 80-year arms** from those same 256 independent backgrounds | Modelled frog counts and eight-patch colonization/extinction states | 24,576 independent natural ponds; calibrated long-term forecasts |

**Four distinct uncertainty types.** R1 source-route resampling intervals account conditionally for acoustic route clustering and hold SDM suitability fixed. G1/G2B block resampling intervals summarize prediction uncertainty under fixed original geographical folds and fixed model specification. R2 proposal fractions and their conditional Wilson intervals quantify finite Monte Carlo exploration of a synthetic model prior and are not a posterior from field observation. PR161/PR162 intervals resample original simulated model backgrounds and are **not** biological field confidence intervals. We do not equate or pool them.

## Supplementary Methods S2. R1 data and measured acoustic response definitions

The primary source selected 4,248 physical acoustic monitoring locations with repeated complete surveys, 432 route components, 63,180 completed original visits and response \`strong_all = n_strong / n_completed\`. Potential Odonata and Caudata predictor surfaces are aggregate SDM suitability for the six and seven retained respective taxa (including pond-breeding Caudata as the focal S subgroup); these estimates are derived from occurrence-environment models, not simultaneous pond larval counts. The plant variable V is a 3-km landscape wetland vegetation proxy, **not a measured in-pond refuge**.

The original response recomputation from completed site×run records passed the following fixed identities:

| Original visit statistic | Audited count |
|---|---:|
| Completed visits at retained acoustic sites | 63,180 |
| Visits with any recorded frog calling | 47,912 |
| Visits with strong calling | 36,554 |
| Site records with no any-call over survey window | 66 |
| Eligible site records for \`strong_given_any\` | 4,182 |

We compared three responses, with the original same full-cohort predictor-only caudate-suitability tertiles and original route-bootstrap seed \`20261027\`: (i) strong per completed survey; (ii) any call per completed survey; and (iii) strong per recorded any-call survey at sites where such surveys exist. Conditional outcome (iii) changes the observation denominator and excludes never-detected sites. It is subject to selection bias and must not be interpreted as the strong-call response among *all occupied ponds*. These probabilities are observational frequencies, not independently estimated false-negative/false-positive detection rates. Full per-tertile sample sizes and rederived original Spearman point/interval checks are in the [G2 source audit](https://github.com/zuizui0223/frogcs/actions/runs/41562618381) and [G2 report](../research/G2_ACOUSTIC_OUTCOME_DECOMPOSITION_VERIFIED_RESULT_2026-11-03.md).

**Table S1. R1 original high-minus-low pond-Caudata-suitability association differences, with source-route bootstrap intervals.**

| Geographic restriction | Outcome | Uniform SDM | Target-group SDM |
|---|---|---|---|
| Whole region | Strong / completed visits | −0.38475 [−0.50912,−0.24038] | −0.17869 [−0.32797,−0.02917] |
| Whole region | Any / completed visits | −0.35118 [−0.48520,−0.20353] | −0.14113 [−0.30073,+0.01750] |
| Whole region | Strong / any-call visits | −0.27298 [−0.37925,−0.15687] | −0.12616 [−0.24895,+0.00379] |
| Within route | Strong / completed visits | −0.12185 [−0.19870,−0.03423] | −0.07250 [−0.18303,+0.02286] |
| Within route | Any / completed visits | −0.05749 [−0.13954,+0.02780] | −0.07591 [−0.17284,+0.01343] |
| Within route | Strong / any-call visits | −0.13329 [−0.20729,−0.05491] | −0.02666 [−0.11823,+0.05698] |

A paired route-bootstrap comparison of the **within-route strong minus any high–low correlation contrast** was −0.06436 [−0.11593,−0.01165] under uniform backgrounds and +0.00341 [−0.05983,+0.06577] under target-group backgrounds. The first is a source-specific observational finding; the latter interval includes zero. The two SDM backgrounds use overlapping sites and do not constitute independent natural-pond replications. None of these rank associations is a measured causal trophic coefficient.

## Supplementary Methods S3. Spatial shared-environment null (G1) and two-part acoustic sensitivity (G2B)

### S3a. Shared-environment G1

For each original background, five test folds were formed from **56 whole 2-degree route-centroid spatial blocks**, keeping all records from a route in one fold. The source model used fixed penalized binomial regression with ridge=10 and acoustic site-count likelihood. The additive null includes survey/season/climate, water, landscape and geographic nuisance terms, plus additive odonate/caudate/vegetation suitability; the flexible model adds 21 outcome-blind environmental squares and pair-products. Both were frozen before evaluating the incremental O×S term. Source heldout predictions totalled 4,248 sites × 2 backgrounds × 8 G1 designs = 67,968 rows. The original G1 source audit is [Actions #41389390897](https://github.com/zuizui0223/frogcs/actions/runs/41389390897).

**Table S2. Incremental O×S held-out negative-log-likelihood improvement per original completed visit.** Positive means lower prediction error when the interaction is included.

| Frozen null | Uniform background | Target-group background |
|---|---|---|
| Additive environment + O×S | +0.001692 [+0.000123,+0.003494] | −0.001786 [−0.003221,−0.000612] |
| Flexible nonlinear environment + O×S | −0.000092 [−0.000982,+0.001014] | −0.000097 [−0.001773,+0.001465] |

The flexible model itself yielded higher average held-out NLL than the simple additive environment under both backgrounds. Thus no incremental O×S success under the flexible comparison **does not prove** that common environmental functions fully explain real ecology; it only prevents a source-supported claim that O×S supplies stable independent predictive information across both available SDM-background specifications.

### S3b. Two-part adult acoustic observation G2B

For the same fixed spatial folds and original sources, \`any_all\` (47,912 events / 63,180 trials) and \`strong_given_any\` (36,554 events / 47,912 any-call trials) were fitted separately using only training blocks. Strong-call predictions for all held-out visits were then constructed as \(P(any)\,P(strong\mid any)\); a separate direct strong/all model was fit on the same training blocks. The four frozen explanatory architectures were environment additive and environment+O×S, each with or without the 21 nonlinear environment terms. The source contains **33,984 held-out site/background/design prediction rows, 32 acoustic model scores and 24 paired block comparisons**, all verified to the original site-count binomial losses. [Main G2B source audit](https://github.com/zuizui0223/frogcs/actions/runs/41921634037), [figure-only data reuse audit](https://github.com/zuizui0223/frogcs/actions/runs/41922244821).

**Table S3. Added O×S after the flexible nonlinear environment, source 56-block interval.** Conditional strong is scored **per recorded any-call visit**, other stages per **completed visit**; do not compare their NLL magnitudes as if they share denominators.

| Outcome | Uniform background | Target-group background |
|---|---|---|
| Any / completed | −0.000053 [−0.001082,+0.001034] | +0.000956 [−0.000932,+0.002647] |
| Strong / any recorded | −0.000226 [−0.000664,+0.000180] | **−0.000515** [−0.000946,−0.000111] |
| Strong / completed, direct | −0.000092 [−0.000992,+0.000860] | −0.000098 [−0.001692,+0.001429] |
| Strong / completed, factored | −0.000202 [−0.001236,+0.000879] | −0.000482 [−0.001880,+0.000838] |

Under the original additive environmental predictor set, the *factored versus direct strong* response gained +0.000415 [0.000105,0.000736] NLL units per completed visit under uniform and +0.000860 [0.000307,0.001554] under target-group backgrounds. This is a small positive **statistical adult acoustic model** finding and does not separately estimate biological larval abundance, survey detection probability, breeding success or recruitment.

**Negative-source gate:** The original PR145 observed-acoustic prediction diagnostic previously showed that appending model-generated aquatic \(\log F_B\) to the environmental calling model did not improve out-of-block prediction against the full environmental interaction baseline. G1 and G2B did not overturn that failure. All three support the statement that source model competence at reproducing idealized trophic contrast signs is not a quantitatively adequate measurement model for adult calling.

## Supplementary Methods S4. R2 full model prior, sign convention and original-rate grids

The main 3,600 canonical model structures allow specific combinations of S→F, D→F, D→S and S→D trophic links, source vegetation functions and developmental paths. The 20,000 original hypothetical rate/context combinations sampled 3,582 distinct main catalogue model IDs. The original seasonal/80-year kernel generated eight V×S×D source corners per proposal (two levels each). The frozen criteria computed four log aquatic frog-cohort contrasts and required \`log_OS < −1e−6\`, \`log_OV < −1e−6\`, \`log_SV > +1e−6\`, \`log_OSV > +1e−6\`. **The signs do not reproduce observed NAAMP correlation magnitudes, nor constitute a field likelihood.**

All original 20,000 proposal results were regenerated *only by reaggregation*, not by biological re-simulation, from eight source-shard artifacts. Their 27 rate-cell denominator/accepted count table and SHA receipts are preserved in [R2 full source audit](https://github.com/zuizui0223/frogcs/actions/runs/41390511365).

**Table S4. Marginal original model-native 80-year acceptance.**

| Original synthetic factor | Low | Middle | High |
|---|---|---|---|
| Attack strength | 0.5: 421/6,555 (6.42%) | 1.5: 227/6,749 (3.36%) | 3: 146/6,696 (2.18%) |
| Local recruitment fraction \(\rho\) | 0.25: 106/6,607 (1.60%) | 0.5: 264/6,704 (3.94%) | 0.75: 424/6,689 (6.34%) |
| Maturation conversion | 2: 131/6,621 (1.98%) | 4: 280/6,707 (4.17%) | 8: 383/6,672 (5.74%) |

The highest **simultaneous** rate cell was attack 1.5, local recruitment 0.75, conversion 8 (78/710; 10.99%); low attack 0.5, local recruitment 0.75, conversion 8 yielded 47/717 (6.56%). Source viability sensitivity required minimum F and S survival of 5% across the original model evaluation; 426 proposals met it **and** the four signs. Of the 146 sign-compatible proposals at attack=3, zero met this model-specific floor. This synthetic threshold is not a measured amphibian survival threshold.

In the historical post-inspection rate region (attack 0.5, local recruitment 0.75; all conversions), the original proposal denominator was 2,245 and 179 proposals matched all four signs. Structural \`support_DF\` and \`cover_SF\` combinations had compatibility rates 12/424 (both OFF), 32/693 (frog shelter only), 29/453 (odonate feeding support only), and 106/675 (both ON). Those are **between-structure conditional associations**, affected by canonical catalogue composition and other structural features. They motivated rather than replaced the subsequent same-background 256-source intervention.

## Supplementary Methods S5. PR161 new-seed 2×2 interventions and predator-hazard diagnostics

The 256 original main-catalogue backgrounds were drawn with a new independent fixed seed, conditional on the two targeted source vegetation functions being legally switchable. The full legal quartet was 00/10/01/11 under identical non-target trophic links and nuisance rates for each background. Each was replayed across three original developmental contexts:

| Context | Model salamander stage input | Model odonate stage input | Additional distinction |
|---|---|---|---|
| 0 | S at day 40 | D at day 20 | D aquatic duration 40 days |
| 1 | S at day 40 | D at day 20 | D aquatic duration 60 days |
| 2 | S at day 0 | D at day 20 | D aquatic duration 60 days |

The context change is **not arrival-time-only** because the aquatic duration differs too. Across contexts and arms, there are 256×3×4 = **3,072** independent-origin model scenarios; the independent structural sampling unit is 256 backgrounds. No originally accepted 794-model sign outcomes were used in the new source draw. Original signs, source model IDs, per-frog hazards and eight-vertex biological outputs were audited against frozen source SHA/negative control. [PR161 biological source audit](https://github.com/zuizui0223/frogcs/actions/runs/41408471121).

**Table S5. Original source acceptance for four legal plant treatments, and artificial viability sensitivity.**

| Arm | Model flags | Four-sign compatible | Four signs + original 5% source survival |
|---|---|---:|---:|
| 00 | neither mechanism | 27/768 (3.52%) | 23/768 (2.99%) |
| 10 | frog sheltered from S | 44/768 (5.73%) | 36/768 (4.69%) |
| 01 | D→F feeding supported | 60/768 (7.81%) | 52/768 (6.77%) |
| 11 | both plant mechanisms | 108/768 (14.06%) | 102/768 (13.28%) |

The within-background both−neither effect was +10.55 percentage points [7.68,13.67], and the nonadditive two-factor interaction +4.04 [0.91,7.29] points. With original 5% survival these were +10.29 [7.42,13.28] and +4.82 [1.82,8.07] points. Stage-specific factorial interactions were +7.42 [1.56,13.67] (context0), +7.81 [3.13,12.89] (context1), and −3.13 [−5.86,−0.39] points (context2; no longer distinct from zero when the artificial 5% survival floor is included). There is no universal stage-independent synergy.

The original seasonal predator-hazard diagnostic was computed at vegetation=1, S-source=2 and D-source=2 and averaged over the three source contexts/backgrounds. Mean model S→F integrated per-frog hazard across the four arms was 0.624 (00), 0.378 (10), 0.622 (01) and 0.376 (11); D→F hazard was 0.488, 0.484, 0.929 and 0.945, respectively. **The corresponding reported D→F hazard shares 59.7%, 66.5%, 67.0% and 73.9% were individually calculated per source and then averaged**. They should not be reconstructed by taking a ratio of the *separate* average hazards: nonlinear ratios do not generally commute with averaging. All four interventions had identical source model population and hazard outputs at vegetation=0 (negative control).

The combined two-feature model mean-log aquatic frog-cohort difference relative to neither feature was −0.0841 [−0.1128,−0.0557] over contexts, although the sign was positive in context2. Original vegetation hazard directions are a **defined process assumption**; the new outcome is their source-matched joint sign compatibility and demographic response, not a discovery of a wild predator switch.

## Supplementary Methods S6. PR162 genuine finite-N demographic model and exploratory contrast separation

The 256 new-seed backgrounds were propagated into the **unmodified original PR160 stochastic annual kernel**, with eight artificial ring patches, q3/q12 synthetic count scales, movement OFF/ON and two independent process seed labels, 3 original developmental contexts and 4 plant treatments. This yields **24,576 true 80-year model arms**, completed across sixteen independent original model-source job shards. The model includes annual **external immigration ON** and delayed recruitment; a 0→positive patch return can reflect local recruitment, migration or external inputs. Its numerical patch and flow bookkeeping was independently audited and source IDs were matched to the original PR161 cohort. [Original finite-N biological 16-shard source](https://github.com/zuizui0223/frogcs/actions/runs/41414717527) and [source-only independent audit and R4 figure outputs](https://github.com/zuizui0223/frogcs/actions/runs/41551412003).

**Table S6. Vegetation both-minus-neither effect on mean year80 occupied F patches (eight artificial patches).**

| Synthetic count scale | Movement OFF | Movement ON |
|---|---|---|
| q3 | −0.0221 [−0.1009,+0.0560] | +0.0293 [−0.0371,+0.0964] |
| q12 | −0.0033 [−0.0163,+0.0098] | +0.0104 [+0.0007,+0.0215] |

With q3 and movement ON, the paired plant 2×2 **factorial occupancy effect** was +0.1003 [+0.0182,+0.1797] patches while the **net** both−neither effect was uncertain. The q12 year80 all-eight-patches indicator was generally >96% across plant and movement arms, providing a numerical ceiling. Under q3 with movement ON, the both-minus-neither occupancy contrasts differed among developmental contexts: −0.0215 [−0.1074,+0.0703], −0.0859 [−0.1758,+0.0059], and +0.1953 [+0.0371,+0.3535] for contexts 0,1,2.

Years61–80 mean model frog counts **decreased overall** with both functions, by −5.3247 [−7.2045,−3.5368] frogs per artificial eight-patch ring at q3 with movement and −23.6539 [−30.8132,−16.9157] at q12 with movement. Under context2 alone, the source model can show positive count change. These counts are process-generated model integers, not observed frog abundances.

The additional movement benefit due to plant-state combination, calculated as \([moveON-moveOFF]_{11}-[moveON-moveOFF]_{00}\), was +0.0514 [−0.0417,+0.1471] patches at q3 and +0.0137 [−0.0013,+0.0286] at q12: both intervals included zero. An earlier exploratory 23-selected-source comparison of a **different** \`S→F predation edge ON/OFF × movement\` estimand gave +0.529 [+0.154,+0.898] at q3. These cannot be treated as replications or contradictions because the intervention, model-source population and inferential target differ. Even a positive reoccupation event does **not** uniquely identify model movement as its cause while external immigration is retained.

**Audit repair provenance.** In original PR162 calculations, a mean of twenty source occupancy fractions could slightly exceed 8.0 in floating-point notation despite integer final-year occupancy remaining valid; we changed **only** mean bound-check tolerance (1e−10). A later auditor erroneously filtered one developmental stage before checking all three were present; the source-only auditor corrected the grouping and reused **the same sixteen untouched biological artifacts**. No biological rate, source cohort process or selection threshold was tuned based on final effect signs.

## Supplementary Methods S7. Field proxy adequacy, statistical limits and selection history

The source PR158 site-map comparison tested 768 finite-N candidate scenarios per original SDM-background specification against six individual observed acoustic-site statistics. No candidate fell within all six separate marginal 95% observation intervals under uniform SDM backgrounds; **7/768** did so under target-group backgrounds, and **none** did under both. The six individual intervals are not a calibrated joint 95% acceptance test, and the map from model larval cohorts to adult calls was *unfitted*. These seven are **not** independently validated natural food webs or likelihood-based posterior samples. [Source PR158 field-proxy audit](https://github.com/zuizui0223/frogcs/actions/runs/41215171866).

The original **20,000-proposal rate-region selection was retrospective**. The subsequent 256-background plant-factorial calculation used a new independent numerical draw after freezing its synthetic rate and legal-catalogue design, which tests *model generality within those assumptions* rather than independent environmental or wild biological validity. There is no fitted likelihood of the NAAMP field observations over the original synthetic attack, recruitment or vegetation coefficients. The acoustic measurements are observed **adult male calling**, while F_B and per-frog hazard refer to a **simulated aquatic cohort**. Their mismatch is a binding limit, not an unreported nuisance sensitivity.

## Supplementary Methods S8. Decoupling salamander arrival and aquatic-stage duration (P1)

The original three-developmental-context experiment was confounded: salamanders arriving early were assigned longer aquatic exposure as well. After preregistering this problem, we crossed salamander arrival (day 0/40) and aquatic-stage duration (40/60 d) while fixing frog arrival to day 20 and frog aquatic duration to 45 d, and odonate arrival to day 20 and aquatic duration to 60 d. We reused **all 256 independently drawn canonical model backgrounds and their unchanged biological rate vectors**, including unsuccessful four-sign source models, and the original four legal vegetation interventions. The full design produced **4,096 genuine 80-year models and 32,768 original eight-corner biological responses**; 10,000 source-background resamples quantified Monte Carlo variation.

Crucially, **late/short (LS)** and **early/long (EL)** were not new counterfactual claims built from scratch: they were numerically verified copies of the original PR161 contexts 1 and 2. The independent audit reproduced **2,048 original 80-year source models and 16,384 source-corner outcomes** against archived source SHA records to machine numerical precision, including predation hazards and four interaction coefficients. At vegetation absent, all four plant interventions produced the same original biological source output. The only new input combinations were **late/long (LL)** and **early/short (ES)**, isolating arrival from residence duration. The fixed original attack=0.5 and local recruitment fraction=0.75 remain retrospectively chosen synthetic rates and are not inferred from original NAAMP adult calling.

**Table S7. Four developmental combinations and the model-native effect of turning both vegetation functions ON versus neither function.**

| Salamander timing × aquatic duration | Arrival/duration | Δ mean log aquatic frog cohort, 11−00 [source MC95%] | Δ four-sign compatibility, 11−00 [source MC95%] |
|---|---|---|---|
| LS: late/short | day40 / 40 d | **−0.1864 [−0.2266, −0.1464]** | +13.28 pp [+8.59, +17.97] |
| LL: late/long | day40 / 60 d | **−0.1860 [−0.2271, −0.1463]** | +10.94 pp [+6.25, +16.02] |
| ES: early/short | day0 / 40 d | +0.0021 [−0.0264, +0.0317] | +9.38 pp [+5.47, +13.28] |
| EL: early/long | day0 / 60 d | **+0.1163 [+0.0787, +0.1560]** | +2.34 pp [+0.78, +4.30] |

**Table S8. Pure arrival, pure duration and their difference-in-differences, moderating the both-minus-neither vegetation response.** These are contrasts between **model inputs**, not coefficients relating natural-pond phenology to calling.

| Moderator | Δ log aquatic F response [MC95%] | Δ four-sign compatibility (percentage points) [MC95%] |
|---|---|---|
| Earlier salamander arrival, averaging both durations | **+0.2454 [+0.1967, +0.2976]** | **−6.25 [−10.74, −1.95]** |
| Longer aquatic salamander stage, averaging both arrivals | **+0.0574 [+0.0438, +0.0714]** | **−4.69 [−7.23, −2.15]** |
| Early-arrival × long-stage interaction | **+0.1138 [+0.0880, +0.1409]** | Source-audited in full model table; do not infer its sign from separate main effects |

The source result is more nuanced than a universal natural priority benefit. Under the same model, earlier salamander arrival made a negative vegetation effect on frog abundance *less negative*, but an unambiguously positive effect emerged only with **early arrival and prolonged aquatic duration together**. Meanwhile, the increase in compatibility of the four idealized signs was smallest under that condition. This provides a controlled **counterexample to equating signature generation with focal-population benefit**, while leaving both mechanisms' true occurrence and magnitude in observed North American ponds unknown.

Numerical evidence: [original eight-source 80-year computation #41986676287](https://github.com/zuizui0223/frogcs/actions/runs/41986676287), [unchanged archived source identity replay and 256-cluster independent audit SUCCESS #41987600437](https://github.com/zuizui0223/frogcs/actions/runs/41987600437), and [two independent source-only plotted comparisons SUCCESS #41988533772](https://github.com/zuizui0223/frogcs/actions/runs/41988533772). Full [P1 numerical scientific report](../research/P1_PURE_ARRIVAL_DURATION_TRUE80_VERIFIED_RESULT_2026-11-05.md).

## Supplementary Methods S9. Source-blind field breeding chronology eligibility (G3)

The proposed regional hypothesis that earlier salamander breeding changes the vegetation–adult frog-calling association was **not tested against an invented proxy**. Original 15 NAAMP frog taxa, five *pond-breeding* caudates and two nonpond caudate controls were fixed to original main species keys. GBIF occurrence lifeStage facets for the United States, 2010–2025, passed all 22 API/source requests, but explicit egg-stage records were concentrated in two frog species (2,618 total; two taxa with ≥50 reports) and one pond caudate species (4,255 total; one taxon with ≥50 reports). The preregistered minimum was five frogs and three pond caudates with ≥50 records each. Therefore **G0 was NOT QUALIFIED** and no egg-onset region-year surface, no NAAMP vegetation×salamander-lead field interaction and no independent phenological field validation was performed. Early-season adult sightings are not a valid substitute for breeding onset. [G3 original metadata-only audited result #41976215608](https://github.com/zuizui0223/frogcs/actions/runs/41976215608) and [complete stop-gate report](../research/G3_GBIF_EGG_STAGE_G0_NOT_QUALIFIED_VERIFIED_2026-11-05.md).

## Supplementary figure inventory and reproducibility

The four-figure arrangement is a **proposed final submission composition**. The original individual panels were source-audited, but the four final editor-ready composited figure files have not yet been independently audited as one journal-specific package.

| Proposed output | Independently source-backed panels / data | Original run or code |
|---|---|---|
| Main Figure 1 | Observed high/low caudate suitability O–frog calling correlations and 3-km vegetation association terms | [Figure 1 source CI](https://github.com/zuizui0223/frogcs/actions/runs/41317178174) |
| Main Figure 2 | Original 27-cell rate prior; same-background 256-model vegetation 2×2 interaction; per-source predator-hazard share vs mean frog cohort | [27-cell audit](https://github.com/zuizui0223/frogcs/actions/runs/41390511365) and [new-seed 2×2 source CI](https://github.com/zuizui0223/frogcs/actions/runs/41408471121) |
| Main Figure 3 | Controlled P1 independent salamander arrival × aquatic duration, four plant states and opposite directions of sign-compatibility and frog cohort response | [P1 source independent audit](https://github.com/zuizui0223/frogcs/actions/runs/41987600437) and [two plotted comparisons](https://github.com/zuizui0223/frogcs/actions/runs/41988533772) |
| Main Figure 4 | Same new-256-background genuine 80-year finite-N frog occupancy and factorial by q, movement, developmental context | [R4 source audit and three panels](https://github.com/zuizui0223/frogcs/actions/runs/41551412003) |
| Supplementary G1 | O×S increment under additive vs flexible shared environmental heldout prediction | [G1 source](https://github.com/zuizui0223/frogcs/actions/runs/41389390897) |
| Supplementary G2 | Adult strong vs any vs conditional strong acoustic geographic contrasts | [G2 source](https://github.com/zuizui0223/frogcs/actions/runs/41562618381) |
| Supplementary G2B | Two-part adult calling heldout O×S increments and factored vs direct strong score comparison | [G2B models](https://github.com/zuizui0223/frogcs/actions/runs/41921634037) and [figure-only reuse](https://github.com/zuizui0223/frogcs/actions/runs/41922244821) |
| Supplementary mechanism/field fit | PR160 selected-96 source survival-floor sensitivity; original same-biological-source six-statistic failure; additional q/seed/migration scenarios | [Source audit](https://github.com/zuizui0223/frogcs/actions/runs/41298704170) and [field proxy](https://github.com/zuizui0223/frogcs/actions/runs/41215171866) |

The original files reside in the stacked draft branches PR160→PR161→PR162→PR163→PR164. The most recent source-backed original analysis manuscript is [here](MACRO_TO_MECHANISM_INTEGRATED_MANUSCRIPT_2026-11-01.md); the concise main text is [here](MAIN_TEXT_R1_R4_SUBMISSION_CANDIDATE_2026-11-05.md). PR164 and preceding stacked PRs are Draft; this submission reframing did not modify original main-model biological kernels. Neither submission nor coauthor approval is implied.

## Bibliography, data permissions and open science gates (incomplete)

**Bibliography not yet finalized.** Full journal-formatted primary references must be reconciled with verified source literature (including the appropriate NAAMP methodology, GBIF/SDM data access, GloBI, EarthEnv, original quantitative trophic/life-history studies and any weak-interaction theory invoked in the Introduction/Discussion). Do not insert an unverifiable reference or imply that a selected taxon’s predation rates have been empirically measured for this dataset. The original source-run GitHub provenance is provided above for numerical audit, but not as a substitute for formal scholarly citations.

**Data availability and permissions not yet approved.** Verify NAAMP source redistribution terms and whether site-level/geographic records may be deposited; verify GBIF-derived occurrence DOIs and original survey protocols. Only promise a specific archive or DOI after it is actually deposited. If raw files are restricted, specify a compliant script/data-access route rather than uploading source bytes without permission.

**Author and submission decisions still pending.** Four final composited figure files, original site-map graphic permission review, code archive version, author contributions/approval, journal-specific structure and a completed reference list. More synthetic sampling without new biological constraints would not resolve the missing field trophic/observation calibration.
