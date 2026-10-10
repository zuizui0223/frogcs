# v5.4 — Original taxonomic provenance: genus-pooled tadpoles vs published speciesCode rows

**2026-10-10 JST. Post-v5.2 exploratory SOURCE CORRESPONDENCE audit, not an original preregistration and not an ecological-effect fit. JAE RC6 main untouched.**

## What the ORIGINAL source establishes and what it does not

Wassens et al. [CEWO/CSU *Murrumbidgee River System Technical Report 2014–20*](https://cdn.csu.edu.au/__data/assets/pdf_file/0008/3853403/Murrumbidgee-2019-20-MER-Technical-Report_final.pdf), Table 4-23, states clearly that *Limnodynastes* tadpoles are combined because the larvae cannot be identified to species in the field. Adult calling was recorded using timed nocturnal transects and tadpole CPUE came from overnight fyke-net sampling. The authoritative public [CEWH Flow-MER Frog Abundance 2014–2022 dictionary](https://data.gov.au/data/dataset/flow-mer-frog-abundance) defines `speciesCode` as a species bio-code and `speciesName` as the scientific name, while `CPUETadpoles` is a mean catch per unit effort. **Neither public document specifies the exact transformations from genus-identified field tadpoles into published speciesCode rows across all 2014–22 water years.**

The actual [v5.3 aggregate source-unit audit](V5_3_REAL_SOURCE_STAGE_GRAIN_QA_AND_SIGN_REVERSAL_DOWNGRADE.md) found **7/98** multi-species site×interval groups where two or more different published species rows had **equal strictly positive** `CPUETadpoles`. That equality is not a synonym for documented pooled-genus assignment; the same positive ratio may occur coincidentally due to rounding and common net effort. No underlying field-stage species mapping has been established.

## Freeze exact post-outcome-source-validation audit *before* viewing tie taxonomy

This check follows exposure to the v5.2 sign reversal, so **ALL results are post-outcome source diagnostics**. It can be falsifying or validating an interpretation, not confirmatory biological inference.

**Exact public API projection:** `Program`, `SamplePoint`, `SampleDate`, `sampleDateStart`, `sampleDateEnd(Date/Time)`, `speciesCode`, `speciesName`, `callingEvidence`, `CPUETadpoles`. No coordinates, observers, physical addresses or free text are requested.

Same frozen source unit as v5.2–v5.3: Murrumbidgee, strictly positive intervals **>31 days**, valid species/site/timestamps and CPUE, discard **all records** in any duplicate speciesCode×site×start×end key.

**Output only aggregated, nonreversible counts:**
1. Within the seven (or currently source-observed number of) positive CPUE-tie events, count events having positive duplicate pairs of **two different `Limnodynastes` species codes** (strongly consistent with, still not proof of, pooled-genus measurement), events where ties involve **two different genera**, and events where exact published `speciesName` parsing is unavailable or genus ambiguous. A single interval may belong to multiple types. Compare positive tied **species pairs** rather than just interval counts.
2. Check whether every source `speciesCode` maps consistently to a single normalized `speciesName` in the observed public projection. Count ambiguous mappings and blank/malformed species labels; do not output names/codes/ID hashes.
3. Count source genus-level `Limnodynastes` species-labelled rows and intervals, without looking at whether calling Y versus N predicts CPUE; report only the structural existence and count of positive-CPUE ties inside the same genus.
4. Preserve the exact **7 positive CPUE shared intervals / 98 site×period units** and check totals against v5.3. Do not cherry-pick genus-specific sign reversal or fit new regressions.

**Stop policy:** a genuine taxon code name conflict, larval genus pooling across different adult species, or unverified stage assignment blocks same-species breeding-payoff inference. A positive CPUE tie entirely outside *Limnodynastes* does **not** prove the original statement wrong: exact equal CPUE could be coincidental or water/site sampling-level. Either result means **the publication-level taxon crosswalk still has to be verified**, before interpreting v5.2's equal-pair +19.8 pp as conspecific larval production.

### Distinct source-status

No original fyke-net taxonomic field sheet, breeding success outcome, wetland hydroperiod or survey effort was downloaded. No direct data-custodian contact or sensitive coordinates requested. This source audit must not revise the locked frogcs JAE RC6.
