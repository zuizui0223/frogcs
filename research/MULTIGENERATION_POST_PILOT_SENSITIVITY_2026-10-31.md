# After-first-pilot sensitivity: reversal intensity, movement and third guild

This addendum was declared **after** inspecting the 20-year default pilot (`MULTIGENERATION_ABM_PDE_PILOT_RESULT_2026-10-31.md`), which showed synthetic dragonfly extinction with the uncalibrated F→emergence predation coefficient 0.12. Therefore this is explicitly exploratory, *not independent or preregistered confirmation*.

Finite fixed diagnostic grid:

- F-adult→D-emerging attack rate `a_fe = {0, 0.01, 0.04, 0.12}`, nonnegative, **illustrative model-year intensities**, not frequencies from Beranek et al. (2023).
- Spatial mobility **baseline stage-specific diffusion/jumps** vs **none**.
- Third-guild D-nymph→S-larva consumption **baseline 0.018** vs **removed 0**. Keep S-larva→D-nymph disabled because no universal pair-specific support.
- All other seven-state hazard, maturation, annual reproduction, vegetation and density dependence parameters fixed at the pilot values.
- The 4×2×2 grid runs deterministic PDE for 20 years and ABM for two held-fixed seed labels (101,102). All arms include `a_fe=0` as a **paired counterfactual within that movement/third-guild setting**. Compare years 1,2,5,10,20.
- Primary diagnostic: `D_adult(on)−D_adult(0)`, `D_nymph(on)−D_nymph(0)`, `F_adult(on)−F_adult(0)`, `D_occupied_cells(on)−D_occupied_cells(0)`. This is not population data or a parametric sensitivity distribution. All rates must be included even if the candidate effect is absent or reversed.

Expected logical checks: zero-rate arms exactly match reference simulation in both models for the same seed; all counts and cell occupancy nonnegative/bounded; no model changes or leakage into PR #145 acoustic results. Numerical ABM/PDE agreement is descriptive and not assumed exact under stochastic extinctions.

Question addressed: Does a reversal effect remain for weaker assumed predation, if dispersal buffers local collapse, and if third-guild predation is absent? Because these factors were not estimated in the field, the test defines **conditional model sensitivity**, not a biological prevalence estimate.
