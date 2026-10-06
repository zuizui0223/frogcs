# Final pre-submission audit corrections — 2026-10-05

## Scope

This receipt records the final factual, figure, provenance-language and anonymous-review corrections made immediately before initial submission. No scientific endpoint, fitted coefficient, null simulation or analysis population was recomputed or retuned.

## Corrected factual inconsistency in Figure 2

The earlier legend/annotation incorrectly stated that marginal depths 1–3 lay within both activation-null envelopes.

The frozen figure data show:

- depths 1–3 lie within the uniform-activation 95% envelope;
- relative to the persistence-preserving null, depths 1–2 lie below its two-sided 95% envelope;
- depth 3 lies within both envelopes;
- depths 4–10 exceed the upper 95% envelope under both nulls.

The manuscript Results, Discussion, Figure 2 legend, renderer and current claim/novelty records were corrected accordingly.

The second-stop statement is now explicitly tied to the prespecified **upper-tail** criterion: it did not exceed the upper 95% range under either null, although it lies below the two-sided persistence-preserving envelope.

## Figure redesign

All manuscript-style “Fig. N …” titles were removed from the image panels; titles remain in the manuscript legends.

- Figure 1 now uses point estimates throughout rather than mixing bars and points. The frozen figure data contain 95% CIs only for the direct CI3 endpoints, so those intervals are shown without inventing intervals for the decomposition-only quantities.
- Figure 2 retains the two null envelopes and now carries the corrected shallow/deep annotation.
- Figure 3 was redesigned around the inferential quantity: observed conditional residuals are shown against their simulated 95% null-residual intervals. The principal residual is 0.297 versus −0.132 to 0.119; the held-out rain × history residual is 0.318 versus −0.117 to 0.126.
- Figures 4–5 retain their existing inferential content, without manuscript-style figure titles inside the images.

The figure workflow now verifies deterministic rendering on pull requests and synchronizes generated PNG/SVG files automatically after renderer changes reach main.

## Supporting Information language cleanup

Reader-facing SI prose no longer uses “endpoint readback”.

Internal contract/QC filenames were removed from the analysis prose and consolidated into a single repository-provenance table (Table S18), preserving auditability without forcing readers through internal file naming.

Exact project dates were removed from the reader-facing provenance narrative where the biological/inferential sequence was sufficient.

## Cover letter

The cover letter now:

- reports the Monte Carlo result as **P ≈ 0.001**, noting that this is the minimum attainable with 1,000 simulations;
- replaces “developed post-opening” with “developed after the initial analyses were inspected”;
- adds the monitoring implication: median specieswise SE inflation **1.61-fold** and pooled route-clustered SE inflation **2.69-fold**;
- remains below the 500-word limit.

## Anonymous reviewer code

The submission pipeline now builds an identity-scanned `Reviewer_Code.zip` containing the main analysis scripts, frozen specifications, selected receipts and deterministic figure inputs without Git history.

The manuscript Data Availability statement now states that an anonymized code bundle accompanies the submission for peer review. The final public code/derived-analysis archive remains planned for Zenodo.

## Reference spelling check

The suggested change from **Kanenko** to **Kaneko** was **not made**.

The British Herpetological Society publication page and the original 1999 paper both list the third author of *Breeding site fidelity in the Japanese toad, Bufo japonicus formosus* as **Shigenori Kanenko**. The manuscript reference is therefore retained as:

> Kusano, T., Maruyama, K., & Kanenko, S. (1999).

## Remaining boundary

These corrections change presentation and factual description of already-frozen outputs only. They do not reopen NAAMP analysis, WFTS work, landscape exploration or any outcome-driven model selection.
