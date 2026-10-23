# Locked post-readback descriptive follow-up: source of the PEM–frog richness surplus

Date 2026-10-23. Added after the real P×W architectural interaction was examined and found non-confirmatory: 499-route within-night category interaction beta_any=+0.02891 (95% route CI −0.04951 to +0.10734; two-call-test BH q=0.50019), beta_strong=+0.01980 (95% CI −0.03785 to +0.07745; q=0.50019). Existing positive, adjusted PEM category contrasts remain beta_any=+0.20460 without woody and +0.23351 with woody; strong +0.12737 and +0.14717. This extra analysis is **retrospective ecological accounting**, not an independent experiment, preregistered test, or forecast.

## Question

At a station already mapped as wetland, is the PEM-associated positive calling taxon unit count more strongly attributable to **(A) at least one taxon being heard**, or **(B) additional taxa detected beyond the first at an already active stop**? This is a question about levels of acoustic metacommunity organization, not direct social interactions or obligate habitat selection.

## Exact no-new-fitting architecture

Reuse unchanged analytical sample and design in exploration/run_naamp_pem_woody_architecture_hierarchy_v0_1.py: the same 57,821 wetland-mapped NAAMP site×night rows, 6,236 complete 10-stop source runs, 499 physical routes and 20 states, within-night fixed-effects and fixed 16 covariates. The existing fitted response types for each CI>=1 and CI>=2:
- Y = number of detected NAAMP taxon units at stop;
- A = 1 if Y>=1, otherwise 0;
- M = max(Y−1,0) = # acoustic taxon units beyond the first.

Identity Y=A+M is true at **every stop**, so every OLS linear coefficient and all linear contrasts must satisfy beta_Y=beta_A+beta_M, including:
1. PEM contrast when woody mapped 0: beta_P;
2. PEM contrast when woody mapped 1: beta_P+beta_PW;
3. Woody contrast when PEM mapped 0: beta_W;
4. Woody contrast when PEM mapped 1: beta_W+beta_PW;
5. P×W nonadditivity beta_PW.

Add these **descriptive component contrasts** and route- and State-clustered CIs to the source aggregate output. Verify the exact identity to 1e-9 for all contrasts and the original interaction P/BH values are unchanged. Report ratios beta_A/beta_Y and beta_M/beta_Y ONLY when beta_Y!=0 and label ratio as signed algebraic contribution (can exceed 100% due to cancellation, not variance or causal fractions).

No new BH families, unregistered p-value searches, label filtering, habitat radius changes, source-year subsetting or treating repeated stops as independent biology. Count+activation+multi-taxon outcomes are statistically dependent accounting decompositions; only the original two predeclared P×W interaction tests have formal BH interpretation.

Any pattern in acoustic detection is not measured occupancy, animal abundance, birth, frog-frog facilitation or trait-mediated species interactions. USFWS NWI polygons are not time-matched aquatic macrophyte observations. JAE RC6 and main are untouched.
