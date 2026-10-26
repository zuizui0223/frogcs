# Source-gradient implementation plan

Goal: Test whether annual feedback can generate negative S modification of the D-source gradient without fitting to NAAMP.

Design: Add optional n-by-3 source_cohorts to simulate_years, replacing only I in external input (1-rho)*(1-survival)*I. Initial B remains unchanged. Default I=presence must exactly preserve prior results. Seasonal hazards remain unchanged.

- [x] Test default replay, independent source mass balance at rho=0, zero influence at rho=1, absent guild and invalid inputs.
- [x] Implement source input and record source values only when supplied.
- [x] Run fixed grid: S,D external supply each .25/1/2; F=1; rho=.5; 80 years, last20 mean. Vegetation roles 0/15/14/13/11/7 (none/all/each of four roles removed), vegetation0/1, refuge S/D, F arrival10/30/50. Kernel variants full/no_reverse/no_cue/no_intraguild/independent. Compute endpoint D slope, modification at S2 minus S.25 on raw and log F_B and F_C; all intermediate doses retained. This is not a calling model or SDM score.
- [x] Validate dt .125 and horizon160 on all-role subset. Sensitivity: rho .25/.75; conversion2/8; delay1/1/1 and3/3/2 on all-role subset. Retain null and positive results; do not infer mechanism necessity from a joint cue ablation alone.
- [x] Report all scenarios, phase-specific deaths and trajectory summaries; update paper discussion, export results, and verify frozen snapshot. Mark achieved only when run and limitations documented.

Acceptance: deterministic replay, finite bounded populations, complete matched contrasts, explicit sensitivity scope, no claim of empirical identification. Independent raw response can contain demographic/scale interactions: only seasonal fixed-input log null has exact zero expectation.

Ruling after primary results: add joint-sign checks (high-S D slope negative AND modification negative), and exploratory adjacent-dose checks on both stored intervals, all contexts. The primary full-range test fails; do not substitute the selected upper-range success for it. No new model fit or parameter tuning.

Review: source-gradient reviewer confirmed source manipulation/contrasts and identified implicit NaN booleans in the runner. Defaults are now explicit; prior boolean kernel arrays and complete fixed primary replay agree. Six new tests, nine previous annual tests, twelve seasonal tests pass. Old 864-scenario annual summary replays and macro snapshot894 verifies. Half-step and160-season numerical checks complete; population-demographic dependence reported. Figure inspected visually.

Outputs: research/manuscript/SOURCE_GRADIENT_RESULTS_2026-10-26.md and research/results/source_gradient_20261026/. Manuscript updated, report and figure exported to task outputs. All planned work complete.
