# NAAMP 2° residual block correlation → R²-matched directional POM (2026-10-31)

## Goal

The user wants to advance the ecological programme after separating the established deterministic 120-day season + 80-year recruitment dynamics from a *hypothetical* site acoustic observation process. The main open methodological sensitivity is that the previous R²-matched POM obtained very different complete-category matching frequencies for **iid Gaussian** and a chosen **0.25 block-Gaussian amplitude**.

**Run a same-estimand NAAMP residual spatial-structure audit and rerun the frozen 132 / genuine 192 / speculative 72 source catalogs with that structure.** Do not retune trophic parameters or independently uncalibrated stage→adult conversion. The original 2° route-centroid blocks and source cohort (4,248 sites, 63,180 strong-call surveys, 56 blocks) remain unchanged.

This is an **observational-process sensitivity after inspecting the prior 0.25 results**, not untouched validation. It must not be presented as proof of a trophic interaction.

## Residual covariance estimand

For each of uniform and target-group SDM inputs, fit the **same original unweighted 8-column rank OLS** on site-level strong-call rate: `rank(strong rate) ~ 1 + O + S + V + OS + OV + SV + OSV`. Compute e_i=standardized rank Y_i−OLS fitted rank Y_i; model R² is separately verified to the previous exact targets 0.046994388... and 0.051772116....

Using the **same 2° spatial blocks** as the POM and outer CV, compute one-way unequal-size method-of-moments between-block residual variance:
`n0=(N−Σ n_b²/N)/(B−1)`;
`MS_B=Σ n_b(ē_b−ē)²/(B−1)`;
`MS_W=Σ_{b,i}(e_i−ē_b)²/(N−B)`;
`τ²=max((MS_B−MS_W)/n0,0)`;
`σ²=MS_W`;
`ICC=τ²/(τ²+σ²)`.
Also compute the analogous route-level ICC (sensitivity to listening-route dependence). If ICC=1 and σ²=0, the corresponding Gaussian generator is undefined; fail closed.

For 999 uncertainty replicates, resample **whole blocks with replacement**; each resampled block is treated as a *new pseudo-block* with its own group label and identical sufficient statistics, rather than merging identical original labels. Recompute ICC without refitting OLS and label it a **conditional block bootstrap**. Keep 95% interval and the fraction of raw between/within variance differences ≤0. Report block sizes, number of routes, route ICC, OLS residual variance, original R², and `a=√[ICC/(1−ICC)]` for an iid unit-variance site innovation plus shared Gaussian block effect. The previous arbitrary a=0.25 corresponds to ICC≈0.058824, not a value observed independently.

### Scientific caution

This is the **spatial correlation of the observed residual from a specific rank regression**, not pure detection noise. It could reflect unmeasured habitat, species composition, geography, sampling routes/observers, or true biology. It cannot independently calibrate the NAAMP detection mechanism and does not identify which predator/prey stage caused calling. Fitting R² **and** residual ICC from the same observed response are descriptive moment matches, not an external model likelihood or biological ABC posterior.

## Simulation sensitivity

- Fix the source-based **132 fixed model cases (104 identical-source groups)**, **192 genuine original seasonal/annual 80-year rate draws (128 source groups)** and **72 S-facilitated hazard hypothesis cells (48 source groups)**. Reuse the successful original archived real-simulator outputs, not a new parameter search.
- For each background separately, set the random-field amplitude to the observed rank-residual ICC estimate of that background; `Z_{site}=N(0,1) + a × N_{block}(0,1)` and standardize per random field exactly as before. This choice is made *before* evaluating any POM signs and is identical across candidate surfaces within a background.
- Preserve the same two signal representations `rank(F_B)` and `log(F_B)`, 16 separate fixed noise fields for *per-source full 8-term R²* matching and 128 independent evaluation fields.
- Score the **same five fixed joint observed patterns**: OS−, OV−, high-S−low-S O/call association ΔS−, V-positive−V-zero O/call association ΔV−, and low-S O/call correlation near zero. Preserve the 999 observed spatial-block bootstrap and fixed low-S observed-only near-zero band. Do not select patterns to favor a candidate.
- Flag every R²-unreachable or unmatched source; rank only the R²-matched groups. Compare all source groups and both SDM backgrounds. The resulting model groups and modal complete frequencies are **conditionally compatible with rank residual ICC**, not established as true field predator mechanisms.
- Report each family’s overlap between the two SDM backgrounds and the comparison with the iid and arbitrary 0.25-block previous results, and do not interpret the three noise structures as independent studies. If the empirical residual ICC implies a materially different result, show the sensitivity rather than choose a favorable alternative.
- Test exact regression R² replay, residual orthogonality, unequal-group ICC, block-resampling, iid generator limit when ICC=0, source-group duplicate invariance, full 132/192/72 catalog completeness, and old source SHA receipts. Capture all outputs and historical inputs' SHA256 in Actions artifacts; commit concise summary CSVs and a clear result report.

**Decision ceiling**: empirical residual correlation can narrow a *descriptive noise scenario*; it cannot independently calibrate aquatic F_B→adult call nor provide an ecological scenario posterior. An absent robust directional model is still a real negative result under tested assumptions; a positive conditional match is not field causation.

Do not edit original season/annual kernels, `main`, PR #144 or #145, or past frozen result files.
