# P1: independent arrival vs aquatic-duration effects behind the PR161 vegetation sign reversal

**2026-11-05. Prospective original-source numerical intervention; frozen before looking at any of its new outputs.** Stacked after G3 G0 failure (PR163) and original R1–R4 (PR162). Do not refit original NAAMP observations, alter old source results, or claim that GBIF adult sightings show breeding onset.

## Scientific identification problem

PR161 used three original developmental contexts. The sharp response difference between original context 1 (S arrives day40, S aquatic 40d, D aquatic 60d) and original context 2 (S arrives day0, S aquatic 60d, D aquatic 60d) **simultaneously changes two variables**. Its reversal in vegetation effects therefore cannot be attributed uniquely to species arrival order or stage duration.

The new numerical experiment asks whether the model-native reversal depends on (i) relative salamander-vs-frog arrival, (ii) salamander aquatic stage duration or (iii) their interaction, with the **same 256 original PR161 canonical source backgrounds and every other model feature/rate fixed**.

## Precommitted design

- Reproduce the **exact original PR161 seed-20261123 sampled 256 legal base model backgrounds**; not only the 108/768 four-sign successes and not only original field-favorable sources. Original main 3,600 canonical structures/seasonal kernel from immutable main SHA `5e2f0a87c639df373fa2700b29403d2ab417a1cc`; fixed hypothetical attack=.5 and local rho=.75, original conversion/refuge strength/refuge_order/size gate and all other predator and plant features untouched.
- Cross **four mutually controlled developmental contexts**, all with frog arrival day20, F aquatic duration45, odonate arrival day20 and D aquatic duration **60d**:
  - **LS (late/short)**: S arrival day40, S aquatic duration40. This is original PR161 context1; must numerically replay its original saved true80 outputs.
  - **LL (late/long)**: S arrival day40, S aquatic duration60. **New.**
  - **ES (early/short)**: S arrival day0, S aquatic duration40. **New.**
  - **EL (early/long)**: S arrival day0, S aquatic duration60. This is original PR161 context2; must numerically replay its saved true80 outputs.
- For each original background × context, preserve **all four legal vegetation interventions**: 00 (neither), 10 (F sheltered from S), 01 (D→F vegetation feeding support), 11 (both). **256×4 contexts×4 plant arms = 4,096 genuine original model 80-year scenarios**, each with **eight original V×S×D design corners = 32,768 genuine model source responses**. Shard into **8 jobs ×32 original independent model backgrounds ×16 source outcomes =512 scored rows** each. `dt=.5`, original 120d seasons nested within **80 true years**, final **20y average**, original `epsilon=1e−6` directional compatibility; no arbitrary extra normalization.
- The *same model background* is the resampling unit (**256 distinct M×theta sources**). The four developmental contexts, four plant roles and eight corners are paired within each background and **must not** be treated as independent real wetlands. **10,000 fixed seed-20261126 bootstrap source resamples**. Source rate regime was retrospectively chosen in earlier R2 and remains uncalibrated. The model design rather than new data determines which two stage variables are manipulated.

## Primary outcomes and contrasts fixed now

**Primary demographic endpoint:** PR161 original source `mean_log_F_B` over all eight V/S/D corners and its *within-background vegetation both-minus-neither contrast* `P = F_log(11)−F_log(00)`. Estimate the two separate moderation effects:
- Pure S arrival moderation of vegetation: `[P_ES−P_LS + P_EL−P_LL]/2` (early minus late, averaging short and long).
- Pure S aquatic-duration moderation: `[P_LL−P_LS + P_EL−P_ES]/2` (long minus short, averaging early and late).
- Their interaction (arrival × duration moderation of the vegetation effect): `P_EL−P_ES−P_LL+P_LS`, plus report **all four original P values**. A source-cluster bootstrap 95% range excluding zero is conditional evidence for a numerical model response; it is not field evidence.

**Secondary mechanisms:** For the same four contexts, evaluate `mean_F_B`, four-sign model compatibility with `epsilon=1e−6`, auxiliary synthetic minimum 5% F/S survival condition, `log_OS, log_OV, log_SV, log_OSV`, and per-larva `H_SF`, `H_DF` and **mean of original source-level** D→F hazard shares at V1/S2/D2. Report four plant treatment rates and both factor moderators of **4-sign compatibility**, **net frog abundance** and **predator-specific relative hazard**; do not infer actual wild predator mortality.

**Numerical consistency and source-matching negative controls:**
1. Before analysing effects, reproduce **exact old PR161 80y source output** for **LS=original context1** and **EL=original context2**, all **256×4 arms each** against the frozen successful PR161 artifact [run #41408471121](https://github.com/zuizui0223/frogcs/actions/runs/41408471121), matching original model IDs, source rates, four sign coefficients, F_B and predator hazards. Audit all eight source corners of these duplicated contexts too. Missing source labels or values = fail, no interpretive report.
2. **V=0** must be identical across the four vegetation flags, within each model×controlled context×S/D supply vertex; preserve missing/zero-hazard cases. No remapping illegal original catalog models.
3. The source generator uses **exact original sampled 256** model backgrounds, not a new favorable draw after stage outcome inspection. No source exclusion based on viability or sign.
4. Keep original G3 GBIF G0 result **NOT QUALIFIED**, and *do not* run the proposed geographical `vegetation × breeding lead` correlation with GBIF adult observations.

## Interpretation

A separate contribution of earlier salamander arrival is a **model-internal pure arrival intervention**, not confirmation of an empirical priority effect. It does not rule out environmental or observation-process confounding at NAAMP sites and cannot replace the PR145/G1/G2B negative predictive discrimination result. The broad main story remains that generating an interaction-like signature and supporting a focal population are **not equivalent**; developmental timing and stage duration distinguish *why* the same vegetation mechanism has conditional outcomes.

Original source calculations and audited results go to a separate stacked Draft PR based on PR163; no merge or submission.
