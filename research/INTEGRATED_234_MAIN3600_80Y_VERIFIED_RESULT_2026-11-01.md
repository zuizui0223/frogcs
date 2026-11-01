# Main3600 ②×③×④: 80-year source-verified integrated ABC→stage interventions→population prediction

**2026-11-01 | Verified GitHub Actions SUCCESS #41262102436 | Draft PR #160 | post-main research.** Same original main seasonal food-web model, same original nuisance rates and the same accepted original draw IDs throughout. Main results are preserved without replacement.

## Single scientific question

Under what ontogenetic arrangement and vegetation function does a food-web mechanism generate four originally observed macro directions, and does that *same compatible M,T,θ* imply a robust long-run population consequence of dispersal and S-larva→F-larva predation?

### ② 80-year ABC acceptance (original 3,600 structures, 20,000 simultaneous prior draws)

All eight actual deterministic source shards, exact 20,000 draw-ID and prior replay, and complete aggregation passed.

| Condition | Accepted | Rate |
|---|---:|---:|
| 40 years / 10-year endpoint, log F_B | 787/20,000 | 3.935% |
| **80 years / 20-year endpoint, log F_B** | **794/20,000** | **3.970%** |
| 80 years, raw F_B | 584/20,000 | 2.920% |
| 80 years, log F_B + original 5% survival floor | 426/20,000 | 2.130% |

Unique distinct accepted model IDs: 647 at 80 years (638 at 40 years). These are compatibility samples, NOT empirical posterior probabilities of biological mechanisms.

Stage context 0 (S arrives day40, D aquatic40d): 317/6,501=4.876%; context1 (S day40, D60d): 265/6,827=3.882%; context2 (S day0, D60d): 212/6,672=3.178%.

**Necessity claim corrected:** S→D predation edge absent 272/6,608=4.116% vs present 522/13,392=3.898%. The original frozen-rate zero-success result when S→D absent was NOT robust to sampling nuisance rates. The posterior axis shares depend on the original 3,600-catalog frequency and hypothetical rates.

### ③ Directly matched 80-year vegetation × developmental-order intervention

Exactly 96 of the 794 accepted sources were drawn *prospectively* (32 per context, seed 20261102) with weights preserving 80-year context acceptance mass. All 96 were replayed in all three contexts under the same structure/rates, separately toggling only cover_SF or cover_DS ON vs OFF. 1,152 actual 80-year source proposal evaluations, 9,216 eight-corner scenario evaluations; all main-original replays matched within **1.78e−15**.

| Pathway ON−OFF | Stage context 0: Δ4-sign passage, Δmean log F_B | Context 1 | Context 2 |
|---|---|---|---|
| **F sheltered from S (cover_SF)** | **+6.25 pp; +0.0435** | **+7.29 pp; +0.0430** | **−5.21 pp; +0.1120** |
| S sheltered from D (cover_DS) | +1.04 pp; −0.0067 | +9.38 pp; −0.0031 | +9.38 pp; −0.0148 |

**Novel joint insight inside this model:** frog refuge from salamanders improves the average F_B in all three contexts, yet its effect on whether the four-direction pattern appears changes sign with developmental order. Pattern-compatibility and population benefit are therefore distinct estimands. This is a *within-source, matched numerical intervention*, stronger than the original unpaired comparison, but not an observed field causal effect. The paired ON−OFF effect on mean log F_B did not reverse its sign for any of the 96 selected source draws, so do not say refuge changes from beneficial to harmful for absolute abundance. Context effects on 4-sign pattern compatibility and on mean abundance are different.

### ④ Same M,T,θ predicts finite-population 80-year occupancy

Exactly the same 96 accepted source IDs, original main season/annual expectation, with new explicitly declared integer sampling, and crossed 2 synthetic q scales × 2 S→F edge states × 2 movement states × 2 process seeds = **1,536 genuine 80-year stochastic arms**, all four source shards SUCCESS. Eight connected synthetic ring patches are the factorial vertices, NOT real NAAMP wetlands. Original external immigration remains ON.

Weighted mean year-80 F occupied patches (of eight):

| Synthetic scale | S→F edge | Movement OFF | Movement ON | ON − OFF |
|---|---|---:|---:|---:|
| q=3 | OFF | 7.519 | 7.724 | +0.205 |
| q=3 | ON | 6.461 | 6.657 | +0.196 |
| q=12 | OFF | 7.990 | 7.969 | −0.021 |
| q=12 | ON | 7.906 | 7.874 | −0.032 |

**S→F predation has a substantial negative model-conditional occupancy contrast at q=3** (roughly −1.06 patches at either movement setting), but the q=12 occupancy endpoint is near 8/8 and the difference is small (roughly −0.08 to −0.095). These are synthetic conditional predictions; the q contrast mixes discrete-population feedback and an occupancy ceiling, not calibrated field population sizes.

**Crucial non-result:** The specific *S→F moderation of the movement effect*, [movement ON−OFF with S→F] minus [movement ON−OFF without S→F], averaged over the accepted 80-year source draws with correct context weights, is NOT robustly different from zero:

| q | Mean moderation (occupied patches) | Source-draw bootstrap Monte Carlo interval |
|---|---:|---|
| 3 | **−0.009** | **[−0.264, +0.240]** |
| 12 | **−0.012** | **[−0.069, +0.041]** |

Conditional q3 context means are −0.125, +0.297, −0.219 for contexts 0,1,2 respectively (each only 32 accepted source draws; no independent field evidence or multiplicity-adjusted confirmation). This is *exploratory effect heterogeneity*, not a confirmed general dispersal-rescue sign reversal. The finite-N q=12 occupancy ceiling severely limits inference based on a zero-to-eight occupancy endpoint. Movement-assisted zero→positive events are indicators, not uniquely movement-caused recolonizations because original background immigration remains enabled.

### Reproducibility, merging and interpretation

[Full passing execution and downloadable source artifacts](https://github.com/zuizui0223/frogcs/actions/runs/41262102436). Final artifact: **integrated-234-final-scientific-receipts** with original IDs, all ② model/axis counts, ③ matched plant×stage values, ④ 384 paired stochastic source contrasts, the **192-row joint mechanism-stage-population table**, and manifest. Selection occurs ONLY from deterministic 80-year four directions; stochastic signs never determine acceptance. All original 96 source parameters are unchanged across pathway interventions and q/movement comparisons.

Code entry: research/scripts/abc_pom_main3600.py; integrated_80y_prepare.py; integrated_paired_stage_vegetation.py; integrated_finite_main3600.py; integrated_main3600_joint_report.py; test_integrated_234_main3600.py. Original seasonal/annual kernels are untouched.

**Evidence limit:** These are not fitted predator counts or a calibrated relationship from aquatic F_B to observed strong adult calls. Prior PR #158's independent real 4,248-site six-statistic audit found no single uniquely identified food-web cause. This study links compatible mechanisms to their own model consequences, NOT the empirically established cause of observed macroecology, NOT a validated 80-year forecast for real wetlands.

**Publication decision:** Present ② and ③ as supported model-native conditional generation, ④ as weak/conditional posterior prediction with strong size ceiling and no robust global S→F-specific movement effect. Maintain PR #160 Draft and do not promote this numerical study to a biological causal claim.
