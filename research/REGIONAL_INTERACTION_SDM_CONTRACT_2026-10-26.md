# Regional interaction-evidence SDM / SSDM cohort

This supersedes the 18-species convenience cohort for the current analysis.
The original cohort is preserved solely as a feasibility pilot. User steering
explicitly permits selecting GloBI interaction-recorded species instead of
claiming total diversity from a few abundant species.

Candidate geography: US records within 24–50 N, 101–65 W, conservatively wider
than all eligible NAAMP coordinates (25.746–49.345 N, 99.001–67.465 W).
Candidate discovery has no date or coordinate-uncertainty cutoff; fossil and
living-specimen basis types are excluded. Training retains the earlier broad
continental-US, 1980–2015, reported-uncertainty <=1 km scope. Lack of training
records does not mean lack of regional distribution.

Independent checklists: 203 ARMI amphibian entries from 37 intersecting US
states (whole states, broader than the box; DC unavailable), and 471 DSA2024
Canadian/continental-US odonate entries. 674 names were checked against GBIF:
673 exact accepted/synonym bridges and one unresolved provisional Orthemis sp.
The regional GBIF query returns 823 candidate labels, of which 202 have no
support in these checklists and remain distribution/taxonomy review items.
This is not a declaration that all 823 truly occur in the NAAMP region.

Primary interaction evidence: GloBI links with both species resolved and
independently supported regionally. Twenty species participate in 16 named
relations: 8 eats, 2 preysOn, 1 ecologicallyRelatedTo, 3 interactsWith, and
2 coOccursWith. These are not all predation records or independent studies.

Supplementary evidence: retain a regionally supported focal species when
GloBI verified both guild paths but the counterpart is not species-resolved.
This adds ten species; it does not identify a local species pair. Original
citations, stages, direction and raw receipt links are retained separately.

Final retrieval cohort: 30 species (17 Anura, 7 Caudata, 6 Odonata), no
record-count ranking or top-N selection. Retrieve even species with fewer
than 100 strict historical records, then report actual spatial-cell support.
Do not fit <30 valid independent 10-minute cells; retain their explicit
unmodeled status in coverage. All-stage records remain eligible. This cohort
is interaction-associated diversity, not all regional species diversity.

Use the same source-pinned predictors, spatial validation, background
sensitivity and fixed NAAMP matching as the earlier contracts. SSDM thresholds
and comparisons follow SSDM_PILOT_CONTRACT_2026-10-26.md, with pool sizes read
from the species actually fitted. Preserve failed/weak species validation.
Pond-breeding Ambystoma and Notophthalmus form a supplementary functional
subset; do not treat Plethodon (direct development) or Eurycea (stream-associated)
as pond larval predators. GloBI stages do not calibrate stage-specific SDMs.

Review tables and source receipts:
research/results/regional_species_pool_20261026/ . No claim of exhaustive
regional pool coverage, local interaction, or causal pond preference follows
from this screening.
