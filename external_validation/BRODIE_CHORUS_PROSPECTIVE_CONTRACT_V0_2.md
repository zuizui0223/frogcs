# Prospective external validation contract — Brodie chorus dataset v0.2

**Frozen before inspecting Brodie raw frog-response rows or calculating any endpoint.**
**This v0.2 supersedes v0.1 before outcome access.**

## Why v0.2 exists

A literature audit conducted after v0.1 but still before any Brodie outcome readback showed that
generic persistence of spatial structure through a pulse is too close to established ecological-memory,
disturbance-legacy and frog cross-site chorusing literature to carry the main external novelty test.

The sharper prediction was already frozen in the parent NAAMP science lock before this external
dataset was selected:

> Broad activation need not erase spatial selectivity; deep multi-site activity may remain more
> strongly associated with recurrent high-use sites than shallow activity.

v0.2 therefore promotes the **deep-versus-shallow strengthening of historical spatial alignment**
to the sole primary external test. The former v0.1 persistence test is retained as secondary.

No Brodie response row has been used to make this change.

## Dataset and fixed temporal split

Dataset: Brodie, Schwarzkopf & Allen-Ankins, DOI 10.25903/bpkv-gf77.

Published metadata describe nightly chorus minutes for 17 frog species at three fixed Hervey Range
breeding sites from 2012-10-04 through 2014-04-27.

Fixed split:
- training/history: 2012-10-04 through 2013-09-30 inclusive;
- validation: 2013-10-01 through 2014-04-27 inclusive.

The split will not change after response access.

## Validity and zero coding

A species-date is used only when recording status is available for all three sites on that date.
Unavailable/missing recordings are never zeros.

For a valid recorded site-night, no detected chorus for the focal species is zero chorus minutes.

## Strictly-prior taxon-specific site template

For each species s and site j in training:

1. `m_sj = mean(log1p(chorus_minutes_sjt))` across valid nights, including valid zeros.
2. Remove generic species and site levels:
   `h_sj = m_sj - mean_j(m_sj) - mean_s(m_sj) + grand_mean(m)`.
3. Re-center `h_sj` to zero mean within species.

Thus `h_sj` represents a strictly-prior species × site interaction beyond generic species activity
and generic site productivity.

Template eligibility requires:
- valid training coverage at all three sites;
- positive training chorus at >=2 sites;
- non-identical `h_sj` values.

## Validation depth and current allocation

For each eligible validation species-night:
- `k` = number of three sites with chorus_minutes > 0;
- deep/broad = k=3;
- shallow = k=1 or k=2.

For each species-night with positive total chorus:
`r_sjt = chorus_minutes_sjt / sum_j(chorus_minutes_sjt)`.

Historical-template alignment:
`A_st = sum_j r_sjt * h_sj`.

Because h is centered within species, uniform current allocation across all three sites has A=0.
Positive A means current chorus minutes are weighted toward sites that were historically strong for
that species beyond generic site productivity.

## PRIMARY TEST — does broad activation strengthen rather than erase spatial identity?

Use only species represented by both deep and shallow validation nights.

Within each species:
- `A_deep_s` = mean A across k=3 validation nights;
- `A_shallow_s` = mean A across k=1-2 validation nights;
- `Delta_s = A_deep_s - A_shallow_s`.

Primary statistic:
- equal-species-weighted `Delta = mean_s(Delta_s)`.

No species is weighted by its number of nights.

### Primary null and support rule

Within each eligible species independently permute the three historical h labels across the three
physical sites, hold all validation response rows and deep/shallow classifications fixed, recalculate
Delta, and repeat 10,000 times with seed 2840236.

Report plus-one one-sided upper-tail P.

**External support requires both:**
- observed Delta > 0;
- permutation P <= 0.05.

This directly tests the prospective NAAMP prediction that broad activation is **more strongly**, not
merely equally, aligned with recurrent taxon-specific spatial use than shallow activation.

## Structural informativeness gate

Before calculating the primary statistic require:
- >=5 template-eligible species represented in both deep and shallow classes;
- >=50 total deep (k=3) validation species-nights;
- >=50 total shallow (k=1-2) validation species-nights;
- >=30 distinct validation dates represented among deep events.

If any gate fails, classify the primary external test as **structurally insufficient**. Do not relax
k=3, alter the temporal split, change the template, pool sites, or replace the primary endpoint.

## Secondary tests fixed before outcome access

### S1 — persistence within maximal breadth

For k=3 nights only, average A within species and then equally across species.

Use 10,000 within-species h-label permutations, seed 2840235, plus-one one-sided P.

This asks whether spatial identity persists when all three sites are active. It is secondary because
generic persistence alone is not a strong conceptual novelty claim.

### S2 — historical strongest-site share

For species with a unique maximum h site, report the equal-species-weighted fraction of total k=3
chorus minutes at that historical strongest site. Compare descriptively with 1/3.

### S3 — rainfall modulation

Only if the public record contains same-night rainfall in the linked weather table, standardize that
published rainfall variable across validation dates and fit alignment A against rainfall with species
fixed effects and date-clustered covariance.

No alternative rainfall window may replace it after outcome readback.

## Interpretation classes

- **external support of sharp prediction:** structural gate passes and primary rule passes.
- **informative non-support:** structural gate passes and primary rule fails.
- **structurally insufficient:** primary structural gate fails.

Secondary S1 may show persistence even if the primary sharp prediction fails; that outcome must not
be described as confirmation of the stronger prediction.

## Biological claim authorized by a positive primary result

> When reproductive activity expands to all monitored breeding sites, spatial identity is not diluted:
> the distribution of chorus activity is more strongly aligned with taxon-specific historical site use
> than on spatially shallower nights.

This would provide independent support for **expansion without spatial homogenization**.

It would not establish:
- the NAAMP ten-stop concentration effect itself;
- rainfall causality;
- individual memory or philopatry;
- movement or social coordination among sites;
- a universal ecological-memory law.

A negative or structurally insufficient result closes this Brodie test without endpoint redesign.
