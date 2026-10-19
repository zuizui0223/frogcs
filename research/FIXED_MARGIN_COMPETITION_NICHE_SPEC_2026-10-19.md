# Frozen-before-readback research plan — frog acoustic assemblage segregation after rain (2026-10-19)

**Separate exploratory extension.** The frozen Journal of Animal Ecology manuscript, `main`, and its primary within-taxon spatial concentration (C) are outside this test. Motivated by the user's request to revisit competition and niche partitioning after prior non-support for simple multispecies co-calling and pairwise Sørensen change. This is **not independent replication or a preregistered hypothesis**. The following comparison, thresholds and algorithm are committed BEFORE viewing this extension's NAAMP association endpoints.

## Ecological question

At the same species-specific number of calling stops and site-specific number of calling species, do species arrange themselves more segregated than a fixed-margin random assembly would predict, and does the departure from that expectation differ between paired survey runs nearer to versus farther from rain?

- A nonrandom pattern is a candidate signature of **site-specific habitat preferences, acoustic detection, or biotic interactions**, not a direct estimate of interspecific competition, fitness effects, resource-use niche width, or mating success.
- A 10-stop route is sampled sequentially, so taxa detected at different stops are NOT synchronized callers at a single instant. A joint record at one stop only means both taxa were detected during the same stop-level observation.
- The fixed row totals retain each taxon's spatial breadth; fixed column totals retain site richness. Crucially **total multispecies co-detections \(\sum_j {c_j\choose 2}\) is algebraically fixed**, so it must NOT be used as the primary statistic. What can vary is the allocation of pair identities and repeated pair-specific separation across sites.

## Authoritative source and population

Same SHA256-pinned public NAAMP `Runs.csv`, `Stops.csv`, `Counts.csv` and eligibility functions at current main SHA `0871da0c97d97e2a20156e75fda738d708c82883`. Preserve 2001–2015 UnifiedProtocol, ten-stop eligible runs, CallingIndex 1–3 as detected. Never impute missing stops or reclassify an operational species complex as verified species.

Re-use existing `build_runs`, `pair_runs` and `stop_matrix` to generate the **same 4,236 paired route-season survey comparisons** (585 routes, 21 states). The "wet" and "dry" names mean **nearer and farther from recorded rain**; they do not establish chronological before/after.

At each run, construct taxon ×10-StopNumber binary detection matrix using every detected operational taxon. Fixed individual matrix eligibility: **at least three acoustically detected taxa**, plus nondegenerate random-assembly variation in the C-score below. Do not select taxa by their effects or cut the data to make associations significant. Report counts of excluded runs and pair reasons. Hard feasibility gate: at least **200 full informative wet–dry pairs from ≥80 routes**, and for year-gap-exactly-one robustness at least **75 pairs from ≥40 routes**. If the gate fails, report nonestimable and stop; do not relax.

## Fixed-margin null model

Represent each detected taxon as a ten-bit StopNumber incidence mask. Randomize the taxon ×stop incidence matrix using a **Curveball row trade**. For two taxon rows, independently redistribute the exclusive stop locations while retaining each taxon's row sum and each stop's column sum. This realizes the Strona et al. (2014) fixed–fixed binary null (DOI 10.1038/ncomms5114), appropriate for co-occurrence inference.

Use TWO deterministic independent PRNG chains per run, each with **128 samples**, **20×max(3,number of taxa)** initial trades and **10×max(3,number of taxa)** trades between samples. Base seed `20261019`, combined with SHA256 of RunID and chain index. With a known reference binary matrix, test row/column invariance after each series, reproducibility, and that the summed overlap \(\sum_{i<j} O_{ij}\) is invariant. Report null Monte Carlo chain disagreement and nonestimable matrices; no adaptive burn-in/sample count or cherry-picked time windows.

Per-run statistic (mean C-score over pairs of detected taxa):
\[
C = \frac{2}{m(m-1)}\sum_{i<j} (r_i-o_{ij})(r_j-o_{ij}),
\]
where \(r_i\) is species i's number of calling stops and \(o_{ij}\) is the number of sites shared by i and j. More positive \(C\) means larger incidence checkerboards, but is **not a direct measure of competitive exclusion**. Define null-centered segregation \(E=C_{observed}-mean(C_{null})\). If null simulation SD for a matrix ≤1e−10, classify the run as structurally uninformative and exclude **both its paired values** from the inferential analysis, retaining the exclusion count.

## Main and secondary contrasts

**PRIMARY:** For informative matched pairs, \(\Delta E=E_{nearer-rain}-E_{farther-rain}\). Calculate the **route-equal mean of within-route pair means** and a 95% route bootstrap CI using 2,000 resamples (seed 20261020); two-sided paired sign/bootstrap evaluation. A positive value indicates increased *degree-adjusted checkerboard segregation* nearer rain, a negative value reduced segregation. The expected difference under the within-run fixed-margin null is zero; a null bootstrap interval including zero does not show equivalence.

**SECONDARY pre-named:** OLS of \(\Delta E\) against `rain_contrast + temp_difference + doy_difference + year_gap + C(State)+C(RunNumber)`, with route-cluster CR1. A negative slope suggests relaxation of assemblage segregation with greater contrast; a positive slope suggests strengthening. Preserve all numerical outcomes even if primary negative.

**Sensitivity without selection:** 1) Only exact-consecutive-year comparisons; 2) same physical SiteIDs for each pair and same observer where available; 3) two independently initialized null chains' estimates of the PRIMARY on identical pair supports. If one chain's estimate has a sign or magnitude far beyond sampling CI from the other, report Monte Carlo instability, do not increase draws after effect inspection.

**Biological interpretation and stop rules:** No inference about male calling frequency, within-site calling overlap timing, direct competition, resource utilization, or breeding success. A supported segregation residual is consistent with either unmeasured environmental/habitat filtering OR acoustic/biotic interactions. An unsupported wet–dry segregation difference does NOT prove absence of competition or exact equivalence. Strong evidence of competition requires within-night call-rate/temporal niche shifts, acoustic playback, or manipulation on independently recorded simultaneous species ×site time-series. No species-pair-specific post hoc claims without new independent holdout.

Save per-run C-score/null mean/null SD/chain means and matched-pair analysis CSV (aggregate run/pair metadata only; no observer identities, coordinates), source pins, all conclusions and software versions as downloadable CI artifacts. Record observed positive and negative results. No `main` merge or JAE scientific reopen.

**Previous distinct findings used only to motivate, not claimed as test replication:** activity-conditioned multispecies OR≈0.988 P=.402 under an older model, paired local alpha β≈+0.0794, and essentially unchanged pairwise Sørensen slope (practical equivalence). These metrics use different denominators/conditioning; do not treat one as contradicting the others.

Methods context: [Strona et al. 2014](https://www.nature.com/articles/ncomms5114) and [Gotelli 2000](https://doi.org/10.1890/0012-9658(2000)081[2606:NMAOSC]2.0.CO;2).
