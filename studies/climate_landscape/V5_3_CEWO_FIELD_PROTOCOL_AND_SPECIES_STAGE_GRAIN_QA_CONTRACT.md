# v5.3 — Freeze source-unit checks before examining repeated tadpole CPUE across species

**2026-10-10 JST • Exploratory follow-up to v5.2, not a preregistered confirmation.**
**No JAE RC6 main changes.**

## Why v5.2 cannot yet be treated as a species-specific reproductive association

The primary Commonwealth Environmental Water Office / CSU [Murrumbidgee River System Technical Report 2014–2020](https://cdn.csu.edu.au/__data/assets/pdf_file/0008/3853403/Murrumbidgee-2019-20-MER-Technical-Report_final.pdf), section 4.5, original PDF page 92, states adult frog acoustic/encounter surveying was conducted after dark with **two 20-minute transects**, while tadpoles were collected using **two large and two small overnight fyke nets**, with alternatives at shallow water. Tadpole CPUE is **catch divided by average deployment (net-soak) time** of the four nets. Surveying was conditional on site water presence and suitability for the sampling gear. The original table at PDF p.109 explicitly says tadpoles of **Limnodynastes spp. were pooled at genus**, because they could not be identified to species in the field. No source-authenticated map has been established between the 2014–2022 public CKAN frog row's `speciesCode` and the original field-level genus-tadpole stage code.

This directly affects the v5.2 579-row result: a species-labelled field does NOT prove a corresponding tadpole CPUE is a same-species offspring count. Its `callingEvidence=N` means no observed calling **as recorded** in a species-listed row, not a guaranteed absence of the adult taxon, not a standardized five-minute silent census, and not the absence of any reproduction. This source also lacks water depth and actual net-soak effort fields. Original scientific design cannot be inferred from source type names alone.

A newer official [Murrumbidgee 2024–2030 research plan](https://www.dcceew.gov.au/sites/default/files/documents/flow-mer-murrumbidgee-area-scale-evaluation-research-plan-2024-30.pdf) lists **three 2-minute calling recordings separated by 10 minutes** and a **40-minute nocturnal transect** for updated monitoring. That future design should not be applied retrospectively to the original 2014–2022 CSV without a verifiable versioned protocol crosswalk.

## Pre-read structural questions — exact source projection only

Source: [data.gov.au Flow-MER Frog Abundance 2014–2022](https://data.gov.au/data/dataset/flow-mer-frog-abundance) resource `70f3b7c9-990b-4770-b306-57c4e7cdac61`. Frozen projection, excluding animal locations and free text:

`Program, SamplePoint, SampleDate, sampleDateStart, sampleDateEnd(Date/Time), speciesCode, callingEvidence, CPUETadpoles`

Frames: same previously frozen Murrumbidgee long positive-duration period >31 days; exclude the 10 zero-length records and both rows with duplicated `site×species×start×end`. This check uses a **previously observed outcome dataset**; any finding here is *post-outcome source QA* and must be labelled as such.

- Is each `site×observation interval` represented by multiple different frog species, and how many records per original interval? This tests whether the 579 input rows should count as 579 independently sampled site intervals.
- Among the multi-species intervals, how often are all or some positive `CPUETadpoles` **numerically identical** across distinct species? Distinguish trivial **all-zero** intervals from positive values. Repeated identical values are *consistent with* an aggregate index being repeated across listed taxa, but do **not alone prove** wrong species attribution (true ties/rounding may occur).
- Count number of independent `site×source interval` units, counts of intervals with positive tadpole CPUE at all, all species values identical vs heterogeneous, and original site/interval/date identity multiplicity. **Never print species names or site IDs** in CI logs/commits.
- Never choose a species-specific cherry-picked subgroup or refit a “positive effect.” If aggregate water-stage indices are shared across species, **suspend** the biological interpretation of the v5.2 within-species×site +19.85 pp rather than inventing a corrected causal estimate from this data.

## Stop rules

**STOP species-specific tadpole payoff inference** until (a) original source field manual/codebook establishes taxonomic assignment of fyke-net tadpoles, especially Limnodynastes, (b) source effort/absence/gear validity is available for the complete species-site-interval risk set, and (c) original visit dates/call and net sampling schedules permit defensible same-period comparisons.

This audit can, at most, distinguish evidence that records are at **site×season survey grain** versus genuine **species×survey biological grain**. It cannot establish rainfall triggering, metamorphosis success, adaptive spatial memory or individual reproductive benefit. The v5.2 sign reversal remains a **numerical descriptive fact for the published rows**, not confirmed taxon-specific ecological mechanism.

**Provenance:** 2021 CEWO/CSU report original pp. 92 and 109 (PDF pages, section 4.5 Methods and Table 4-23); Australian Commonwealth government frog attribute dictionary (2014–22); [v5.2 response-frozen contract](V5_2_PRE_RESPONSE_PERIOD_LEVEL_CALLING_TADPOLE_CONCORDANCE_CONTRACT.md). No source contacts sent; no protected coordinates output.
