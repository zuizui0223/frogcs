# Macro-first endogenous 2×2×2 POM + biological-rate ABC (2026-10-31)

## Current goal and observational authority

The *primary* question is now **which ontogenetic trophic network STRUCTURE produces the four observed pre-environmental-adjustment sign patterns** in `main`: `OS−, OV−, SV+, OSV+`. Use only these four. Do **not** require low-S acoustic correlation≈0, route-scale site patterns, a fitted acoustic link, SDM rank transport or a 4,248-site joint distribution in this workstream. Those were different post hoc observation exercises and remain archived separately.

Authoritative main source: `research/results/final_mechanism_20261027/macro_targets.csv`. Uniform pooled coefficients: OS −0.16559 (95% [−0.22940,−0.10756]), OV −0.08750 ([−0.12418,−0.04778]), SV +0.05834 ([+0.01529,+0.10135]), OSV +0.03704 ([+0.00789,+0.06805]). Target-group point signs identical, but SV +0.04638 ([−0.02202,+0.10898]) and OSV +0.02730 ([−0.02378,+0.07302]) cross zero. Therefore four target signs are **the user-selected uniform-main biological target**, not four independently robust empirical facts in both SDM constructions.

## Simulator and 12 structural groups

Use the **unchanged original** `stage_network_extension_20261029.simulate` seasonal trophic kernel and `extension_annual_summary_20261029` annual delayed-recruitment equation. Main horizon **80 years**, last **20 years** mean of `F_B` (frog aquatic start-of-season population), 120 days each year and `dt=0.25`. This is actual deterministic demographic simulation, not post hoc perturbation of frozen F_B grid, not ABM/PDE, and F_B is **not observed calling adult males**.

Model factorial: O (D source) low/high = **0.25 / 2.0**, S source low/high = **0.25 / 2.0**, vegetation V=0/1; all **eight corners equally weighted**. Do **not** map the model corners onto actual NAAMP sites.

Structural class = 3 stage-timing/size trajectories (`original`, `D_first_S_overtakes`, `S_first_D_overtakes`) × 2 feeding-time handling variants (`baseline`, `shared_both`) × 2 behavioral refuge switches (`risk=False/True`) = **12 classes**. Within each structural class include **both** original `dynamic` and `frog_reverse` adult-frog→emerging-dragonfly switches as paired `edge` nuisance states (prior 1:1); **never claim they are universally identical before checking actual drawn signs**. Same parameter vectors shared across all 12×2 structures to reduce Monte Carlo imbalance, but report effective independent draw count separately.

## Four contrasts — fixed biological response scale

For y(v,s,o)=`log(F_B)`, define O effect (E_O(v,s)=y(v,s,1)-y(v,s,0)) and S effect (E_S(v,o)=y(v,1,o)-y(v,0,o)). Then
- `OS = mean_v[E_O(v,1)-E_O(v,0)]`
- `OV = mean_s[E_O(1,s)-E_O(0,s)]`
- `SV = mean_o[E_S(1,o)-E_S(0,o)]`
- `OSV = [E_O(1,1)-E_O(1,0)] - [E_O(0,1)-E_O(0,0)]`.

**Primary = log(F_B)** because proportional demographic changes are relevant; **raw F_B** is prespecified sensitivity. Three-way and higher-order signs can change by response scale, so do not merge log and raw results or choose a favorite after viewing. Require nonzero contrast above 1e-10; zero is a distinct state, not randomly assigned a sign.

## Phases, no after-the-fact success target

**Phase A (deterministic POM):** calculate the four exact contrasts at the eight corners for all 24 source `dynamic/frog_reverse` cases in the frozen 80-year `literature_extension_20261029` outputs; group 12 classes, report exact 4-sign matches and edge-toggled equality. This establishes the scale and factorial orientation and is an actual reproducible first result.

