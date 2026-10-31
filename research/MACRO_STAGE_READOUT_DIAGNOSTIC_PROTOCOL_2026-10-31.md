# Post-result life-stage readout test — macro scenario selection (2026-10-31)

**Purpose:** Investigate whether the absence of a robust macro explanation in PR #146 partly reflects using the wrong biological output of a fixed multi-year model. This is an **exploratory, post-result comparison**; all previous negative results remain authoritative. No additional ABM/PDE, mechanism parameter fitting, or favorable outcome selection.

## Biological readouts

The unchanged `stage_network_extension_20261029.simulate` computes three aquatic-guild seasonal completions; `extension_annual_summary_20261029` propagates those completions into **next year's** cohort stock via a fixed two-year F maturation delay. The 80-year model currently stores mean `F_B` (preseason cohort) and mean `F_fraction` (within-season completion fraction) but **not** mean `F_C` (completed metamorph cohort). They are not interchangeable:

- `F_B`: mean of year-start aquatic frog cohort stock over years 61–80; **original endpoint** and exact replay anchor.
- `F_C`: mean of within-season completed frog cohorts over the **same years**. The correct mean is `mean(B_t × fraction_t)`, not `mean(B_t) × mean(fraction_t)`. This is a *potential future recruitment input*, **not mature singing male abundance**.
- `F_fraction`: mean within-season frog aquatic completion fraction; a survival-like response, not a density or call-rate estimate.

For diagnosis, report year-endpoint standard deviation and the actual covariance `mean(B_t*fraction_t)-mean(B_t)*mean(fraction_t)`. In a stationary long-run summary, **a uniform temporal lag cannot be learned from last-20-year means alone**. Never claim a specific 1/2-year lag from this comparison.

## Exact source and replay gate

Use the archived `research/results/literature_extension_20261029/design.csv`, restricted to the **same 24 existing cases** in PR #146 (3 context × baseline/shared_both × risk off/on × frog reverse off/on). Re-evaluate the unmodified stage kernel and same annual recurrence at 80 years, dt=.25, 2×9×9 source grid. Fixed stage durations/growth, attack .5, rho .75, return, conversion 4 and initial/source cohorts **identical** to the archived extension calculations.

**Fail closed** unless recomputed per-cell `F_B`, `F_fraction` and `F_B_sd` agree with the pinned original `primary_{0,1}_dynamic_cells.csv.gz` to 1e-9. Do not use reconstructed endpoints or report scenario selection if this replay fails.

## Same empirical validation design

Run the original 4,248-site, 63,180-visit nested spatial validation with *exactly* the same 5 outer and 3 inner blocks, two SDM backgrounds, 24 scenarios, additive and full OS/OV/SV/OSV environmental nulls and ridge-binomial observation operator. For the two **new** post-hoc readouts independently, replace only the mechanism feature:

- `log(F_C)` for seasonal completed cohorts (potential recruitment).
- `logit(F_fraction)` clipped at 1e-6 and 1-1e-6 for survival probability.

Select cases only on the *inner* folds for each new outcome family; evaluate the outer holdouts. Keep `F_B` results exactly as previously reported; do not reclassify the new outcomes as preregistered findings. Distinguish four questions: (i) which stage readout predicts better; (ii) if the same model dominates both backgrounds; (iii) do candidate gains beat **both** environmental nulls in both backgrounds; (iv) do observed OV and OS directions match predicted heldout patterns?

**Decision:** The first analysis remains `NO_EMPIRICALLY_SUPPORTED_WINNER`. Only label an alternative readout as *exploratory predictive lead* if it improves over the stronger null and keeps OV/OS compatible without claiming causal stage calibration. Any negative result remains a substantive diagnosis.

## Independent observations and limit

The available 44 green-toad pond-days show calling vs manually counted males but fail to establish transferable NAAMP density calibration. The Alpine 73-pond dataset contains adult/nonadult guild counts but **no frog calling**; neither can provide a joint time- and pond-matched `F_C→adult chorus` regression. INBO's 245 same-location/year adult-to-larval records likewise do not directly measure cohort completion, reproductive adults or density. No cross-source pseudoreplication or invented calibration.

This PR must not modify `main`, PR #144, PR #145, original published-source tables or frozen kernels. Store exact numeric outputs, source SHA receipts, tests and failures in PR #146.
