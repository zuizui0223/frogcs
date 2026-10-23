# Frozen post-readback vegetation-class and taxon-breadth follow-up to rarefied gamma

Date 2026-10-23. Analysis added **after** the immediately preceding 6,236-run rarefied-gamma study found positive PEM acoustic taxon-pool difference (+0.33184 CI>=1, +0.23652 CI>=2 per equal-size 2–5-stop pooled sample, 286 physical routes). Hence targeted **post-hoc explanatory test**, not an independent prospective hypothesis. No literature review, prediction/forecast, species transplant or new data; JAE RC6 main/paper/SI protected.

## Macroecological question

Does PEM-associated taxon-pool enrichment still occur **among stations already mapped as wetlands**, rather than being an artefact of comparing wetlands to totally NWI-unmapped land? Across these comparisons, is pooled-gamma surplus distributed across multiple acoustic taxon labels or attributable to a single widespread taxon?

## Original data and exact balanced treatment

Reuse the original source-verified NAAMP 2001–2015 7,848 standardized nights / 6,236 NWI-complete ten-stop route-nights and validated 5,147 USFWS NWI physical site records (12-shard source #39450277196). Two original calling-index thresholds CI>=1 and CI>=2; keep all recorded labels including complexes. Select only 250m NWI stations with **any mapped wetland fraction>0** (the wetland denominator); distinguish PEM fraction>0 from PEM==0. If wetland-mapped stops are fewer than 2 in either PEM class, route-night fails the **primary** multi-site comparison. Equalize sampling effort to m=min(n_PEM+,n_PEM−), m>=2, never treating ten-stop nights or exact expectation draws as independent replicates.

Two **secondary** subconditions, frozen now for architecture specificity:
- among **woody/shrub-NWI-overlap** wetland stations only, PEM+ vs PEM0;
- among wetland stations with **no mapped woody class**, PEM+ vs PEM0.

The two woody subconditions may be underpowered; do not tune m or minimum route threshold after reading them. All source comparisons have the **same wetland criterion** and original mapped 250m buffer. Class 0 means no mapped polygon overlap, not proof of botanical absence. PEM and woody polygons may overlap within 250m of the same stop.

Use the exact no-replacement taxon inclusion probability
`p_s(m)=1−C(n−k_s,m)/C(n,m)`,
and pooled gamma Δ = Σ_s(p_s,PEM+ − p_s,PEM−), from the already validated `exploration/run_naamp_rarefied_vegetation_gamma_v0_1.py`. Calculate per-run gamma± and shared/exclusive expectations. **Primary** all-wetland PEM gamma difference per independent route; **secondary** two woody-context strata. Require >=30 physical routes and >=5 States. Six comparisons (3 conditions × CI>=1/CI>=2) with all six retained in one BH correction family, route mean -> cluster-t interval, 4,999 independent-route sign flips, 20-State distribution and leave-one-State-out diagnostic. n_m >=2 eligibility not varied after readback.

## Species-level ecological hierarchy, descriptive (only main wetland-conditioned PEM contrast)

At each eligible route-night, for **every** original monitoring taxon s compute the exact contribution `d_s=p_s,PEM+−p_s,PEM−`. Every route contributes the mean across its eligible nights including zero contributions for taxa not detected; equal independent-route weighting. Verify sum of all named taxon contributions equals the overall wetland-conditioned gamma contrast within 1e−10. Report number of positive and negative contributing labels, top 10 contributors with sign and contribution and **share of sum of positive contributions** from the largest 1 and 5 taxa (not shares of net signed total). Also aggregate genus prefix contributions as exploratory morphological taxon grouping, no phylogenetic independence claim. Quantify the net gamma contrast after deleting the highest positive contributing taxon as a **descriptive leverage diagnostic**, not a new BH-significant biological discovery. This is not a claim that any taxon physically colonized or was driven away by vegetation.

## Biological interpretation and falsification

- A positive within-wetland PEM gamma result supports an environmental **habitat-architecture association** after excluding areas with no mapped NWI wetlands, not a plant causal experiment. Unmeasured water level/geometry, detection, anthropogenic land use, fish/insect predators and temporal mismatch of NWI still possible.
- If the effect falls sharply or turns negative after wetland restriction, classify the original broad PEM pattern as partly **wetland-category composition confounded**, not a failed analysis or evidence of plant biological harm.
- If one taxon accounts for nearly all positive contributions, narrow the biological claim; else describe a distributed assemblage-level association without inventing a taxonomic replacement mechanism.
- Same-visit pooled acoustic gamma is an incidence proxy, not stable occupancy, survival or reproductive success. Do not assert direct interspecific or genuine ≥3-species causal interactions.