**Phase B (real parameter draws):** sample **128 independent exploratory multivariate rate draws** using a fixed, reproducible 7-dimensional Latin hypercube, applied identically to every structural class and to both reversal switches (256 scenario/draw combinations per structural class; 3,072 structure×rate×edge configurations; 24,576 factorial cells). The *actual 80-year simulator* runs for every draw and each of 8 corners. This is not an archival-response warp or an eight-draw toy posterior. Individual continuous draws: attack scale log-uniform 0.25–1.0; S,D growth multipliers uniform 0.75–1.25; rho 0.55–0.90; conversion 2–6; F juvenile survival .60–.90; F adult survival .25–.60; F maturation time 2 or 3 years balanced. All numeric ranges are **exploratory synthetic bounds, not literature-calibrated prior distributions**. Other guild rates and seasonal hazard logic remain unchanged. For computational tractability, a new vectorized annual accounting path accepts per-row biological parameters and must replay `summarize_years` and the frozen source numerical endpoint at baseline to <=1e-8 before any ABC interpretation.

## ABC inference and diagnostics

**Primary is exact-rejection ABC on the FOUR discrete sign summaries**, since the observed target contains only 4 bits and the rank-coded summary has only at most 16 nonzero patterns. For class g:

`accept_g = (1/(2×128)) Σ_{draw,edge} I[(sign OS,sign OV,sign SV,sign OSV)=(-,-,+,+)]`.

Under equal class priors and the specifically declared **exploratory parameter/edge distributions**, `π_g^ABC = accept_g / Σ_h accept_h` is an **approximate conditional model probability**, NOT a calibrated empirical probability of a causal trophic mechanism. If all counts are zero, the class posterior is undefined and must not be fabricated. Quantify uncertainty by resampling 128 **entire prior draw IDs shared across all classes and both edge variants**, not treating 3,072 responses as independent. For every class, save acceptance counts, rates and 95% conditional bootstrap intervals. Save distributions of attack, growth, rho, conversion, juvenile/adult survival, maturation time in the accepted vs *same-class original prior draws* to reveal which ecological parameter conditions yield the target pattern; require adequate effective acceptance before interpretation.

**Secondary ABC-RF**: because ONLY four signs are supplied, a classifier cannot create more independent information than the exact 16 patterns. Use grouped out-of-fold 4-way CV by **shared prior draw ID**, RandomForestClassifier, confusions and class recovery. Report out-of-fold error for the actual 12 structural labels, naive majority baseline 1/12 and any exact-signature ambiguity. An ABC-RF accuracy/correctness probability is computed only with a separately trained OOF error regressor if implementation supports it; *never call raw vote share posterior*. Compare RF ranking with exact ABC; no claim that RF produces true probability from four bits. Original potential source: Pudlo et al. (2016), *Bioinformatics*, ABC model choice via RF.

**Null:** the often-quoted `1/16` chance of reproducing four signs applies ONLY if those signs are **independent and equiprobable random coin flips**; it is a combinatorial orientation reference, not a calibrated ecological null or p-value. If a null comparison is required, retain the actual synthetic prior-predictive sign frequencies instead of treating 1/16 as a test.

**Pseudo recovery:** across held-out shared parameter draw IDs, report exact 12-structural-class confusion. If the four bits fail to distinguish the classes, group equivalent 4-bit distributions and state the limit. Compare edge-ON/OFF sign identity per paired rate draw; merge only if output equality for the assessed summaries is substantiated. Report both log/raw sensitivity.

## Preserve positive and negative evidence

Existing NAAMP positive results are **observational**: rain-driven silent→strong chorus, intermediate multi-site organization (β1.650 vs null1.353, conditional excess+.297, p.000999), recurrent taxon-specific site use (β+.151 CI .129–.173), and strong-site historical +27.68 points in fixed site comparisons; weak negative Odonata suitability–call correlation (ρ−.095/−.086) and context-dependent OS/OV negative. None proves actual larval predation. Published predator reversal and risk-mediated third-party effects support biological *possibility* in specific species; simulated outcomes are model-conditional findings. Do not elevate untested S-facilitated D→F amplification to an observed effect.

Do not overwrite existing POM, R²-noise, observational CV, ABM/PDE pilots or their negative results. The original `main` and PRs #144/#145 must remain unmodified; PR #146 is Draft. Record exact source hashes, full draws, all 4-bit outputs and failures; save concise durable CSVs/interpretation plus full CI artifacts.
