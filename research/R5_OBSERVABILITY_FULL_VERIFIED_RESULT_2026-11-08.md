# R5 complete — observation-proxy loss is possible, but cannot by itself explain the real field failure

**8 November 2026.** The response-blind source/geometry preflight [#42445478134](https://github.com/zuizui0223/frogcs/actions/runs/42445478134), original 24-scenario virtual observer simulation [#42446291543](https://github.com/zuizui0223/frogcs/actions/runs/42446291543), and *reporting-only* full-scenario source verification and categorical-ID correction [#42446992844](https://github.com/zuizui0223/frogcs/actions/runs/42446992844) have completed. All three **SUCCESS**, except the superseded first reporting-only attempt #42446918954, which failed JSON serialization of a NumPy Boolean and was repaired **without recomputing any simulations**. The complete original science run always succeeded.

**Scientific state:** CONDITIONAL VIRTUAL OBSERVABILITY LOSS SUPPORTED; EMPIRICAL REASON FOR ORIGINAL G5/G14/G15 FAILURE NOT IDENTIFIED; NATURAL TROPHIC MECHANISM NOT IDENTIFIED.

## 1. Pre-outcome fixed sampling and truth

The [frozen R5 protocol](R5_VIRTUAL_ECOLOGIST_OBSERVABILITY_FROZEN_PROTOCOL_2026-11-08.md) was recorded before R5 output inspection. Source: 256 legal independent canonical source backgrounds ×3 developmental contexts, eight model-cohort vertices in each vegetation path setting, averaged into original G4/G5 **both vegetation functions OFF (00)** and **both ON (11)** source surfaces, never rerun or selected for favorable R5 results. Those are **mean model log aquatic frog cohorts**, not wild larvae counts.

The virtual landscape preserves the original NAAMP 4,248 sites, 63,180 completed site-visits and 56 geographic blocks/five spatial CV folds. Exactly **24 conditions ×100 independent binomial call realizations ×2 observer SDM backgrounds =4,800 source-confirmed heldout evaluations**; all conditions, failed and positive, are retained.

The *conditional* virtual truth uses either the original uniform or target-group O/S occurrence-SDM ranks, never an observed density census; the source 11 or 00 interaction signal on these ranks and hypothetical true local V; a fixed original-field flexible additive environmental calling baseline; and hypothetical \(p_{i}=\mathrm{logit}^{-1}[\mathrm{logit}(p_{0i})+\gamma\,z(\phi_{\mathrm{source},i})]\) with \(\gamma=0,0.25,1\). Actual original site-specific completed-visit counts generated binomial synthetic calls. Observer models saw the two unchanged original SDM backgrounds and original landscape V, with original spatial folds and G5 source-shaped nonnegative training-only coefficient, original 00 alternative, and flexible environmental null. The original 56-block 999-resample lower-95% NLL improvement had to be >0 **against both OFF and additive environmental baselines** for recovery. The unrestricted saturated O/S/V interactions were scored separately to assess structural equivalence, **not** used as causal truth.

**Illustrative pond vs landscape error:** exactly 25% (separately within original V=0 and V=1 categories) of true V values were flipped in a frozen outcome-blind site mask. Because mapped V=1 occurs at only 506/4,248 sites, this **changes true V-positive prevalence** from 506 to approximately **1,316/4,248** in the error world. Neither the 25% discordance nor the resulting prevalence is empirically estimated; this is a deliberately strong what-if sensitivity. True pond vegetation and local predator density are not measured by NAAMP.

## 2. Main positive outcome: two proxy errors together can remove recoverability

True source arm **11**, illustrative nonzero call-link \(\gamma=0.25\); recovery counts out of **100 independent observed-style virtual datasets** for every row:

| Virtual-truth ranks | Observer ranks | V true = V landscape | 25% true-pond V discordance |
|---|---|---:|---:|
| Uniform | Uniform | **100/100 (100%)** | **87/100 (87%)** |
| Uniform | Target-group | **100/100 (100%)** | **55/100 (55%)** |
| Target-group | Target-group | **100/100 (100%)** | **80/100 (80%)** |
| Target-group | Uniform | **93/100 (93%)** | **12/100 (12%)** |

The weakest conditional result, 12/100 (Wilson 95% **7.0–19.8%**), occurs with target-group true ranks, uniform observer ranks and 25% hypothetical V misclassification. Relative to the **same target-group true world** with perfectly aligned observed ranks and V (100/100), recovery falls by **88 percentage points**, conservative bound by separate 95% Wilson limits **76.5–93.0 points**. For the uniform true world, the corresponding 100%→55% reduction is **45 points** (conservative Wilson-bound interval **31.9–54.8**). Rank mismatches alone are much weaker under these particular fixed source ranks; the combination matters.

Crucial counterexample preserved: with the stronger, still hypothetical \(\gamma=1\), true uniform ranks and both proxy errors yield **100/100 recovery** (no detection loss), whereas true target-group ranks with both errors yield **57/100**, compared with 100/100 when aligned. **Observation failure is therefore NOT inevitable whenever the vegetation pathway exists.** Detectability depends on the assumed observation-link strength and the particular correlated proxy errors.

## 3. Critical controls and null results

- The **zero-signal negative control** \(\gamma=0\) falsely favored the source 11 over 00 **and** flexible additive in **9/1,600 observer evaluations =0.5625%** (pooled Wilson 95% **0.296–1.066%**). This conservative error rate should **not** be described as a calibrated nominal 5% test; its uncertainty interval excludes 5%.
- When the **true source arm was 00** and \(\gamma>0\), 11 was falsely recovered in **0/1,600** observer evaluations; the prespecified recovery contrast does not simply always prefer 11.
- The no-binomial-noise **expected-call oracle** recovered 11 in all eight matching-rank positive-link cases (two source truths × two nonzero gamma × both V states; source arm 11). This does **not** identify the actual source in wild ponds.
- Relative to a **saturated freely fitted empirical O/S/V interaction** model, the source 11 predictor is not uniquely identifying. Original G4 source interpolation fits the eight-term empirical span to ~10^−14 maximum residual, so the eight O/S/V terms can mathematically represent the same landscape signature without being the true predation mechanism.
- Adult calling data lack salamander arrival and aquatic duration. R5 did **not** identify the P1 stage-specific reversal from field calling. R5 also did **not** rerun the original 794-proposal G14 ABC-ensemble source comparison: it probes the **original G5 00/11 controlled source shapes** using the G14 geographic evaluation conventions. The original G14/G15 dual-background failures and G17 numerical replay failure remain unchanged.

## 4. Scientific interpretation, strict limits and journal decision

**What R5 supports:** Known model source differences can become difficult to recover when plausible categories of imperfect proxies (rank inputs and pond–landscape V disagreement) are jointly altered. Such conditional observation losses can coexist with mathematical pattern-generation and model-cohort effects. This demonstrates a **potential identification bottleneck**, not an empirically established explanation for G14/G15.

**What R5 does not support:** No observed pond-level Odonata/Caudata densities, actual within-pond submerged vegetation, experimental salamander arrival-duration treatments, adult-calling sensitivity to larval *abundance*, or individual larval survival were acquired. G18's USGS same-sample co-detection association **does not calibrate \(\gamma\)** or the 25% V discordance. A specific N-pond power/80% field-design requirement cannot be inferred. Matching a source shape more often than an *additive* null is not identifying its biological cause against a saturated interaction model.

**Editorial disposition:** Include one careful Discussion sentence on conditional observer-sensitivity and complete SI S21 methods/results with all controls; do **not** replace the main model-based ecological conclusion or reframe failure as proof of natural mechanism. Do **not** retune, restart, or append G19. The existing frozen Ecology Letters original submission package remains a separate coauthor-review authority pending author approval, rights clearance and permanent repository DOI.

## 5. Original numerical source, QA and correction

- [R5 original all-24-scene science run SUCCESS #42446291543](https://github.com/zuizui0223/frogcs/actions/runs/42446291543): **all 24 scenario shards and the full 4,800-row aggregate have succeeded**. Original artifact: `frogcs-R5-24worlds-100rep-full-audited-results`, ID **13603733316**.
- [R5 reporting-only categorical correction and 48-cell independent recheck SUCCESS #42446992844](https://github.com/zuizui0223/frogcs/actions/runs/42446992844). Archive: `frogcs-R5-observer-power-complete-reporting-qa`, original 4,800 heldout results, 48 fixed cells, 48 oracle cells and conditional power contrasts. This corrected pandas `read_csv`'s interpretation of literal string arm `00` as number 0. It did **not** change the underlying simulated predictions, NLL estimates, bootstrap CIs, or model runs.
- [R5 reporting-only source and scenario audit code](scripts/r5_reporting_only_dtype_repair_20261108.py); [source experiment engine](scripts/r5_virtual_observer_frozen_20261108.py).
- 56-block spatial grouping, exactly 100 replicates in all 24 conditions, source solver equivalence to the original G5 implementation, and all original 4,248/63,180 count gates **passed**. The numerical source model itself was not rerun.

**Single defensible take-home:** *Observation-proxy mismatch can substantially reduce power to detect a known simulated food-web response, but cannot establish which food-web process operates in nature, nor which error caused the actual acoustic-field prediction failure.*
