# Post-readback NPS strict-history sensitivity: weak prior sites vs strong prior sites

Defined on 2026-10-25 **after reading the primary NPS +0.464 result**. This is clearly a post-hoc mechanism clarification and cannot be promoted as a prespecified independent confirmatory test.

## Diagnostic question

Does historic strong-chorus targeting still predict strong calling if the comparator is limited to locations where the same frog species was *at least once acoustically detected* in earlier years (only CallingIndex 1), rather than sites with no prior recorded call?

Fixed source: NPS GLKN 2016–2023 public CSV DOI 10.57830/2320505; SHA256 b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2. Primary contract: [NPS_GLKN_STRICT_HISTORY_HYDROPERIOD_CONTRACT_V0_1.md](NPS_GLKN_STRICT_HISTORY_HYDROPERIOD_CONTRACT_V0_1.md).

## Stage-2 eligibility and thresholds

- Each current site×species×year must have at least one earlier-year scored recording **and** at least one prior call CI≥1 for that same species.
- `prior_strong=0`: maximum **earlier-year** CI was 1 (previously heard but never strong).
- `prior_strong=1`: at least one earlier-year CI≥2.
- Current outcome: annual CI≥2, prespecified by primary.
- Within exact park×species×current-year groups retain at least four site observations and prior_strong variation, otherwise exclude. Report all sample losses / number informative groups and site-year/species coverage.
- Repeat unadjusted and adjusted group-FE comparison using same prior-other-species general site hotness, permanent/semi-permanent/ephemeral hydroperiod and current/prior recordings. Cluster bootstrap park×species trajectories, 2000 draws.
- Robustness: leave each of seven parks out entirely using the **primary** informative annual panel. Do not fit a new model chosen based on park outcomes. Optionally restrict current site-year observations to ≥10 manual species-scored recordings, with eligibility recomputed and missing declared.
- If weak-vs-strong is unestimable, say so and do not collapse non-detections to weak chorus.
- As before, historical same-taxon calling might reflect unmeasured species×wetland suitability; **no individual memory, direct interactions, plant refuge or rainfall-specific selection is identified**.
