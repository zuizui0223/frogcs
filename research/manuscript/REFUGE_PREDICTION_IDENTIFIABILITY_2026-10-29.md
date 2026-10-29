# Existing-data tests of refuge-mediated indirect rescue

Audit date: 2026-10-29. Scope: discrimination among mechanisms, not a new search for a favourable coefficient. No original kernels, frozen results, or manuscript claims were changed in this audit.

## Finding

The existing macro data can test whether the vegetation–Odonata association differs across salamander-suitability contexts. They cannot identify whether vegetation removes a consumptive D→S→F benefit, changes dragonfly feeding, or supports dragonfly recruitment. A contrast using the same NAAMP observations is an **internal, posthoc model constraint**, not independent verification. A useful additional public source is the Hossie–Murray vegetation experiment distributed through FoRAGE/BayesFR: it can constrain the D→F functional-response alternative with S absent, but cannot identify the mechanism behind the NAAMP association.

Here D means aquatic odonate predators, S means salamanders/newts, and F means tadpoles in a mechanistic model. Macro O and S are environmental suitability indices; macro Y is calling frequency. These are not interchangeable quantities.

## What the frozen observations contain

Direct inspection of `research/results/naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz` confirms 4,248 site rows. The visit source, `research/results/naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz`, has 74,317 rows before fixed-cohort and timeout filtering, years 2001–2015, and fields `strong`, `any`, `season`, `source_taxa`, `prior_n`, and `prior`. `nee_context_robustness.py::load()` restricts completed visits to the frozen sites and verifies the visit totals against site summaries.

| Quantity | Observed or derived information | Missing for mechanism identification |
|---|---|---|
| Y | Site fraction of completed visits with a strong call classification; effort and seasonal summaries | Tadpole density, kills, survival, recruitment, adult abundance, and species-specific strong-call records in this prepared table |
| O | Mean suitability percentile of six Odonata species | Local aquatic abundance, instar, size, prey consumed, emergence |
| S | Mean suitability percentile of five pond-breeding Caudata | Actual presence/absence, larval versus adult state, size, density, feeding |
| V | EarthEnv flooded-vegetation neighbourhood mean at 3 km; 1 km summaries also available | Pond-scale stems, litter, refuge occupancy, recipient-specific protection, oviposition/emergence substrates |
| Time | Survey date/day/year and survey-round code | Three-species developmental overlap and cohort-specific encounters |

The S pool is `Notophthalmus viridescens`, `Ambystoma maculatum`, `A. tigrinum`, `A. laterale`, and `A. mavortium` (`naamp_site_use_associations.py::POND`). O comprises `Libellula luctuosa`, `Sympetrum danae`, `Leucorrhinia intacta`, `Erythemis simplicicollis`, `Argia sedula`, and `Anax junius` (checked in `interaction_species_sdm_20261026/naamp_species_suitability.csv.gz`). The species names do not supply stage observations. GloBI links can establish reported interactions elsewhere; they do not fill these local stage/density gaps.

**Vegetation support is sparse:** only 506/4,248 sites have positive `flooded_3000m_mean`; 3,742 are zero. Its first three quartiles are all zero. A low/high-S contrast therefore needs positive-V site and route counts, O ranges within those cells, and spatial/environmental support diagnostics. The median V is not an informative high-vegetation treatment. Rank transformation retains the large tied zero group; it does not recover unmeasured vegetation structure.

## Mechanism-specific predictions and their limits

| Mechanism | Discriminating quantity in a controlled model or suitable experiment | What current macro observations can say |
|---|---|---|
| Vegetation protects F from S, reducing the benefit of D consuming S | The D→S-mediated component vanishes when actual S is absent or D→S is disabled, holding other paths fixed; it requires S stages vulnerable to D and S capable of consuming F | Compare OV across S-suitability contexts; low suitability is **not S absence**, so persistence of OV there does not eliminate this mechanism |
| Vegetation changes D's response to F density | V changes kill-rate curvature over measured F density even without S | No F density or kill-rate observations; calling frequency cannot serve as the prey-density axis without calibration |
| Vegetation supports D survival or emergence | V changes D survival/emergence and later aquatic abundance, with an explicit lag | No D demographic time series; O suitability is not this mediator |
| D induces F refuge use, reducing S feeding without consuming S | Caged-D cues change F refuge use and S kills while S abundance stays fixed | No cues, behaviour, or feeding observations; observationally can resemble a lost-rescue path |

The absence of the D→S-mediated component at S=0 is a structural prediction; the direction of the **total** OV contrast at low versus high S is not universal. Other paths, predator saturation, stage overlap, F depletion, and the observation mapping can reverse it. Derive the competing predictions on the fixed model output scale before comparing macro coefficients. Do not select a transformation or stratum after seeing which sign fits.

## Feasible analysis using the existing cohort

The full current rank design is O, S, V, OS, OV, SV, OSV, plus the fixed nuisance specification (`nee_context_robustness.py`). With centred standardized ranks, its conditional O-by-V coefficient is

`C_OV(s) = beta_OV + s * beta_OSV`.

At prespecified empirical S reference values, the difference is `(s_high - s_low) * beta_OSV`. This is a contrast of one full model, not two regressions fitted after splitting the data. Use the same outcome, rank reference, adjustment, and pooled/within-route modes as the existing comparison. Report both uniform and target-group backgrounds. Compute bootstrap contrasts draw by draw, retaining covariance between OV and OSV. Report support alongside estimates; a full-rank design alone does not establish adequate ecological overlap.

Interpretation rules fixed before results:

