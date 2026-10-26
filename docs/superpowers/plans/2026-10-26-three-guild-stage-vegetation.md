# Three-guild stage vegetation implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement task-by-task.

**Goal:** Deliver a tested, reproducible stage/vegetation scenario model and manuscript discussion.
**Architecture:** New cohort model with simultaneous hazard updates, paired edge removals and isolated outputs.
**Tech Stack:** Python, numpy, pandas, matplotlib, unittest; existing environment.
**Spec:** research/manuscript/STAGE_VEGETATION_MODEL_DESIGN_2026-10-26.md

## Global constraints

Keep frozen payload unchanged; use arbitrary parameters transparently; no fit to empirical signs;
no claims of population coexistence or same-year adult calling caused by later larval survival.

## Review focus

Mass accounting at births, emergence and drying; predator absent but cues still active; unobserved edges;
off-grid event times; emergence benefit incorrectly feeding back into prior larval dynamics.

## Tasks

- [x] Add failing invariant/ablation tests in research/scripts/test_stage_vegetation_network.py.
- [x] Implement research/scripts/stage_vegetation_network.py with simulate(parameters, dt) returning all cohort endpoints and death ledgers.
- [x] Run tests, fixed factorial, edge removals, drying and half-step comparisons; save all results in research/results/stage_vegetation_network_20261026/.
- [x] Draw and visually inspect a figure showing phase/vegetation contexts and both positive/negative effects.
- [x] Write manuscript discussion and methods connecting observed patterns, independent literature and explicitly synthetic findings.
- [x] Independently review model/claims, verify original snapshot hashes, run relevant regression tests, save deliverables and commit.

## Execution ledger

User explicitly expanded the ongoing manuscript task to simulation improvement. Proceed inline with the
specified scenario design; no additional model fitting or raw-source acquisition is needed.

Final audit: 70 tests passed; all 894 frozen payload files verified. Independent scientific/code review corrected the multiplicative-survival null and explicitly bounded the exclusively antagonistic model and unimplemented S cue-release pathway. All reported scenario counts and illustrative values were independently checked against CSV/JSON.
