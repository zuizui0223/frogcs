# Submission handoff — JAE RC11 release

## State

- parent baseline: RC10 retained at `release/jae-v1-rc10`
- merged reviewer-defense PR: #54
- canonical manuscript: `MANUSCRIPT_JAE_V1_3.md`
- canonical SI: `SUPPORTING_INFORMATION_JAE_RC11_V0_1.md`
- current authority: `main` / `release/jae-v1-rc11` / `submission/jae-v1`
- RC10 files remain unchanged as audit history.

## What RC11 changes

1. Adds an explicit Limitations boundary: the current null uses one common activation shift, and a species-specific activation-shift null remains untested.
2. Uses the public NAAMP `ObserverTrackingID` field to test observer turnover directly.
3. Restricts to 3,152 same-observer matched pairs (74.4% of all pairs) and reruns the three headline responses plus the four-component uniform and persistence-preserving null comparisons.
4. Adds the complete same-observer method and results to SI.

## Outcome

The prefrozen classification is **observer robust**. All three headline coefficients remain positive with 95% confidence intervals above zero. Boundary crossing is 92.0% in the same-observer subset and lies above the 95% intervals of both primary nulls. Uniform-activation and persistence-preserving four-component omnibus tests both give Monte Carlo P=0.001.

## Deliberately not done

The species-specific activation null was not run. It remains a clearly identified revision reserve if a reviewer asks whether species-level response heterogeneity alone can reproduce the boundary allocation.

## Compliance

RC11 initial-submission QA passes:
- combined manuscript + title-page proxy: 7,403 / 8,500 words
- abstract: 317 / 350 words
- anonymous cover: 368 / 500 words
- required structural/anonymization checks: PASS

## Authoritative RC11 files

- `MANUSCRIPT_JAE_V1_3.md`
- `SUPPORTING_INFORMATION_JAE_RC11_V0_1.md`
- `submission/RC11_STORY_FREEZE_V0_1.json`
- `NAAMP_SAME_OBSERVER_ROBUSTNESS_CONTRACT_V0_1.json`
- `NAAMP_SAME_OBSERVER_ROBUSTNESS_SUMMARY_V0_1.json`
- `submission/NOVELTY_AUDIT_V0_11.md`
- `submission/REVIEWER_ATTACK_MATRIX_V0_11.md`
- `submission/JAE_PORTAL_CHECKLIST_V0_10.md`

Administrative author/title-page/archive fields remain human-completion items.
