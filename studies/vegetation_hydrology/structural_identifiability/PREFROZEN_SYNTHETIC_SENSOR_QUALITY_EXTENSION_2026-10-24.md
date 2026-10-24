# Prespecified synthetic observation-quality design extension — 2026-10-24
New simulation-only appendix, written **before** comparing hypothetical observation-quality outcomes. Does not use any real frog calling records or refit previously reported NAAMP ecological coefficients.

All other parameters remain those of `PREREADBACK_SYNTHETIC_PROTOCOL_2026-10-24.md`: exact 333 real-NLCD route habitats, k=3 and k=5, gamma=1.5, 80 simulations × 2 occasions, RNG 2840223, conditional exact-k placement.

Three illustrative, assumed (NOT empirically estimated) instruments are compared:
1. `remote_low_under_canopy`: sensitivity open-water 0.90, vegetated wetland 0.12, other 0.55; specificity 0.98, route-month complete visibility 0.79.
2. `improved_all_habitats`: sensitivity 0.90 for all three mapped habitat categories; specificity 0.98, route-month complete visibility 0.79.
3. `local_near_direct`: sensitivity 0.99 for all categories, specificity 0.99, route-month complete visibility 0.95.

The **same latent-water RNG stream** and exact true distributions are used where possible to isolate instrument-quality effects. Compare mean expected exact-k log-score gain recovered relative to the true-water oracle on the *same simulated visible route-occasions*. These are design illustrations and do not estimate JRC classification skill, field-monitoring accuracy, confidence intervals for amphibian ecology, or field sample-size/power guarantees. Record negative gains if any; no tuning of assumed thresholds in response to findings.

Practical aim: determine whether improving measurement of *vegetated* and small ephemeral breeding-water states can in principle recover information hidden from a coarse open-water product. The rank-identified field target remains event-dated, site-varying water changes with explicit sound/detection controls.
