# JAE initial-submission checklist v0.4 — week-scale community-reassembly paper

## Scientific package

- [x] current manuscript: `MANUSCRIPT_JAE_V0_6.md`
- [x] current claim boundary: `ECOLOGICAL_CLAIM_BOUNDARY_V0_2.json`
- [x] current argument spine: `ECOLOGICAL_ARGUMENT_SPINE_V0_2.md`
- [x] matched richness result
- [x] prespecified rain-recency timescale result
- [x] turnover / nestedness decomposition
- [x] raw and adjusted species-response heterogeneity
- [x] within-family species-response heterogeneity
- [x] exact ecological Figure 1–3 hashes
- [x] v0.6 ecological manuscript QA

## Current article claim

> Recent rainfall is associated with a multi-day elevation in active-community richness, detectable through the prespecified 4–7-day bin, together with species-selective wet–dry reassembly.

## Timescale boundary

- [x] run-level route-season FE: day0, day1, days2–3 and days4–7 all exceed >=8-day richness reference
- [x] exact-consecutive dry-anchor sensitivity: clear through days2–3
- [x] days4–7 matched sensitivity: positive but imprecise
- [x] dry–dry compositional-memory comparison failed sample-size gate before effect readback
- [x] no physiological half-life / exact recovery-time claim

## Hard boundaries

- no occupancy or abundance change
- no colonization / extinction
- no rainfall causality
- no breeding-success claim
- no week-long compositional-memory claim
- no proven body-size / hydroperiod / breeding-season mechanism

## JAE formatting

- [x] Research Article route
- [x] <=8,500 words
- [x] <=350-word five-point abstract
- [x] <=8 alphabetical keywords
- [x] double-anonymized main manuscript
- [x] separate title page
- [x] anonymous DOCX builder
- [x] archive-intent statement without reviewer-identifying archive DOI

## Human metadata still required

- [ ] final author set/order
- [ ] affiliations and institutional addresses
- [ ] corresponding author postal address/email
- [ ] CRediT roles
- [ ] funding / acknowledgements
- [ ] Conflict of Interest statement
- [ ] Statement on Inclusion
- [ ] all-author approval
- [ ] all entitled authors included
- [ ] no concurrent submission
- [ ] store completed metadata as Actions secret `JAE_SUBMISSION_METADATA_YAML`

## Initial-submission action

After human metadata are complete, run **frogcs initial JAE submission bundle** from RC5/main and inspect the generated artifact.

## Final archive stage

Archive license, public snapshot and DOI remain deferred until finalization.
