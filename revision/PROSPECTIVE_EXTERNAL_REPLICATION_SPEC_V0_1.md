# Prospective external replication specification v0.1

**Status:** frozen before selecting or inspecting any external outcome data for this integrated claim.

## Purpose

Prospectively test whether the NAAMP finding of **within-taxon multi-site concentration** generalizes to an independent frog monitoring network.

The external study is confirmation only if its outcome data were not used to develop the NAAMP concentration endpoint or choose the comparator.

## Dataset eligibility

A candidate external monitoring network must provide, before any response analysis:

1. repeated surveys at identifiable physical sites;
2. taxon-level calling/detection records at each site;
3. at least three sites per repeated spatial unit so third-and-later participation is definable;
4. survey-level rainfall recency or an externally linkable rainfall exposure;
5. repeated history sufficient to estimate prior taxon × physical-site use without using the focal comparison;
6. enough independent spatial units to split them deterministically into training and test folds.

If these structural requirements fail, the dataset is classified **ineligible**, not negative.

## Frozen biological endpoint

For each taxon absent from the reference survey and present in the target survey:

- (k_i) = number of target sites occupied;
- (e_i = max(k_i-1,0));
- concentration score (C = Σ_i choose(e_i,2)).

The primary question is whether the survey closer to rain shows more within-taxon concentration than expected under a comparator that preserves transferable taxon response and prior site use.

## Frozen principal comparator

Where the external design permits, fit only:

- taxon-specific rainfall response using the opposite spatial fold;
- strictly-prior taxon × physical-site propensity;
- focal reference-state persistence;
- one common magnitude-matching shift within each comparison.

Do not add taxon × site-specific rain coefficients or new trait terms after outcome readback.

## Primary decision

Support requires the observed concentration effect to exceed the upper 95% comparator distribution in the predeclared direction.

Report the effect size and uncertainty even if the gate fails.

## Secondary endpoints

Secondary only:
- direct silence→strong/full chorus if an ordinal calling index exists;
- third-and-later site participation;
- historical strong-site targeting;
- an exact N,K exchangeable diagnostic.

The N,K diagnostic cannot substitute for the principal comparator.

## One-shot rule

The first eligible external dataset tested under this specification is the confirmatory test.

If it fails, do not search additional external networks and report only successful ones as confirmation. Further datasets may be analysed as explicit replications, with all outcomes disclosed.

## Interpretation

A positive external result would support transferability of the multi-site concentration pattern.

A negative result would delimit its generality.

Neither outcome identifies the lower-level biological generator.
