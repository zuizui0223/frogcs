# Refuge indirect-benefit generality investigation

**Goal:** Test the user-approved conceptual novelty and generality claim without new field measurement. NEE remains aspirational, not a predetermined outcome.
**Spec:** Prior response accepted by user: primary literature, alternative response/refuge targets, existing-data discriminatory predictions.
**Execution:** Inline using existing research Python pipeline; research-skill agents audit primary literature/data; fresh review at end.

## Fixed design before outcomes
- Preserve all old kernels. New copied kernel changes only D functional-response family/density scale and explicitly common F refuge strength; replay original when options omitted.
- Five D hazard families normalized at F=1: constant, fixedII, fixedIII, vegetation mixII/III, vegetation mixII/III with high-density exponent3. No claim that this family spans all possible feeding laws.
- Nine vegetation pathways: no direct function, F protected from S, F protected from D, F protected from both, S protected from D, D protected from S, D attack support, D emergence survival, F-from-S plus S-from-D. Response vegetation dependency is a separate factor, so no-direct-function is not no-vegetation under mixed response.
- Primary F refuge/attack coefficient .25 (same coefficient across recipient pathways); emergence survival uses original.8 coefficient. Two S handling forms FF-only and all shared; D handling0. Three previously fixed stage contexts. Edge D->S on/off; S=0 truly absent via FD community, otherwise S source .25/2; D source .25/2; V0/1. Total6480 scenario cells per timestep. No chosen winning subset.
- Primarydt.25 and full half-stepdt.125,80years last20. Record all H and F_B. Secondary density/refuge scale K=.5/1/2 and refuge .25/.5/.75 in reference stage/F-from-S and S-present, both handling/edge settings; report separately from primary.
- Main mechanistic contrast: DS-edge contribution to OV = OV(edge on)-OV(edge off), separately low/high S and S absence. Also record total OV/OS/SV and density-conditioned null, avoiding rank/hazard equivalence.
- Existing data: same4248 sites, both backgrounds. Estimate OV contrasts at low/high continuous S from full OSV regression, plus lowest/highest S-third subset fits with support diagnostics. A low suitability site is not salamander absence. Existing cohort, outcome-selected hypothesis: not independent causal validation. Contrasts must include covariance; report intervals and failures.
- Literature audit can conclude mechanism already known. Model robustness cannot by itself close calling-density calibration or field causal gap.

## Tasks
- [x] Tests: old kernel replay, normalization, noS edge invariance, response-scaled accounting.
- [x] Primary and secondary simulations, timestep verification, complete failure catalogue.
- [x] Existing-data prediction comparison and identifiability audit.
- [x] Primary-source novelty verdict, report/figures/manuscript, source hashes, tests, PR144 update.

## Execution record
- Primary6480 and secondary1440 cells completed at both dt=.25/.125;18/270 and38/90 edge-on joint hazard directions, none edge-off. Full failed conditions retained.
-161 unit tests passed;894-file frozen snapshot verified; baseline reference replay exact at both timesteps. All passing configurations stable under timestep halving;10 individual primary contrasts change sign.
- Existing4248-site conditional OV comparison completed with999 block resamples, all high-low intervals include0. External91 plotted points are not complete126 trial data.
- Ruling: do not fit external plotted points as independent complete trials; incomplete multiplicities would bias fitting. Cost: no new experimental parameter calibration.
- Ruling: no new density-clamp intervention; retained existing analytic density boundary and explicit edge-removal controls, and report this limitation. Cost: do not claim intervention-level isolation of the density feedback beyond existing analysis.
- Primary-source review finds prior art for habitat-modified intraguild predation; no first/new-principle claim.
- SupplementfiguresS1/S2 visually inspected; no need to change original frozen paper.
- Fresh read-only reviewer completed: kernel/role controls, saved grid arithmetic, joint macro covariance and claim boundaries checked. Significant P2 cache provenance issue identified; reproducing test failed before fix, passed after. Two cache safeguards increase full suite to163 passing. Full simulation rerun completed; all8 cell files byte-identical; validated cache reuse completed.

- Final review scope: additions since0da1d82, not a full branch or primary-literature re-audit. Reviewer independently confirmed999/999 valid draws for all four macro comparisons.
- Final: minor (deferred): save valid bootstrap draw counts in machine-readable receipt; current999/999 were independently verified, but the extra field was not added.
- Final: fixed cache provenance mismatch — missing-provenance test RED→GREEN; checks also reject changed demography and altered output; full suite163/163.

Task complete: source audit, fixed simulations, internal empirical comparison, manuscript, figures,163 tests,894-file snapshot, source hashes, and final review fix. NEE readiness remains false.
