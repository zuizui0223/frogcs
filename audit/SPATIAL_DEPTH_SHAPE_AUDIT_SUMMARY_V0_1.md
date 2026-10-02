# Spatial-depth shape audit summary v0.1

## Question

Does the frozen NAAMP spatial-depth result imply a biological threshold at the third occupied stop, an exponential increase with depth, or a deeper-than-expected multi-site tail?

## Frozen population

- 4,236 wetter-drier matched NAAMP comparisons.
- Same residualized rainfall design as the frozen spatial-depth analysis.
- 1,000 simulations under:
  - uniform activation (kappa=2);
  - persistence-preserving activation (a=0.75).

This audit was fixed before the exact k=1..10 depth profile was read.

## Main result

There is **no discontinuity at the third occupied stop**.

Marginal j-th-stop rainfall coefficients decrease smoothly with depth:

| j-th occupied stop | observed beta | uniform-null mean | persistence-null mean | Above both 95% nulls? |
|---:|---:|---:|---:|:---:|
| 1 | 0.1847 | 0.1754 | 0.2665 | no |
| 2 | 0.1317 | 0.1332 | 0.1859 | no |
| 3 | 0.1097 | 0.0997 | 0.1092 | no |
| 4 | 0.0934 | 0.0718 | 0.0595 | **yes** |
| 5 | 0.0811 | 0.0506 | 0.0314 | **yes** |
| 6 | 0.0699 | 0.0347 | 0.0162 | **yes** |
| 7 | 0.0485 | 0.0229 | 0.0078 | **yes** |
| 8 | 0.0368 | 0.0143 | 0.0033 | **yes** |
| 9 | 0.0235 | 0.0080 | 0.0011 | **yes** |
| 10 | 0.0096 | 0.0034 | 0.0002 | **yes** |

The third-stop marginal coefficient is:
- observed beta = 0.109746;
- uniform-null mean = 0.099749, upper-tail p = 0.177;
- persistence-null mean = 0.109232, upper-tail p = 0.484.

Thus the earlier significant cumulative third-plus endpoint is significant because it sums a **deep tail**, especially fourth through tenth occupied stops. It should not be described as a threshold at exactly three stops.

## Is the increase exponential?

No exponential shape was tested or supported.

Observed marginal j-th-stop coefficients actually **decline** with depth. What changes is their relation to the null expectation: null models decline much faster. Therefore the empirical pattern is best described as a **heavier/deeper multi-site tail than expected**, not exponential growth with stop number.

## What does simple site counting show?

Simple extent measures are already positive:

- total route-new occupied sites beta = **0.7890**;
- extra-stop beta, sum(k-1) = **0.6043**;
- cumulative third-plus beta, sum max(k-2,0) = **0.4726**.

All exceed both primary nulls.

These measures answer **how much spatial spread occurred**, but not **how the same total spread was allocated among taxa**.

Example with two recruited taxa and four total occupied sites:

- allocation (2,2): both taxa occupy two sites;
- allocation (3,1): one taxon occupies three sites, the other one site.

Both have:
- N=2 recruited taxa;
- K=4 total incidences;
- extra stops K-N=2.

But the second allocation is more concentrated within one taxon.

## Why use H = sum choose(k-1,2)?

For one taxon:

| k occupied stops | H=choose(k-1,2) |
|---:|---:|
| 1 | 0 |
| 2 | 0 |
| 3 | 1 |
| 4 | 3 |
| 5 | 6 |
| 6 | 10 |
| 7 | 15 |
| 8 | 21 |
| 9 | 28 |
| 10 | 36 |

This is **quadratic/triangular**, not exponential.

More importantly, it has an exact identity with the standard within-taxon site-pair count:

`choose(k,2) = choose(k-1,2) + (k-1)`.

Summed across recruited taxa:

`P = H + extra_stop`.

Therefore, once extra-stop spread is conditioned on—as it is in the principal comparator—H contains the same concentration information as the standard pair-count statistic P. H simply subtracts the first-order spread term so that ordinary one- and two-site participation contributes zero.

Observed coefficients verify the identity:
- H beta = **1.5240**;
- extra-stop beta = **0.6043**;
- standard pair-count P beta = **2.1283**;
- H + extra = 2.1283 = P.

## Ecological meaning

The simple count says:

> Recent-rain surveys contain more route-new taxon-site incidences.

The concentration statistic asks a different question:

> Given how many taxa were recruited and how much total extra-site spread occurred, are those extra incidences distributed roughly independently among taxa, or do they cluster within the same taxa?

The observed excess supports the latter.

This is evidence for **distributed within-taxon expression across many separated route stops**, beyond the amount of spread alone. It does not identify:
- direct acoustic coordination among stops;
- individual movement;
- hydrological connectivity;
- a single lower-level mechanism.

The endpoint also ignores exact geometry: a taxon at stops 1,2,3 and a taxon at stops 1,5,10 have the same k=3 concentration score. Route-topology/adjacency analyses are therefore secondary corroboration, not part of H itself.

## Recommended wording change

Avoid:
> the effect begins at the third site

Prefer:
> the cumulative excess lies in the deep multi-site tail: second- and third-stop marginal participation are consistent with the activation nulls, whereas fourth through tenth occupied stops are overrepresented.

Or more compactly:
> recent-rain activation produces a heavier within-taxon spatial tail than expected, with recruited taxa persisting across unusually many route stops.

