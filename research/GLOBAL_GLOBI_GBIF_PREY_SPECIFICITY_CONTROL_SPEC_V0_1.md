# Additional ecologically specific null: documented GloBI prey versus same-guild undocumented comparators

Date 2026-10-25. **Exploratory *after* reading the first within-pair month-shift results**. Distinguishes ordinary seasonal co-reporting from possible added *trophic partner specificity*. This is not independent hypothesis preregistration or new data.

## Why

At the initial 1° GloBI×GBIF stage analysis, 16/18 documented pair patterns exceeded their own 11-month phase-shift averages, but 10/18 were adult dragonfly→adult dragonfly. Two flying insects with overlapping emergence seasons and shared observers can produce strong month concordance **without any trophic link**. A comparator must use the same predator, same prey guild and stage, and similarly documented geographic-year occupancy.

## Exact diagnostic

- Use same pinned GloBI 2026-09 MD5 source and experimental GBIF August 2026 Anura/Odonata 1° month/year grid, same fixed 18 eligible nonself predator×prey×stage directed GloBI patterns.
- Alternative prey candidate: a **different GBIF taxon** of the *same GloBI-assigned prey guild* and the same normalized prey stage. Exclude the focal predator species, focal prey and **all pairs with that predator in any complete-stage GloBI edge of the available 881-pattern set**. This exclusion says *undocumented in our complete-stage indexed subset*, not known biological noninteraction. Taxonomic matches outside this subset might still be documented predators.
- Before viewing candidate months, match alternative prey on the number of positive GBIF species×stage×1°×month×year cells and its coarse **same grid-year footprint** with the focal predator. Strictly minimize absolute log ratios of these two quantities, select up to five closest among candidates within factors 3× for GBIF monthly reporting volume and 2× for predator-pair shared grid-year cells, requiring at least one shared grid-year. If fewer than two alternative species meet match criteria, return non-estimable for that focal edge, do not automatically broaden bins.
- For each focal and alternative pair compute 1° grid×year×month observed co-reports `C0`, 11 nonzero prey month-rotation `Cd`, and **relative phase-concordance `Q=(1+C0)/(1+mean(Cd))`**. Compare focal Q with the median of up to five matched alternative prey values; report Qf−median(Qcontrols), fraction greater, and bootstrap intervals only if ≥8 distinct focal predator species (otherwise descriptive only).
- Repeat using GBIF minimum **five observations per species-stage-grid-month** as strict sensitivity but retain control membership fixed from threshold-one matching; do not reselect controls after seeing strict overlap.
- Restrict top-level summaries to matched focal pairs; stratify source as Quick Pond/metaweb vs original iNaturalist links. Do not call controls verified non-prey and never infer true dietary specialism from documented source edges + amateur occurrence reporting.
- No causal interpretation, no P-values from pseudo-independent cells, no wetland plant-cover or rainfall inference. If focal Q and matched control Q are similar, phase alignment is likely broadly explainable by non-specific phenology/observer effort; if focal Q is higher, it is an exploratory hypothesis for field verification, not confirmed predation-specific synchrony.

Data outputs: deterministic source/taxonomy coverage QA, exact sample/eligible/excluded controls, `matched_comparator_pairs.csv`, `observed_results.json`, Github CI artifact.
