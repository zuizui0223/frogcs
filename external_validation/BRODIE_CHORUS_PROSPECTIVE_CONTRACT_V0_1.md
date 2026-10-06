# Prospective external validation contract — Brodie chorus dataset v0.1

**Frozen before inspecting raw Brodie response rows for this reanalysis.**

## Status and separation from RC6

This is a new external-validation project decision on branch `external/brodie-chorus-validation-v1`.
It does not reopen the closed NAAMP endpoint search and is not evidence in RC6 unless the
predefined external test is executed without outcome-driven retuning and its status is reported
regardless of direction.

The hypothesis is inherited from the frozen NAAMP science lock:

> Broad activation need not erase spatial selectivity; spatially deep activity may remain associated
> with recurrent high-use locations.

The Brodie dataset has only three fixed breeding sites, so it cannot replicate the NAAMP ten-stop
deep-tail endpoint. It can independently test the narrower biological prediction that the broadest
possible cross-site chorus state remains aligned with a taxon-specific historical site template.

## External dataset

Brodie, Schwarzkopf & Allen-Ankins data record:
**Data for: Chorusing patterns and environmental drivers of an Australian tropical savanna frog community**
DOI: 10.25903/bpkv-gf77.

Published metadata state that the record contains nightly chorus activity (minutes chorusing) for
17 frog species at three fixed breeding sites near Hervey Range, Queensland, from 2012-10-04 through
2014-04-27, plus nightly environmental data.

No NAAMP observation is present in this dataset.

## Primary question

On validation nights when a taxon is chorusing at **all three fixed breeding sites**, is the
distribution of its chorus minutes still preferentially aligned with its taxon-specific historical
site-use template estimated from earlier data?

This asks whether maximal spatial breadth homogenizes site use or whether spatial identity persists
inside a broad species-night response.

## Temporal split

The split is fixed before raw response-row inspection.

- **training/history period:** 2012-10-04 through 2013-09-30 inclusive
- **validation period:** 2013-10-01 through 2014-04-27 inclusive

No date threshold may be moved after outcome readback.

## Valid site-nights and missingness

A validation species-night is eligible only when recording status is available for all three sites.
Missing or unavailable recordings are never coded as zero chorus.

The response is nightly chorus duration in minutes for each species x date x site. A valid recorded
site with no chorus for that species is coded as zero.

## Historical species-specific site template

For each eligible species s and site j in the training period:

1. compute `m_sj = mean(log1p(chorus_minutes_sjt))` over valid recorded nights, including valid zeros;
2. remove generic species and site levels using the two-way interaction residual

   `h_sj = m_sj - mean_j(m_sj) - mean_s(m_sj) + grand_mean(m)`;

3. re-center `h_sj` to mean zero within species.

Thus `h_sj` is a strictly prior species x site preference score beyond generic site productivity.
No validation observation contributes to `h_sj`.

Species are template-eligible only if:
- they have valid training coverage at all three sites;
- they have positive training chorus at at least two sites;
- their three `h_sj` values are not identical.

## Validation spatial depth

For each eligible species-night in validation, let `k` be the number of the three sites with
chorus_minutes > 0.

- **deep/broad activation (primary population): k = 3**
- shallow activation for the prespecified contrast: k = 1 or 2

The k=3 definition will not be relaxed after outcome readback.

## Primary endpoint

For each k=3 species-night, define current chorus shares

`r_sjt = chorus_minutes_sjt / sum_j(chorus_minutes_sjt)`.

Historical-template alignment is

`A_st = sum_j r_sjt * h_sj`.

Because `h` is centered within species, a perfectly uniform 1/3 : 1/3 : 1/3 allocation has
`A_st = 0`. Positive values mean the broad current chorus is weighted toward sites that were
taxon-specifically stronger in the training period.

The primary statistic is the equal-species-weighted mean alignment:

1. average `A_st` across eligible k=3 validation nights within each species;
2. average those species means equally across species.

No species is weighted by its number of active nights.

### Primary support rule

Replication support requires:
- observed primary statistic > 0; and
- one-sided within-species site-label permutation P <= 0.05.

The permutation null independently permutes the three historical `h_sj` labels within each species,
holds all validation response data fixed, uses 10,000 replicates, seed 2840235, and reports a plus-one
upper-tail P value.

## Structural informativeness gate

Before calculating the primary alignment statistic, require:
- at least 5 template-eligible species with at least one k=3 validation night;
- at least 50 total eligible species-night k=3 clusters;
- at least 30 distinct validation dates represented.

If any gate fails, classify this dataset as **structurally insufficient for the frozen primary test**.
Do not relax k=3, alter dates, pool sites, redefine the template, or promote a weaker endpoint as the
primary result.

## Prespecified secondary tests

### S1 — deep versus shallow template coupling

Among species having both k=3 and k=1-2 validation nights, calculate the same equal-species-weighted
mean alignment separately for deep and shallow nights.

Statistic:
`Delta = mean_species(A_deep - A_shallow)`.

Use the same 10,000 within-species site-label permutations and seed 2840236.
A positive Delta with one-sided P <= 0.05 supports the sharper prediction that broad activation is
more, not less, aligned with prior taxon-specific spatial use.

This is secondary because the three-site design is not homologous to NAAMP's ten-stop deep tail.

### S2 — historical strongest-site share

For interpretation only, identify each species' unique highest `h_sj` site when one exists and report,
on k=3 nights, the equal-species-weighted mean fraction of chorus minutes occurring at that site.
Compare descriptively with 1/3. This is an effect-size aid, not a replacement endpoint.

### S3 — rain modulation

If the public weather table contains the published same-night rainfall total for the recording night,
standardize rainfall across validation dates and test whether `A_st` increases with rainfall using
a species-fixed-effect regression with date-clustered covariance.

This is secondary. Failure does not negate the primary persistence-of-spatial-selectivity test.
Do not substitute another rainfall window after readback.

## Interpretation classes

- **external support:** primary support rule passes.
- **informative non-support:** structural gate passes but the primary support rule fails.
- **structurally insufficient:** any structural gate fails.

The result must be reported under one of these three labels.

## Claim boundary

A positive result would support:

> Even when a frog taxon is chorusing across all monitored breeding sites, the distribution of chorus
> activity can retain a taxon-specific spatial signature learned from an earlier period.

It would not establish:
- the NAAMP ten-stop concentration effect itself;
- rainfall causality;
- individual memory or philopatry;
- movement among sites;
- social coordination;
- a universal pulse law.

A negative result would remain informative and must not trigger endpoint redesign in this dataset.
