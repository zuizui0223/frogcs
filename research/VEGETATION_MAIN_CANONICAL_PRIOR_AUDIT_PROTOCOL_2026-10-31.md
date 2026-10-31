# Canonicalize original main's vegetation × behavioral-refuge model-space prior (2026-10-31)

The genuine 18,432-run, 144-class cross-ontogeny vegetation ABC was intentionally a **complete 2×12×3×2 factorial experiment**, but not every one of these factorial conditions is a distinct **main** model. `research/scripts/final_mechanism_common.py` canonicalizes `behavior="risk_refuge"` to `none` whenever `cover_SF=0`. The current new 144-class equal-class ABC instead counts both `risk=0,1` when frog shelter from salamanders is OFF, even though the seasonal model implements identical F_B in those cases. This double-counts some `SF0` hypotheses and biases the equal-class normalized shares. It does **not** invalidate the actual trajectories or paired ecological intervention contrasts.

## Source checks and fixed sensitivity

1. Read all six genuinely run 80-year source artifacts from [completed simulation Actions #41184627221](https://github.com/zuizui0223/frogcs/actions/runs/41184627221). Reject if any of the **4,608 same draw×reverse×plant×context×handling baseline SF0 risk0/1 pairs** disagrees in four log and raw interaction effects (≤1e−10 numerical tolerance), minimum/maximum F_B or four-sign acceptance. This is the crucial proof that risk=1 is not a distinct biology when coverSF=0.
2. Collapse duplicates by keeping risk=0 for SF0. Exactly **108 main-canonical classes** remain: each of 3 ontogenetic orders ×2 feeding contexts has **6 SF0 plant roles×1 risk +6 SF1 roles×2 risk =18**, hence 3×2×18=108.
3. Keep the same **64 original biological rate draw IDs**, both reversal cases, two log/raw response scales, target exact four signs OS− OV− SV+ OSV+, and same common 999-rate bootstrap indices. No new model parameters, noise, acoustic transport or biologically calibrated source priors.
4. Compare **three explicit structural priors**, with equal prior weight over represented classes in different ways:
   - `canonical108_equal_class`: equal prior weight on each of 108 canonical structures;
   - `equal_12_plant_roles`: each of 12 legal plant roles has equal mass; spread uniformly among the canonical stage/handling/risk classes within that role;
   - `main3600_role_multiplicity`: use the actual **marginal number of main's 3,600 catalog structures in each of the 12 plant-role groups** as plant-role prior mass, then distribute uniformly among the canonical classes in that role.
5. Note that the third prior **does not** mean the rest of main's 3,600 model axes have been run; it only tests how the role **prior multiplicities** affect conclusions and is not a biological prior. The other main axes (emergence changes, feeding support, S↔D edge ablation, cue) are still fixed as in the cross-stage experiment.
6. For each prior and log/raw model, normalize weighted exact ABC acceptance. Report timing, handling, risk and 12 plant-role marginal conditional shares and full paired common-rate bootstrap CIs. If an accepted class has too few independent draws, do not claim well-constrained biological rate parameters.

## Interpretation ceiling

If the same stage×plant interaction sign reversals remain across all three priors, they are **model-internal pathway responses at the tested rates**; if the relative model selection changes when redundant structures are collapsed or catalog role frequencies are used, the previous 144 model normalized shares must not be promoted as unique ecological conclusions. This corrects an identifiable model-space counting issue *without erasing the original 144-case experiment or pretending to run 3,600 models*.

This is post-result sensitivity to prior architecture on **the same field-pre-adjustment four associations**, not an independent empirical test of vegetation causality.
