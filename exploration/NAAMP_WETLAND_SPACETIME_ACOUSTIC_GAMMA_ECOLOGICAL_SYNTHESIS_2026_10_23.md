# NAAMP: vegetation-associated frog communities accumulate more taxa through seasonal re-observation than additional site coverage

**2026-10-23, executed source-backed nonpredictive macroecology.** Source: original USGS NAAMP 2001–2015 frog acoustic index records × response-blind USFWS NWI 250-m mapped wetland/emergent polygons. These are mapped environmental classes, NOT time-matched observations of live aquatic plants. Study is **exploratory post-hoc**, continuing previous positive PEM one-round and seasonal gamma results on the SAME archive; not a separate field replication. No literature research or predictive forecasting; original JAE RC6 paper, SI, and main remain frozen.

## New supported, specific ecological result

**The larger seasonal acoustic taxon pool at mapped emergent-wetland (PEM) stations relative to other mapped-wetland stations is associated chiefly with repeated observations through survey rounds, rather than a specifically larger spatial accumulation gain from surveying one additional physical site.** This is a *community sampling hierarchy*, not evidence plants cause frog-frog interactions.

Previous 2–5-site whole-round study documented **PEM−other two-round temporal bonus +0.12780 taxa (CI≥1)** under route/State/BH gates, with species label contributions concentrated in multiple *Lithobates* taxa. This new analysis asks a DIFFERENT question: compare **exactly 1 vs 2 distinct fixed physical sites × exactly 1 vs 2 different source-year survey rounds**, holding those effort dimensions identically across PEM and other mapped wetlands. Distinguish a spatial increment, temporal increment and their non-additive cross difference with exact arithmetic.

### Strictly original and fully aligned source hierarchy

