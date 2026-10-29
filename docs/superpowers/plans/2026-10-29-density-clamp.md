# Density-clamp discrimination implementation plan

**Goal:** Separate frog depletion from predator removal and compare F refuge with joint F/S refuge.
**Architecture:** Copy seasonal kernel, preserve defaults exactly, replenish losses of specified aquatic guilds after each integration step. No annual recruitment under this intervention. Accumulate replacement inputs; keep resource accounting. Individual sentinel survival is exp(-H), not replenished cohort completion.
**Stack:** Existing Python/numpy/pandas.
**Authorization:** User asks to set next goal and continue; implementation choices delegated through preceding research instructions. No new user preference needed.

## Fixed design before outcomes
- Clamp modes: none, F, FSD. Matched seasonal starts; F initial1/3/6, S/D .25/2, V0/1.
- Four vegetation roles: none, F-from-S, S-from-D, F-and-S. Strength.25. Families constant/II/III/mixed, K1; handling1000/1111; all3 existing stage contexts; DS edge0/1. Same attack.5, Farrival20/Fduration45, Sduration80, reversefalse,cue0.
- Total13,824 cells per timestep, dt.25/.125. Freeze design before execution. All pathways and failures retained. This is a within-season controlled intervention; not the prior80-year source-cohort experiment or a rank-fit test.
- Primary compare OS/OV/SV total and pathway hazards with/without F replenishment. FSD clamp is a structural null for density-mediated D->S benefits; it does not test behavioral effects absent from model.
- Direct discriminatory prediction: same S/D densities, changing V should reduce S->F hazard for F refuge, and D->S hazard for S refuge. These direct signs follow assumed functions; they are experimental design predictions, not empirical discoveries.
- Report noS-independent observational mediator measurements exist in current macro table; don't repeat same cohort fit as independent evidence.

## Tasks
- [x] Failing tests: default replay, replacement mass accounting/sentinel survival, predator-clamp edge invariance, invalid clamp.
- [x] Implement copied kernel, fixed runner, both timesteps and sign/edge summaries. No cache reuse; save hashes and full cells.
- [x] Identify what does/does not survive F clamp; mechanism comparison and distinguishable mediator contrasts.
- [x] Update report, manuscript, evidence ledger, output figures, tests, fresh review and PR144. Preserve frozen original paths.

## Adaptive bridge, fixed before bridge outcomes
With D->S enabled, the first matched-season grid has no positive OS in any mode, including dynamic. It therefore cannot establish that seasonal depletion is necessary for the prior multi-year OS. Add a diagnostic bridge using all saved20 actual year-start states for120 original scenarios, not mean-state substitution. Factorial initialF=actual versus common within year/context/handling, and seasonal F replenishment=off/on; retain actual S/D starts. All5 original handling arms,3 contexts,8V/S-source/D-source corners, both timesteps. Exactly replay original hazard means first. This identifies sensitivity to inherited F density contrasts separately from seasonal loss; it does not identify wild causes or re-equilibrate the intervention over years.

## Execution evidence
- New tests first failed on absent kernel import, then5passed; full168tests passed,894snapshot files verified.
-13,824cells per timestep, no cached calculations. Full primary/bridge outputs saved. Bridge replay max error4.44e-16.
- Original joint reference directions4/15; inheritedF+replenishment2/15; commonF0/15. Seasonal edge-off16/288 (8distinct), edge-on0/288, hence prior necessity claim qualified.
- Ruling: add pre-specified adaptive bridge after matched-season baseline failed to reproduce old OS. Retain that failure; do not present seasonal contrast as direct removal of the old annual mechanism. Cost: bridge interventions condition on old S/D starts rather than new annual equilibria.
- Fresh reviewer ongoing; output figure checked, y-axis padding adjusted for label readability.

## Review and resolution
- Fresh reviewer independently verified all saved mass balances, direct/bridge counts, role duplication, year-state alignment, and source receipts; no numerical/code errors.
- Fixed Important scientific scope: F-only and joint refuge are indistinguishable in frog hazard only under FSD clamp, not universally. Dynamic counterexample H=.420072 versus.431171 explicitly added; F-clamped.374461 versus.384097. S predation is a useful discriminator, not the only possible measurement.
- Regraded bridge wording as scientific-scope correction rather than deferred polish: zero OS in matched-season grid applies to edge-on. Added explicit qualifier in plan/report; full table retains edge-off success.
- FigureS3 visually inspected and axis padded; source/draft links checked. Frozen source remains unchanged. No deferred new findings.
- Task complete: deterministic interventions and adaptive bridge, conditional predictions, manuscript/gate updates,168tests/894snapshot, reviewed scientific wording. NEE remains unmet.