1. A model-predicted contrast reproduced with adequate support is consistency with that **narrow model plus observation assumptions**, not proof of its edge.
2. A robust opposite contrast challenges that mapped model. Do not rescue it by redefining the scale or choosing an unplanned subset.
3. A small or uncertain contrast cannot distinguish mechanisms; a nonsignificant contrast is not equivalence.
4. Poor support makes the contrast inconclusive, even if its fitted sign agrees.

Additional existing summaries have limited roles. Comparing 1 km/3 km flooded vegetation or herbaceous cover can assess proxy specificity; neither is a clean negative control because all may share ecological causes. Prior calling history and repeated dates can assess persistence of site use, but static O/S/V and unobserved larval cohorts prevent a stage-mechanism test. Survey rounds 1–4 are not developmental stages. Positive `source_taxa` records cannot reconstruct species-specific strong calling or undetected-species abundance. These extensions should not be multiplied until a preferred sign appears.

## Primary experimental evidence

**Davenport & Chalcraft (2013)** used adult newts, late-instar Anax, and newly hatched Bufo tadpoles. Lethal/caged predator treatments separated physical predation from cues. Dragonfly-induced tadpole hiding reduced newt feeding; newt-induced behaviour did not similarly change dragonfly feeding. The first experiment supplied the same leaf-litter amount to tubs. It therefore supports a **behaviour-mediated alternative** and a stage-specific refuge role, not an experimental vegetation gradient or evidence that Anax consumed adult newts. Its mortality-risk analysis is also more informative than raw survival differences for avoiding a simple floor explanation. Sources: [primary article](https://doi.org/10.1002/ece3.691), [methods and treatments](https://pmc.ncbi.nlm.nih.gov/articles/PMC3790551/), [abstract and figures](https://pubmed.ncbi.nlm.nih.gov/24101994/).

**Hossie & Murray (2010)** manipulated leaf-litter structure in a dragonfly–tadpole system. Functional responses changed from type II with low/absent cover to type III with sufficient refuge; predator hunting behaviour, rather than density-dependent prey hiding, explained the shift. This directly supports an alternative route by which vegetation changes D→F effects without S. It does not support a claim that vegetation always increases D harm. Source: [author-hosted primary article](https://www.thomashossie.ca/uploads/6/0/6/0/60609931/hossie_and_murray_2010_-_oecologia.pdf), DOI [10.1007/s00442-010-1568-6](https://doi.org/10.1007/s00442-010-1568-6).

A useful accessible data lead is `df_Hossie_and_Murray_2010_OECOLOGIA`, documented as 91 rows across three litter treatments, with initial/eaten prey, duration, predator/prey, and treatment ID. The maintainer tutorial identifies 24-hour nonreplacement trials and Anax junius/Rana pipiens. Sources: [package data documentation](https://www.stats.bris.ac.uk/R/web/packages/BayesFR/refman/BayesFR.html), [maintainer tutorial](https://benjamin-rosenbaum.github.io/BayesFR/Tutorial_02.html), originating [FoRAGE archive](https://doi.org/10.5063/F1RX99KB). **Follow-up retrieval completed:** exact 2010 data subsets, RDA, metadata, primary article and URL/hash receipt are in `research/results/refuge_generality_20261029/external_hossie2010/`. No models were fitted in this audit. This is potentially an external edge constraint, not an independent discovery test: this paper already informed model choice.

The existing raw-package audit (`NEE_EXTERNAL_RAW_AUDIT_2026-10-29.md`) records that the downloaded Hossie 2021 data lack S and vegetation treatments, Urban data access is incomplete and concerns Daphnia prey, and Carroll's potentially useful call–larval/bycatch package has unresolved raw inputs. None currently supplies the joint vegetation × F density × D/S stage × feeding measurements needed to select among these mechanisms.

## Manuscript implication

The defensible advance is a macro pattern plus explicit mechanistic constraints: vegetation-related changes in predator associations motivate competing, stage-dependent pathways, and simulations reveal when those pathways can generate the observed signs on a common scale. Current public evidence can constrain a feeding edge and rule out overbroad interpretations. It cannot turn the selected simulation into the measured cause at NAAMP sites. Distinguishing consumptive rescue loss, behavioural refuge use, direct predator support, and altered functional response remains an identifiability problem until their mediators are observed or experimentally separated.


## Retrieved external data: provenance gate

`receipt.json` records frozen GitHub commit, direct FoRAGE object URLs, hashes and extraction rules. FoRAGE EML declares CC0 1.0; BayesFR package declares GPL >=3. Full FoRAGE tables were moved outside the repository to `../forage_v5_source_archive/`. Exact2010 subsets remain in the repository.

These are **figure-extracted compiled points, not complete original trial data**. Original methods report126 trials: seven replicates at six densities and three cover conditions. Extracted groups have32/30/29 points, totaling91. Replicate multiplicities are incomplete; do not invent missing trials or derive trial-precision claims from this reconstruction.

Numeric/taxon fields agree row-for-row between BayesFR and FoRAGE. FoRAGE metadata IDs506/507/508 mean none/low/high litter, but its curve table labels these Figure1a/1b/1c. Primaryfigure and BayesFR use Figure1a/1c/1e. Follow the saved treatment crosswalk, not uncorrected FoRAGE figure strings.

Original methods counted remaining tadpoles after24h; the figure calls this prey killed, while the compilation calls it eaten. Label the response **24-hour tadpole loss**, not directly observed ingestion or handling. Nonreplacement requires Rogers-type depletion for typeII or an integrated/dynamic typeIII model. Static Holling evaluated at initial density times duration is inappropriate. Original methods and the BayesFR tutorial explicitly account for depletion. Reconstructed parameters describe the experimental species/stage/arena, not NAAMP suitability or calling.