- 7,848 original normalized source 10-stop NAAMP runs, 6,236 NWI/stop-environment complete runs; 5,147 mapped NWI source-only physical SiteIDs (12 audited shards, Actions #39450277196).
- Reuses **exactly 2,869 repeat survey rounds**, **1,115 same physical route×calendar-year groups**, **274 physically distinct monitoring routes and 20 States**; all source ten-stop SiteIDs and their NWI class identities are identical within the same route-year. Other-wetland comparison has mapped total NWI wetland, not guaranteed absence of actual vegetation.
- Use every **2,475 unordered pair of actual observed seasonal rounds**, average each route-year's `R choose 2` combinations before giving each whole physical route equal inferential weight.
- For each vegetation group and route-year, m=2 **physical SiteIDs chosen once for both seasonal rounds**, and the same two survey rounds are used in PEM and other wetland groups. Calculate **exact expectation over all two-site subsets** using the frozen hypergeometric formula. Original source taxon labels/complexes and acoustic zeros included.
- Four expected observation-scale incidence gamma quantities:
  - `G11` one site, one of two rounds.
  - `G21` two different sites, one round.
  - `G12` same site, two rounds pooled.
  - `G22` same two physical sites, two rounds pooled.
- Exact identity: `G22 = G11 + S + T + I`, where `S=G21−G11` spatial added taxa, `T=G12−G11` seasonal added taxa from same site, and `I=G22−G21−G12+G11` a signed space×season observation cross-difference. The `I` term **is not biological synergy** and can be nonzero even with completely independent animal detections.

Source-free mathematical QA passed: brute-force all possible two-site combinations and two seasonal rounds for distinct toy acoustic incidence matrices, including both positive and negative `I`, completely silent matrices, persistent labels; original source QA passed.

### Exact route-balanced ecological decomposition (CI≥1, all calls)

| Source ecological layer | Mapped PEM | Other mapped wetland | PEM − other |
|---|---:|---:|---:|
| One physical site × one round: `G11` | 1.65937 | 1.38579 | **+0.27357** |
| Two sites × one round: `G21` | 2.31095 | 2.01406 | +0.29690 |
| One site × two rounds: `G12` | 2.85305 | 2.41754 | **+0.43551** |
| Two sites × two rounds: `G22` | **3.88583** | **3.44405** | **+0.44178** |
| **Spatial increment S** (G21−G11) | +0.65158 | +0.62826 | **+0.02332** |
| **Seasonal increment T** (G12−G11) | +1.19368 | +1.03175 | **+0.16193** |
| Space×season cross component I | +0.38120 | +0.39825 | **−0.01705** |

Here all four source-stratified expected taxon pools are calculated under the same 2-site, 2-round incidence expectation framework, including actual zero acoustic detections. Cross terms are usually positive within each habitat under the non-additive species accumulation identity, but their *difference* does not imply a causal plant×species synergy. The expected PEM two-site/two-round pool advantage **+0.44178** decomposes algebraically as **+0.27357 baseline +0.02332 spatial +0.16193 seasonal −0.01705 cross**. These percentages can be expressed as ~61.9% baseline acoustic pool, ~5.3% spatial increment, ~36.7% seasonal increment and ~−3.9% signed cross correction, **not causal proportions or variance explained**.

### Six frozen two-sided ecological component tests

Cluster at 274 **physical routes**, not 2,475 round pairs or 10-stop records; each route-year gets one averaged value first. Student route-t(df=273) 95% intervals, independent-route Rademacher sign flips (4,999 draws), 20-State confidence intervals and omit-one-State diagnostic; **BH across six pre-readback S/T/I × 2 calling strength tests**.

| PEM−other effect | CI≥1 beta (95% route CI) | CI≥1 BH q | CI≥2 beta (95% route CI) | CI≥2 BH q | Robust result |
|---|---:|---:|---:|---:|---|
| **Seasonal increment ΔT** | **+0.16193** (+0.12465 to +0.19921) | **5.32×10⁻¹⁵** | **+0.12291** (+0.09357 to +0.15225) | **2.08×10⁻¹⁴** | **Positive supported** |
| Spatial increment ΔS | +0.02332 (−0.00175 to +0.04839) | 0.10218 | +0.02083 (+0.00075 to +0.04091) | 0.08428 | Not robust |
| **Space×season ΔI (primary)** | **−0.01705** (−0.03728 to +0.00319) | **0.11808** | +0.00596 (−0.01145 to +0.02338) | 0.50093 | **Not supported** |

The supported **ΔT_any** route sign-flip p=.0002 and 20-State CI **+0.10799 to +0.21694** agree with positive temporal increment, and 18/20 States had positive mean effects. **ΔT_strong** sign-flip p=.0002, 20-State CI +0.06958 to +0.19242 and 18/20 State mean effects positive. The apparent CI≥2 spatial ΔS nominal route P=.042 is NOT supported after pre-frozen six-test FDR (q=.084) and State-level uncertainty.

**Primary prereadback `ΔI_any` did not pass** route CI, BH or State criteria, so overall primary result classification is `no_robust_PEM_specific_space_time_accumulation_cross_difference`. Treat ΔT as a supported **secondary** ecological component, explicitly distinguished from a successful primary interaction hypothesis. No new taxon/route/radius/season selection was done to move a P value below threshold.

### What the result adds to the ecological hierarchy

1. **Habitat and local community size:** earlier NWI PEM positive matched acoustic alpha, +0.23777 taxon units/stop after simultaneous mapped habitat, wetland area, temperature and noise control.
2. **Single-round area-matched gamma:** earlier mapped PEM+ within wetland acoustic taxon pool +0.29837 versus mapped nonPEM, across 281 routes.
3. **Two-round acoustic complementarity:** previous +0.12780 absolute seasonal bonus beyond average single-round two-to-five-station gamma, many taxa contributing but *Lithobates* genus heavily represented; a separate descriptive analysis did NOT show a higher proportional bonus `B/G_two` in PEM.
4. **NEW 2×2 space-time accumulation:** expected **+0.16193 more additional taxon units from sampling another round at exactly the same physical site** in PEM relative to other wetlands (274 routes, 20 States). **No supported differential spatial gain or additional space×season interaction.**
5. **Longitudinal anchoring:** previous 2,403 exact physical-station interannual year-pairs had positive site-specific acoustic taxon re-detection beyond wetland-category-constrained spatial swaps in both PEM and nonPEM habitats, no PEM advantage; adjusted year-gap decay test nonsupported.
6. **Interaction caution:** neither these sampling-scale gamma components, previous fixed-margin PEM-specific dyadic co-detection nor original third-order acoustic motifs identify direct plant–frog, frog–frog, aquatic fish/insect mediating or irreducible three-species biological interactions.

**Nontrivial ecological interpretation:** *PEM mapped wetland contexts contain more frog acoustic taxon labels observable across the same breeding-season survey visits because seasonally complementary calling records add taxa at a fixed physical station, rather than because a PEM site necessarily yields more new taxa merely from moving to another stop.* This pattern is consistent with environmental differences in acoustic phenology or detection, but cannot identify the source mechanism from NAAMP+NWI alone. The **spatial-versus-seasonal gamma accumulation comparison is within a fixed source geography**: no model forecasts, no new experiment, no exact contemporaneous botanical or aquatic vegetation identity.

## Immutable calculation and audit

- Outcome-before-readback fixed spec `exploration/NAAMP_WETLAND_SPACETIME_ACOUSTIC_GAMMA_SPEC_2026_10_23.md`.
- Reproducible Python source `exploration/run_naamp_wetland_spacetime_accumulation_v0_1.py`.
- Scientific computation actually finished on [Actions #39909317997](https://github.com/zuizui0223/frogcs/actions/runs/39909317997), with original full result [artifact #12482680088](https://github.com/zuizui0223/frogcs/actions/runs/39909317997/artifacts/12482680088). The run's overall GitHub conclusion shows `failure` because the very last validation script used a **wrong JSON field name** (`matched_physical_sites_same_m_across_both_rounds` instead of the actual `same_fixed_2_site_m_for_both_vegetation_classes`). Complete scientific run and mathematical synthetic QA both succeeded. Validation path was corrected without altering outcome/statistic or deleting prior failed audit evidence.
- Immutable numerical source output versioned: `exploration/NAAMP_WETLAND_SPACETIME_ACOUSTIC_GAMMA_AGGREGATE_2026_10_23.json`.
- Full original artifact downloaded and **independently cross-checked** against versioned results; all six coefficients, route/State intervals, raw sample counts, exact four-gamma source accounting and original NWI/NAAMP gates passed: [Actions #39909729800](https://github.com/zuizui0223/frogcs/actions/runs/39909729800) **SUCCESS**. This is source-artifact integrity validation, NOT independent biological replication.
- All files on exploration/naamp-wetland-spacetime-accumulation-2026-10-23; frozen `main` RC6 manuscript, SI, submission and release remain unchanged; raw USGS/USFWS site-level records were not committed.
