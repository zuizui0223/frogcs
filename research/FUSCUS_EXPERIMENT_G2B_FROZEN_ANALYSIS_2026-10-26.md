# Frogcs G2B: original randomized water-level × predator cue × temperature stage experiment

**Date 2026-10-26; prepared after inspecting the ORIGINAL SOURCE assignment columns, before reading numerical outcome columns.** Exploratory secondary analysis of an already published experiment, not an unseen/preregistered validation. Original study: Delgadillo-Méndez et al. 2025, [Freshwater Biology 70:e70124](https://doi.org/10.1111/fwb.70124), [public CC BY 4.0 CSIC dataset 10261/411885](https://digital.csic.es/handle/10261/411885). Source original Excel SHA256 `eb76b0ec8162278c14860fddcfe30a487ff9e8fc4b8fe40311f88dabe0fd9b25`, 59,841 bytes; read from source only, not committed.

## Scope and actual factorial assignment G0

Source workbook sheet `data_fuscus` with 32 columns. Factorial assigned treatments **30 vs 35°C**, **HW** (high water) versus **DD** (experimental drawdown), and **P** (predator chemical cue present) versus **NP** (cue absent). `Nest` is the three-collected-clutch factor, `Pool` is a shared thermoregulated **400-L water bath**, `Replicate` is the independently exposed ~0.8-L container, `ID_tadpole` is an individual nested in `Replicate`. The experiment started with 10 planned small containers × 3 tadpoles per treatment combination (8×10×3 = 240 assigned individuals). **This initial allocation is a reported protocol, not inferred from observed workbook rows.**

[Response-blind G0 source](results/part2_g2/fuscus_workbook_schema_g0.json) / [experimental-unit QC](results/part2_g2/fuscus_assignment_g0.json): only **226 individual rows**, **79 actual container IDs**, **8 bath pools**, **3 clutches** remain in the published workbook. **One of 10 planned containers is wholly absent from the `35°C|P|DD` arm**, and 10 other containers have fewer than 3 recorded individuals. **14 of the intended 240 tadpole records are absent** and cannot, without source documentation, be equated with deaths. All eight factorial combinations are represented by observed containers, but the effective bath pools must be treated as eight independent temperature units, rather than 226 independent temperature replicates. Treatment allocation is known; outcome columns have not yet been read.

## Estimands and frozen analysis, not reconstructed mortality by fiat

**A. Population survivor-denominator source check (mandatory before efficacy claims).** Read only `survival_G46` among the 226 actually observed ID rows, report valid coding and 0/1 counts by original arm, plus 14 unrecorded planned animals. No zeros are imputed for missing IDs. If binary values are absent or inconsistent, fail closed on survival. Report two *explicit sensitivity bounds*, not a unique treatment survival effect:

1. **Missing-as-dead lower bound**, 30 planned animals per original arm: count recorded `survival_G46=1` / 30. This is valid as a true mortality estimate **only if** the publication's allocation and absence-as-death record policy are separately verified.
2. **Missing-as-survived upper bound**: (recorded survivors + [30 − number of recorded animal IDs in that arm]) / 30. Missing is treated as possible survival, regardless of unrecorded fate. If any arm shows more than 30 recorded IDs or nonbinary labels, abort.

For both bounds, report explicitly 80 intended, 79 observed containers. Do not pool three animals within a container as independent experimental replicates. The 400-L shared bath pools are independent units for temperature inference, with just four per temperature regime.

**B. Primary developmental phenotype among observed metamorphs**, independent of survival ambiguity: `mass_46` body mass at Gosner stage 46. Source design says body mass in grams; **valid** if numeric, positive and paired with individual source record. Target analysis: mean `mass_46` **per recorded container** (unweighted by the number of surviving tadpoles) to prevent pseudoreplication. Containers without measured metamorph body mass are excluded with QC count, no value imputation. This is the **conditional phenotype of survivors**, not treatment causal effect on all originally assigned embryos.

- M0 **environment only**: temperature °C, binary DD, and fixed three-clutch indicator (within a bath unknown handling accounted by out-of-bath validation).
- M1 **biotic risk**: M0 + source binary P (predator chemical cues).
- M2 **interaction**: M1 + DD × P interaction.
- Primary predictive test: same eligible containers, `LeaveOneGroupOut` across **8 entire original temperature-controlled water bath pools**, ridge α = 10 and training-only z-scaling; site-weighted MSE on log body mass and bath-equal-weight MSE. All three models evaluated on identical held-out containers and folds.
- Uncertainty: 2,000 deterministic bootstrap draws of the **8 bath-specific held-out MSE difference** (conditional on predictions), report interval as descriptive, not independent field replication; leave-one-bath-out fits automatically prevent bath leakage. Also report a simple **within temperature × water** cue contrast and an **interaction difference-in-differences**, with n per arm; mark observed conditional effects as exploratory.
- Optional descriptive sensitivity: body mass among survivors by all eight treatment arms; don't interpret bias-free if survival differs across arms.
- Do not fit across-nest independence without reporting clutch group; 3 clutches are too few for confidently portable estimates. No dynamic year-to-year pond hydroperiod or true consumption endpoint.

**C. Secondary response:** `time_to_46` days until complete metamorphosis, only valid among observed survivors; same M0–M2 predictor set and bath holdout. No retuning if negative. Do not silently condition on `survival_G46` to remove inconvenient values; report selection explicitly.

### Hard stop rules

1. If original SHA, eight arms, temperature nesting, source stage columns or the treatment/integrity gate fails, no biological effect is fitted.
2. Use the recorded source values; **missing 14 source rows never silently become deaths or equal zero**.
3. A predator **cue** is risk perception, not an actual predation event, consumptive loss, or field predator density. `DD` is lab-controlled drawdown, not a verified climate drought kill.
4. The study supports a direct **experimental environmental × perceived predator-risk stage response** within *Leptodactylus fuscus*; it is not a co-located explanation of NAAMP's multi-stop acoustic concentration and cannot calibrate real pond predator attack coefficients without new measurements.
5. If M2 fails out-of-bath transport, retain that adverse result and **do not** conclude a supported three-way predator×drought×temperature developmental effect.
6. Prior reported findings from the original article have already been read during source discovery; label every numerical reanalysis postpublication exploratory and attribute the original experiment. Do not claim the current secondary analysis discovered this experimental phenomenon.

### Publication gate

If the original-data experiment is correctly decoded and analysed, it is **G2B: controlled cue × artificial drying stage-phenotype evidence**; true field G2 remains **BLOCKED**. Place the result in the unified manuscript as an independent mechanistic plausibility **and counterexample** only, not as proof that NAAMP's spatial acoustic pattern is caused by aquatic predator legacy. Emphasize condition-specific no-effect and effects of temperature/water even if predator cues fail.
