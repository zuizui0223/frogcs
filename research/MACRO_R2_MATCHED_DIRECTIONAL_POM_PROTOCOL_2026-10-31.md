# Acoustic-SNR-matched direction-only POM: frozen comparison protocol (2026-10-31)

## Primary question
Do the archived 132 frozen models, the **8 genuine 80-year rate draws × 24 structural variants**, or the separate **3 neutral/moderate/strong S-facilitated-danger settings ×24 cases** generate the observed OS−, OV−, high-S-minus-low-S O/calling correlation ΔS−, vegetation-positive-minus-zero ΔV−, **and low-S O/calling correlation near zero** when their response is observed with the same total rank-regression signal-to-noise level as NAAMP?

This is **post hoc** to the model failures seen in the same 4,248 NAAMP sites, not independent validation. Neither matching one summary R² nor matching sign patterns warrants a biological ABC posterior.

## A mathematical issue that must be tested rather than hidden

Adding the same noise to `rank(F_B)` *cannot recover absolute effect sizes already discarded by ranking*. If two source surfaces have identical ranks, their rank-plus-noise distributions remain identical no matter whether one has a 1% and another a 50% cohort response. **A per-scenario R² calibration also erases any strictly affine signal-scale difference.** Therefore evaluate two explicit, fixed observational representations in all three source families:
1. **rank_signal** (requested primary): globally standardized `rank(F_B)` plus Gaussian site noise, followed by global ranking for exactly the same 8-term rank regression and pattern summaries.
2. **log_signal** (sensitivity): raw `log(F_B)` plus Gaussian noise in log-cohort units, followed by global ranking. This retains differences in signal spacing, although per-scenario calibration to one R² still cannot identify a purely global scaling effect. It does **not** posit a biologically calibrated count-to-call function.

No negative observation slopes and no selection of a favorable link after seeing sign scores. These two representations are compared side-by-side; the user-requested `rank_signal` is primary.

## Exactly fixed R² calibration (not a fit to the direction patterns)

- Observed: `R²_obs = 1−SSE/TSS` of **unadjusted pooled rank OLS** of globally ranked observed strong-call frequency on intercept, O, S, V, OS, OV, SV, OSV at the original 4,248 NAAMP sites. Report both SDM backgrounds. This is a descriptive site-level R², not a visit-level calling detection model or an independent measurement of acoustic error variance.
- For **each exact simulated surface** and background, use the existing predictor-only rank-to-9×9-grid mapping, V as positive/zero 3-km remote landscape flooded vegetation, and observed spatial site distribution.
- Fix the **same 16 Gaussian innovation fields** for every candidate within each background during calibration (drawn independently of observed calls and sign patterns). On a 0–32 positive noise scale, compute the *mean over these 16 fields* of the same globally ranked 8-term OLS R² after noise addition; find the noise SD with bisection (18 steps, relative target 0.01, absolute target 0.002).
- If unperturbed source R² is **already below** the observed R², no nonnegative additional noise can make the output more explanatory in the intended attenuation interpretation: record `NOISE_ONLY_R2_UNREACHABLE`, retain sigma=0 **without pretending it matched**. If the high-noise value is still too high, fail closed with explicit `NOT_BRACKETED` rather than silently treating the model as calibrated. Output the achieved calibration R² and mismatch.
- Evaluate **128 new, independently seeded** Gaussian innovation fields per candidate/background, with the same evaluation field IDs across all cases. Their sign/zero frequencies and mean R² must be saved. Zero disturbance is never silently re-fitted to force observed OS or ΔS signs.
- **Predefined sensitivity**: one separate 0.25 block-correlated plus site-noise innovation ensemble for calibration/evaluation, not a proven NAAMP noise decomposition; use the exact same calibration and directional score gates. Distinguish the iid case as primary. If running both noise structures, report all without favorable post hoc selection.

## Fixed directional comparison and outcomes

- Use the **existing same-block 999 observed-bootstrap** of OS, OV, ΔS, ΔV. Select binary directions at ≥90% bootstrap frequency. In the previous fixed cohort all four were negative at ≥90% in both backgrounds, but re-check their exact point and classification from the input.
- Use the *same observed source's* low-S O/calling correlation (rank correlation; median S suitability split) and same 999-block bootstrap to declare a **ternary negative / near-zero / positive state**. Zero band `delta=max(0.05, observed 95% interval half width)`, frozen from observation only, **never candidate dependent**. Preserve original low-S probability masses.
- Score **joint five-category agreement** against the same observed-block draws, without multiplying five independent likelihoods or treating the scores as a biological posterior. Report probability of a complete simulated five-pattern match to the *observed modal categorical vector*, agreement with observed-bootstrap joint vector, and mean mismatches; soft penalty 0.25 per mismatch.
- A success requires **the low-S near-zero AND all four eligible directions to occur in one simulated noisy replicate**. Report complete-match frequency (0/128 distinct from e.g. 12/128) and sample support; positive frequency is conditional on the chosen observation-noise model.
- Preserve all candidate models, no result-based scenario pruning. For fixed 132, group byte-identical F_B source surfaces (104 groups, equal prior source-group weight in any aggregations); the 192 and danger-replay catalogs must be treated separately, with labels and parameters retained.
- Include **unselected** four pattern diagnostics (V-zero O correlation, V-positive O correlation, within-route OS and OV) for top candidate *after* selecting by the five directional components. These are summaries of the SAME sites, not independent external confirmation.
- Report the **observed-category chance baseline** from the empirical joint categorical resampling, and clearly mark an independent uniform 2^(-K)/3 combinatorial benchmark as illustrative only, **not a null-model p value**.

## Input and integration gates

Use original freeze-controlled GitHub files for the 132 F_B surfaces and same 4,248 site ledger. Download **successful** source artifacts, without re-simulating or re-tuning their biological parameters:
- [Original eight-rate actual 80-year simulation #41163370575](https://github.com/zuizui0223/frogcs/actions/runs/41163370575), `real_simulator_F_B_cells.csv.gz`, 8×24×162 cells and source SHA receipt.
- [Actual 80-year S-facilitated danger hypothesis #41164886106](https://github.com/zuizui0223/frogcs/actions/runs/41164886106), `hypothetical_80year_F_B_cells.csv.gz`, 3×24×162 cells and source SHA receipt.

Run a source-integrity smoke test (complete grid, 132/192/72 configurations, 104 exact frozen groups, nonnegative finite F_B and distinct artifact run receipts); then a full-site test. No original kernels or PR #144/#145 edits.

## Interpretation and stop criteria

- **If matching achievable R² changes all-sign/zero alignment**, record specifically which model cases, source groups, noise choices and backgrounds reproduce those observations. This supports *observation-model sensitivity*, not proof of the proposed facilitation mechanism.
- **If all calibrated models still fail**, distinguish genuinely R²-matched failures from `NOISE_ONLY_R2_UNREACHABLE`, where the test cannot adjudicate.
- **If iid and block-correlated results disagree**, report dependence on the unmeasured residual correlation structure rather than select the favorable result.
- For any candidate to count as a **stable descriptive lead**, require support in both SDM backgrounds and both signal representations, plus that observed low-S near-zero is not achieved solely because the nonpositive low-S effect has been erased along with other strong directions.
- Genuine ecological ABC needs independent field or literature distributions for demographic rates, stage-to-adult/chorus observation and residual spatial dependence. **No pseudo-posterior fractions as probability of the real mechanism.**

This is a **post-outcome methodological sensitivity** under a selected R² noise model; the previously archived direction-only and quantitative POM tests remain unchanged.
