# Cached-data bridge: does aggregate segregation recur at the same route?

2026-10-20. The species-by-SiteID weighted-null contract remains UNEXECUTED: creation of a new GitHub source-export workflow was blocked, direct source access failed, and the separate browser-download attempt did not start because of provider wallet balance. No retry to bypass these constraints, no charge, and no claim that new source data exist.

The available verified ZIPs contain per-run C-score/null statistics and paired scientific metadata, NOT the individual taxon-by-SiteID matrices. Therefore they cannot identify which species pairs drive segregation or run the proposed species-site-history null. The following is a separate, narrower bridge test, frozen before its results are inspected, using only the existing caches.

## Question and scope

Can strictly earlier measurements at the same route, seasonal sampling round, and documented stable physical-station component predict that route's FUTURE degree-conditioned segregation score better than earlier measurements at other routes in the same state and round?

This asks about persistence of the DEGREE of segregation, not persistence of species-pair identities, environmental causes, competition, learning, or breeding success. A successful forecast could still reflect habitat, species composition, detection or persistent interactions. A negative forecast does not establish absence of ecological memory.

## Dates and identity without inventing raw records

Use original fixed-margin ZIP (SHA256 0690c24e72172a0d6a5a4a0144bac9bda9c78bacee9651b69b49e2cbb2275e19) and existing environment-cache ZIP (SHA256 e182e0e30a7a5f1a7f1b8683d0024155b06f44b03205faa5df4beb02895d97a0). Verify all inner digests. Union unique wet/dry RunID pair records and verify identical shared metadata. Each pair supplies the two survey years, but wet/dry labels are NOT chronology. Resolve individual run years only when the intersection/propagation of exact pair-year constraints yields ONE unique year. Omit unresolved isolated pairs; never infer year from numeric RunID or wet/dry label. Validate every resolved edge against its archived earlier/later years.

Use transitive components of archived same-physical-SiteID pair flags within State:Route:RunNumber. Both flags must agree where shared sources overlap; do not bridge a relocated/unstable edge. A secondary component also requires same-observer flags. This represents documented continuity in cached pairs, not independent field verification or metre-level coordinate accuracy.

## Prediction, fixed before readback

Eligible target: informative null score, uniquely determined year, at least TWO informative strictly-earlier-year runs in its physical component, and at least FIVE other routes in the same state/round with informative strictly-earlier records. Deduplicate RunIDs everywhere. All target years are tested in expanding past-only fashion; no coefficient is fit on a target or future records.

Peer-only prediction mu: mean of historical per-route mean E at other routes in the same state and round (each route equal weight), excluding the target route completely. E=observed Cscore-minus-fixed-margin-null mean.

Local-history prediction: (sum of earlier same-component E + 2*mu)/(n_prior+2). Two pseudo-observations of the peer mean are a FIXED shrinkage rule, not optimized using results.

PRIMARY: per-target squared prediction error(peer) minus squared prediction error(local history). Average first within route, then equally across routes. Report 2,000 route-bootstrap CI (seed 20261022), route-equal error reduction and fraction of routes helped. Minimum 100 targets / 30 routes; if insufficient do not weaken the gate.

Pre-named sensitivities: same-observer historical component; standardized E/null_SD rather than raw E; both independent archived Monte Carlo chains on the identical primary sample. Keep raw E primary even if sensitivities differ. Record quantities from every target including exact source history IDs and maximum prior year in the LOCAL audit; omit identity-level audit from any public summary. No new species selection, moisture thresholds, lag windows or repeated tuning.

No inference that peer-only environmental context has fully removed environmental differences. No claim that a better local forecast proves individual memory or inherited historical contingency. No claim of independent external validation: endpoints originated in the already explored NAAMP sample. Original weighted species-site mechanism question remains pending actual source matrices.
