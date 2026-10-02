# Method literature grounding v0.1

## Purpose

Document what parts of the RC4 spatial-depth/concentration method are established ecological practice, what parts are study-specific, and which interpretations are not authorized.

## 1. Counting sites per taxon

Established precedent:
- McGeoch & Gaston (2002), *Biological Reviews* 77:311–331, DOI 10.1017/S1464793101005887: occupancy-frequency distributions summarize how many sampled areas are occupied by each species and emphasize the effects of grain, extent, coverage and sampling intensity.
- Jenkins (2011), *Global Ecology and Biogeography* 20:486–497, DOI 10.1111/j.1466-8238.2010.00617.x: ranked species occupancy curves begin by counting the number of study sites at which each species was observed.

RC4 use:
- for each taxon acoustically absent from all ten drier-survey stops but detected calling in the wetter survey, k is the number of wetter-survey stops with a calling record;
- mathematically this is a row-wise site-incidence count;
- biologically it is **calling-incidence depth**, not confirmed physical occupancy, arrival, colonization, dispersal or movement.

## 2. Constrained incidence-matrix null models

Established precedent:
- Gotelli (2000), *Ecology* 81:2606–2621, DOI 10.1890/0012-9658(2000)081[2606:NMAOSC]2.0.CO;2: presence–absence matrix structure is tested against null matrices; results depend on which row/column properties are fixed, proportional or equiprobable.
- Gotelli & McCabe (2002), *Ecology* 83:2091–2096, DOI 10.1890/0012-9658(2002)083[2091:SCOAMA]2.0.CO;2: large-scale application of constrained null-model analysis to published presence–absence matrices.
- Dormann et al. (2009), *The Open Ecology Journal* 2:7–24, DOI 10.2174/1874213000902010007: ecological network indices can depend strongly on network dimensions, connectance and sampling intensity; comparison with null expectations is needed to distinguish structural inevitability from additional organization.

RC4 use:
- pair-level total wet calling incidence is magnitude matched;
- increasingly structured nulls then preserve dry-state persistence, route-cross-fitted taxon rainfall response, strictly-prior taxon × physical-SiteID probabilities and, in the strongest sensitivity, a held-out rain × history gate;
- the inferential claim is always relative to the information preserved by the comparator.

## 3. Simple spread versus within-taxon concentration

Let k_i be the number of calling-positive wetter-survey stops for acoustically route-new taxon i.

Simple extent:
- total sites: sum k_i;
- extra spread: E = sum(k_i-1).

Ordinary within-taxon site-pair count:
- P = sum choose(k_i,2).

RC4 residualized concentration:
- C = sum choose(k_i-1,2).

Exact identity:
- choose(k,2) = choose(k-1,2) + (k-1);
- therefore P = C + E.

Consequences:
- C is **not claimed to be a standard named ecological index**;
- it is a study-specific algebraic residualization of an ordinary pair count;
- once E is conditioned on, C and P contain the same residual concentration information;
- the role of C is to ask how a fixed amount of multi-site calling is allocated among taxa, not how much calling spread occurred.

Example:
- allocations (2,2) and (3,1) across two taxa both have N=2 taxa, K=4 incidences and E=2 extra incidences;
- P is 2 versus 3 and C is 0 versus 1;
- the latter arrangement has more within-taxon concentration despite identical total incidence and extra spread.

## 4. Exact-depth shape

The post-freeze exact-depth audit fixes marginal j-th-stop participation before readback.

Observed result:
- marginal depths 1–3 remain within both primary activation-null envelopes;
- marginal depths 4–10 exceed both;
- observed marginal coefficients decline with depth rather than increase.

Authorized interpretation:
- **heavier/deeper within-taxon calling-incidence tail than expected**.

Not authorized:
- a biological threshold at exactly the third stop;
- exponential increase with site number;
- movement or arrival at successive stops;
- simultaneous acoustic coordination among stops.

## 5. Geometry boundary

C and P use only k and ignore which physical stops are involved:
- stops {1,2,3} and {1,5,10} have the same k=3 contribution.

Therefore:
- C tests concentration across taxa conditional on amount of spread;
- route adjacency is a separate secondary analysis;
- historical SiteID targeting is a separate recurrence analysis.

## Recommended manuscript language

Prefer:
> We treated the number of calling-positive stops per taxon as calling-incidence depth, analogous mathematically to site-incidence summaries in occupancy-frequency analysis but without interpreting acoustic zeros as physical absence.

Prefer:
> We compared within-taxon site-pair concentration with increasingly constrained incidence-matrix null models, following the general null-model principle that inference depends on which first-order matrix properties are preserved.

Prefer:
> The study-specific score C = sum choose(k_i-1,2) is the ordinary within-taxon site-pair count minus total extra-stop spread; after conditioning on extra spread it isolates allocation of calling incidences among taxa.

Avoid:
- standard concentration index;
- occupancy expansion;
- species reaching later stops;
- colonization of route stops;
- movement across the route;
- third-stop threshold;
- exponential spatial activation.
