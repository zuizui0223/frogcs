# Complete G7 species-group vegetation test and simplify the integrated manuscript

**Draft review package; publication authorized on 6 November 2026.**

Base: `editorial/p1-g6-review-package-20261106`.
Head: `research/g7-developmental-trait-bridge-20261106`.
Keep Draft; do not merge or send a journal submission as part of this action.

## Why this change

The integrated P1/G4–G6 manuscript still lacked the proposed species-trait follow-up, and its Abstract described the field–model comparison in opaque language. G7 completes a fixed comparison and carries the result into the manuscript without changing earlier model findings.

## What this PR changes

- Freeze the literature qualification and exact comparison before new acoustic fits (`21fda6b3`), then freeze the tested implementation before the real run (`be77b4c4`). Ordinary larval durations overlap, so the main contrast is two tiger salamanders versus two other Ambystoma, with the aquatic newt separate. The user-proposed two-versus-three grouping remains a fixed sensitivity.
- Reuse all 4,248 original sites, 63,180 visits and 56 geographical blocks. Preserve the original SDMs, five folds and ridge value. Save every coefficient, bootstrap draw, held-out prediction, support check and receipt.
- Integrate G7 into main text, Supplement S3e/Table S3f/Figure S2, references, cover letter and entry points. Replace the Abstract's opaque predictive-compatibility phrase with plain English. Current complete main file: **4,981 words**; Abstract: **133 words**.
- Include the already verified reference/provenance update on top of the original frozen-source review package.

## Result and interpretation

The primary vegetation×species-group coefficient was positive but uncertain: uniform **+0.067 [−0.142,+0.319]**; target group **+0.028 [−0.214,+0.267]**. Incremental held-out NLL gains per visit were **−0.000196** and **−0.001100**, with both intervals spanning zero. All support checks passed. All **3,996 coefficient refits** and **40 held-out training fits** converged. The fixed pooled-newt sensitivity did not alter the decision.

The positive-association and predictive-improvement criteria were unmet. The suitability contrast does not measure local larval duration or arrival order and cannot directly validate or falsify P1's joint early-arrival×long-duration mechanism. No post-result regrouping or additional association search was performed. Prior positive R1–R4/P1 results and G4–G6 inference limits remain intact.

## Verification

- **192 research tests passed**, including 15 G7 behavioral tests.
- All **44 existing manuscript numerical claims** were freshly recomputed from the frozen inputs and passed; manuscript structure and word-count checks passed.
- Independent calculation reproduced four coefficient intervals, eight NLL/Brier scores and four paired prediction comparisons. Independently optimized primary coefficients differed by no more than **4.4×10⁻¹²**.
- P1 main Methods/Results and Supplement S8–S9 remain byte-identical to the pre-edit text; all four original main figure PNGs retain their hashes.
- All **117 relative links** checked resolve. The new scientific figure was visually reviewed.
- Existing rasterio/Affine deprecation warnings occurred in the full suite; there were no test failures. Candidate-bearing CSVs should be read with `keep_default_na=False` because `null` is a literal model label.

Evidence: [G7 report](../research/G7_TRAIT_COMPOSITION_RESULT_2026-11-06.md), [protocol](../research/G7_TRAIT_INFORMED_COMPOSITION_PROTOCOL_2026-11-06.md), [independent validation](../research/results/g7_trait_composition_20261106/G7_independent_validation.json), [editorial validation](../research/results/g7_trait_composition_20261106/G7_editorial_validation.json).

## Publication scope

The user explicitly authorized sending this completed branch to `zuizui0223/frogcs` and creating a Draft PR on 6 November 2026. This package is ready for review; merging and journal submission are outside this publication action.
