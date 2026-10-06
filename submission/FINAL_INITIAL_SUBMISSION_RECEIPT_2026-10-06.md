# Final initial-submission receipt — 2026-10-06

## Canonical submission state

Canonical scientific-bundle source commit:
- `85610c8bf9f56491c5d3c0ba88b66ae8bc1e86cf`

The final conceptual framing distinguishes **response magnitude** from **realised configuration** without changing any endpoint or numerical result. Receipt/readiness-only commits after this point are excluded from scientific-bundle triggers.

Current manuscript:
- title: **Rainfall-associated frog chorus activation is concentrated within taxa across multiple sites**
- anonymous manuscript: **7,966 words**
- title-page template: **158 words**
- current combined count: approximately **8,124 words**
- current margin below the 8,500-word Research Article limit: approximately **376 words**
- Abstract: **293 words**
- cover letter: **400 words**

The finite public-data scale validation has been completed and reclosed under:
- `revision/PUBLIC_DATA_SCALE_VALIDATION_CLOSURE_2026-10-06.md`

No further same-data NAAMP endpoint, weather-window, mechanism, trait, landscape or threshold analysis is authorized for this submission state.

## Final conceptual framing

The reader-facing contribution is now stated consistently as a distinction between two empirical properties of a short behavioural response:

- **response magnitude** — how much activity appears;
- **realised configuration** — how that activity is distributed among taxa and places after first-order propensities are represented.

This is an ecological framing of the existing frozen result, not a new endpoint or statistical theorem. The detailed boundary is recorded in:
- `revision/KNOWLEDGE_SHIFT_SYNTHESIS_V0_1.md`.

## Final visual polish

The final submission-facing figure/abstract audit made no new scientific inference:

- Figure 1 explicitly labels the upper three decomposition quantities as **point estimates only** and the two direct CI3 endpoints as **95% CI**, with the note placed above the axes;
- Figure 3 shows four conditional-residual rows: the principal comparator, held-out rain × history gate, focal-State-excluded response training and the 2009–2015 temporal block;
- the two blocked rows remain explicitly post-hoc within-programme transferability tests;
- Abstract point 5 was reduced to the core conclusion, one blocked-transferability sentence and the confirmation boundary;
- internal filenames remain confined to the SI provenance table;
- Kusano et al. (1999) retains the original journal spelling **Kanenko**.

The generated Figure 1 and Figure 3 files were synchronized onto main by deterministic figure-build commit `4c4f65f46f62f39216d50cccb2a64497ee818b6c`.

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

On scientific-bundle source commit `85610c8bf9f56491c5d3c0ba88b66ae8bc1e86cf`:

- JAE submission pipeline
  - run: **37422937862**
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

## Final anonymous scientific bundle

Artifact:
- name: `frogcs-jae-pulse-template-scientific-submission`
- artifact ID: **11393249104**
- size: **1,222,249 bytes**
- digest: `sha256:3714e36148fb3d11d2b2e52b1dc72aa297e6d2284293bde6fe477c460d61ffa7`
- source workflow run: **37422937862**
- source scientific commit: `85610c8bf9f56491c5d3c0ba88b66ae8bc1e86cf`

This is the canonical anonymous reviewer-facing scientific package. Its bundled canonical provenance is self-reference-free: dynamic artifact identifiers live only in this receipt, not inside `CURRENT_ANALYSIS_SPECIFICATIONS.json`. Subsequent receipt/readiness-only edits do not alter its contents and do not trigger a scientific-bundle rebuild.

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
