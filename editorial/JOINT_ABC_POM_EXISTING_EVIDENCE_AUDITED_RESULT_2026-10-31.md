# Frogcs — unified ABC–POM: existing source layer audit (SUCCESS, 2026-10-31)

**Executed read-only source audit**: [GitHub Actions #41207780504 SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/41207780504). Workflow retrieved five original compact CSVs by two immutable upstream Git commit SHAs, then executed [auditor](../research/scripts/audit_joint_abcpom_existing_layers_20261031.py). Its compact generated evidence receipt and CSV are preserved as a GH Actions artifact (retention period 30 days). This markdown fixes the scientific interpretation permanently in Git.

- Original PR146 scientific source SHA: c5ad81b1fb29a9bb92d742ee7004ae66a404dca9.
- Original PR155 q-grid scientific source SHA: 19d45ffb833e2970aff8d88de101736aee289d26.
- These are source revisions, not independent datasets. No new biological simulation, ABC model posterior or real-site calibration was executed in this audit.

## Verified source evidence

| Evidence | Actual source/sample | Observed execution result | Inference limit |
|---|---|---|---|
| Site-mapped observed POM, uniform background | 132 frozen cases, 104 distinct source surfaces, original 4,248 locations | **0 cases adequate to all 6 observed descriptive marginal 95% intervals**. Best case_005, distance **10.82687**, best 0/6 marginal patterns | No independently calibrated stage-to-acoustic observation process; no full 6-pattern field reproduction |
| Site-mapped observed POM, target-group background | Same 132 cases/104 response classes under second SDM background | **0 cases adequate to all 6**. Best case_036, distance **8.26239**, best 2/6 marginal patterns | Both backgrounds share NAAMP and modelled occurrence inputs |
| Original model-native rejection ABC | 12 process structures ×256 hypothetical biological rate draws ×2 paired reversal flags = **6,144 genuine 80y source runs** | **254 simulations** produced all 4 *model-native* signs; original-stage baseline no-risk source **65 independent rate IDs /256** | Sign success under a balanced synthetic 2×2×2 supply grid is not real-site 6-statistic adequacy or posterior over field causal mechanisms |
| Structural-prior variation | 108 original canonical stage×plant model classes, three different hypothetical structural prior weights on log scale | **At least two different leading plant roles** depending on prior | No uniquely identified vegetation mechanism |
| Finite-N long-run model | Original source q3,q6,q9,q12, each 12 independent RNG seed labels, 2 original nominal plant settings | Strict stage-growth movement sign reversal with S→F-only: **2/2, 1/2, 0/2, 0/2** | Synthetic counts-per-density q, selected rate/plant priors, not observed wild year80 occupancy |

**What this DOES establish:** the candidate class can generate particular theoretical signs, but none of the original source's fixed 132 site-mapped candidates jointly fitted the six empirical spatial patterns under either SDM background. In a different conditional 80y model, demographic movement outcomes were strongly q/rate-dependent. The contrast makes the **mechanism identification problem** more interesting and sharply limits a one-mechanism narrative.

**What this DOES NOT establish:** the 254 model-native accepted runs are NOT a field posterior sample, and the 12/108-class model-native library is NOT the same as the site-mapped 132 fixed-case library. The q3–q12 demographic stress grid is a third sublibrary. Therefore the number or fraction of candidate mechanisms satisfying ALL field+demographic requirements is **NOT ESTIMATED**; do not write "0 of all possible mechanisms" or claim field-conditioned year80 predictions.

## Exact next joint inference

A single actual source model/parameter library keyed by canonical structure, plant role, stage, rate draw θ, paired reverse flag and site observation operator must generate BOTH:
1. the same six observed 4,248-site POM pattern summaries under both SDM backgrounds, with 56-block observed covariance and held-out within-route patterns; and
2. the original trophic/delayed 80y source with integer finite-N outcomes at q and migration sensitivity **without adjusting θ after looking at site suitability fits**.

Only if some hypotheses pass *absolute site-pattern adequacy* may ABC-conditional demographic predictions be reported. NAAMP does not measure year80 larval F occupancy, so these later outcomes cannot be appended to the ABC likelihood as another observed target. If none passes, stop at **NO_FIELD_CONDITIONED_DEMOGRAPHIC_PREDICTION**, retaining the complete model-native feasibility and explicit failures.

## Manuscript scope

This is **one result**, not "main result 2: process-model winner" plus "main result 3: a separate supported long-run demographic mechanism". The new [English manuscript](MACRO_TO_MECHANISM_HIGH_IMPACT_MANUSCRIPT_2026-10-31.md) merges both into one integrated ABC–POM Results section, with one proposed Fig3 and Supplement with rate/plant/q and exact observed-model mismatches. RC6 rainfall spatial concentration remains only historical Introduction motivation.

**Editorial status:** source-provenance audit COMPLETE; genuinely matched real-site biological ABC library, field observation calibration, three journal-ready figures, source figure/SI audit, authorship approval and actual manuscript submission are NOT COMPLETE.
