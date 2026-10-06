# Final initial-submission receipt — 2026-10-06

## Canonical submission state

Canonical scientific-bundle source commit:
- `3c7677e14866f70f922ff09d2fd398d6e5d74279`

A later operational commit narrows the JAE workflow trigger set only. Comparison against the bundle-source commit shows no manuscript, Supporting Information, figure, analysis, provenance or cover-letter changes. Receipt/readiness-only commits after this point are intentionally excluded from bundle triggers.

Current manuscript:
- title: **Rainfall-associated frog chorus activation is concentrated within taxa across multiple sites**
- anonymous manuscript: **7,996 words**
- title-page template: **158 words**
- current combined count: approximately **8,154 words**
- current margin below the 8,500-word Research Article limit: approximately **346 words**
- Abstract: **320 words**
- cover letter: **412 words**

The finite public-data scale validation has been completed and reclosed under:
- `revision/PUBLIC_DATA_SCALE_VALIDATION_CLOSURE_2026-10-06.md`

No further same-data NAAMP endpoint, weather-window, mechanism, trait, landscape or threshold analysis is authorized for this submission state.

## Final scientific additions

The final manuscript retains the original focal endpoint and principal comparator and adds two post-hoc within-programme validation results:

1. **Blocked State transferability**
   - 2,916 pairs, 439 routes, 20 States;
   - focal-State-excluded species-response training;
   - observed concentration **1.6503** versus **1.3557** predicted;
   - residual **0.2947**, null 95% **−0.1203 to 0.1298**;
   - plus-one P = **0.000999**.

2. **Blocked temporal transferability**
   - response and physical-site history frozen through 2008;
   - evaluation only in 2009–2015;
   - 1,095 pairs, 211 routes, 18 States;
   - observed **3.0058** versus **2.4288** predicted;
   - residual **0.5771**, null 95% **−0.2253 to 0.2377**;
   - plus-one P = **0.000999**.

A future-rain negative control remains an interpretation boundary:
- antecedent 72-h prediction **1.4345**, residual **0.2791**;
- future +1–72 h prediction **1.4291**, residual **0.2845**;
- future-rain residual remains above its null 95% upper bound.

Therefore the 72-h rainfall-amount increment is not interpreted as specifically antecedent, while the focal spatial-allocation excess remains.

## Final main-text boundary

The manuscript still does **not** claim:
- rainfall causality;
- literal synchrony among sequentially sampled stops;
- movement, colonization or occupancy change;
- individual memory or philopatry;
- reproductive success;
- a unique lower-level mechanism;
- independent confirmation.

The blocked tests are explicitly described as **post-hoc within-programme transferability**, not external confirmation.

## Final GitHub Actions validation

On scientific-bundle source commit `3c7677e14866f70f922ff09d2fd398d6e5d74279`:

- JAE submission pipeline
  - run: **37406142401**
  - conclusion: **SUCCESS**

Within that run, all scientific-package steps succeeded:
- integrated manuscript QA;
- figure rendering from frozen inputs;
- private-metadata renderer smoke test;
- anonymous manuscript and Supporting Information build;
- JAE formatting and anonymity verification;
- anonymous reviewer-code bundle build and identity scan;
- scientific submission bundle assembly;
- artifact upload.

The later workflow-trigger hardening commit changes only `.github/workflows/pulse_template_submission_pipeline.yml`; the canonical scientific inputs are unchanged.

## Final anonymous scientific bundle

Artifact:
- name: `frogcs-jae-pulse-template-scientific-submission`
- artifact ID: **11387327485**
- size: **1,191,690 bytes**
- digest: `sha256:018dbab97284978ec69cb37736ba111b4b38b4f76f0c490406a0976c892c8226`
- source workflow run: **37406142401**
- source scientific commit: `3c7677e14866f70f922ff09d2fd398d6e5d74279`

This is the canonical anonymous reviewer-facing scientific package. Subsequent receipt/readiness-only repository edits do not alter its contents and no longer trigger a scientific-bundle rebuild.

## Remaining initial-submission blockers

Only author-side decisions remain:
- final author set/order;
- affiliations;
- corresponding-author details;
- CRediT roles where applicable;
- funding/acknowledgements;
- Conflict of Interest;
- Statement on Inclusion approval;
- final author/institutional approvals.

## Pre-publication archive finalization

Not required to block initial submission:
- repository/archive license;
- final release/archive source;
- Zenodo persistent DOI;
- final archive `CITATION.cff` and Zenodo metadata.

The scientific analysis and submission packaging are otherwise complete.
