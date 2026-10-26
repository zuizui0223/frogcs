# Multiyear Stage Network Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline, with one fresh whole-change review at the end.

**Goal:** Close annual density feedback in the existing synthetic three-guild model and test reversal, third-party, vegetation and immigration effects.

**Architecture:** Preserve the seasonal kernel with optional input cohorts. A separate annual driver maintains maturation queues, applies bounded recruitment and records trajectories. A plotting/report layer presents matched contrasts and sensitivity.

**Tech Stack:** Python3.10, numpy2.2.6, pandas2.3.3, matplotlib3.10.8.

**Spec:** research/manuscript/MULTIYEAR_STAGE_NETWORK_DESIGN_2026-10-26.md

## Constraints and review focus

- Preserve the 894-file frozen snapshot and existing numerical seasonal results.
- No fitted ecological rates, calling conversion, forced sign or equilibrium claims.
- Audit off-by-one maturation, absent-guild immigration, initial-history transients, unequal scenario matches, and temporal discretization.

## Tasks

- [x] Add failing tests for arbitrary seasonal input, mass balance and compatibility; implement optional initial cohorts.
- [x] Add failing annual tests for delay/zero-return/absence/bounds; implement annual queue and outputs.
- [x] Execute all864 primary scenarios, all-role sensitivity, half-step and horizon160 checks; save matched results.
- [x] Create and visually inspect figures; write Japanese interpretation and English manuscript paragraphs.
- [ ] Fresh review, full tests, original replay/snapshot checks, CI replay and draft PR update; export deliverables.

## Ledger

Design choices are authorized implementation details of the user's approved extension. Existing draft branch is suitable and reused. No graphify graph exists; source files provide the implementation evidence.

RED→GREEN: optional input API failed before implementation; annual module absent before implementation; duplicate pairing test failed before rejection was added. All87 tests now pass. All7 old numerical seasonal tables replay exactly, and the894-file frozen snapshot verifies. Full annual rerun reproduced every original table exactly. Fresh source review found no recurrence blocker; requested preservation of all sensitivity arms is implemented as13 summary/trajectory pairs. Figures inspected. Half-step maximum final-window mean-density discrepancy0.00891 (all-role subset); report explicitly avoids universal convergence or equilibrium claims. CI and PR handoff pending.
