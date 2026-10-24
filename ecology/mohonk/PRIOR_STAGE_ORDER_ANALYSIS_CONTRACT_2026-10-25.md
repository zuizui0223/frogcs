# Independent empirical ecological test: wood-frog versus spotted-salamander stage ordering
Date 2026-10-25. Data source: Mohonk Preserve original GBIF-IPT Darwin Core Archive, DOI 10.15468/dypfbs, archived v1.1, **13,862 original records**. This is separate from frogcs NAAMP/JAE RC6.

## Question
Do wood-frog (Lithobates sylvaticus) egg detections tend to precede spotted-salamander (Ambystoma maculatum) egg detections in the **same vernal pool and year**, thereby creating repeatable temporal opportunities for wood-frog tadpoles to co-occur with salamander eggs?

Do NOT claim direct consumption, fecundity, competition, fitness or causal effects. The original archive contains no observed predation events and no dragonfly life stages; those cannot be inferred.

## Locked data/QC definitions (after inspecting table schema and marginal counts, before estimating stage-order frequencies)
1. Raw publisher DwC-A archive SHA256 pin recorded from the downloaded exact GBIF-US IPT ZIP; preserve original `occurrence.txt`. Treat coordinates as **generalized pond identifiers**, not precise sampling GPS positions; use unique pair (decimalLatitude, decimalLongitude), accepting 11 unique ponds.
2. Use **2016–2021** because these years have near-systematic per species × lifeStage positive **and zero** records. Earlier years are largely positive-event reporting and cannot be treated as comparable absences or effort.
3. For each pond × original calendar date × species × lifeStage, collapse duplicated records to **positive if any individualCount>0**; a stage is assessed only if at least one row is present. Missing stage records do NOT become zero.
4. Pond × year first egg detection: earliest surveyed date with >0 egg counts; if both wood frog and spotted salamander eggs ever detected, calculate `date(first spotted egg) - date(first wood egg)` in days (positive = wood frog eggs recorded earlier). Also report ties and the case salamander earlier. Earliest recorded appearance is interval-censored by survey dates and should never be called exact laying date.
5. Direct **potential stage encounter** is only **same pond, same original survey date, both wood-frog tadpoles and spotted salamander eggs with >0 counts**. This is an *opportunity for interaction*, NOT evidence of trophic predation. Report event-level counts and unique pond-year counts; repeat separately for Jefferson salamander eggs. Do not infer tadpoles are actively eating eggs without stomach/attack data.
6. Salamander `lifeStage=tadpole` after 2016 has few/no positive rows. Report as an observation gap for reverse predation, NOT evidence larvae were absent.
7. Unit of environmental replication is **pond × year**. Repeated dates do not count as independent years/ponds. Report crude proportions and optional pond-resampled bootstrap intervals (2,000 resamples; RNG seed 2840223), visibly exploratory. Stratify by survey effort (≥2 vs ≥3 distinct sampled dates) and same year; never cherry-pick a favourable threshold.
8. Run metadata QC: raw number of rows, zeros/positives, 11 ponds, original dates, duplicate species-stage-day rows, completeness of compared stage records. Report attrition and whether initial positive is on first visit (left censor).
9. No statistical model of predation or effect of temporal priority on **survival** is licensed: predator abundance, direct feeding, egg damage and larval recruitment outcomes absent.

### Ecological interpretation if first stage order is dominant
If wood frog eggs tend to be detected before salamander eggs, and wood-frog tadpoles and salamander eggs repeatedly co-occur at the same dates, that provides a **recurrent stage-specific opportunity window** consistent with the previously demonstrated Lithobates sylvaticus tadpole predation on Ambystoma maculatum eggs (Takahashi & Ruszala 2023, DOI 10.1002/ece3.10427). This is not evidence that predation occurred at Mohonk. Contextual environmental conditions, predator phenotypes and the year-to-year timing of water filling may modify the window but are not present in the source GBIF Occurrence table.

### Literature constraint on novelty
Carroll et al. (2023; Oikos, DOI 10.1111/oik.09773) already measured calling and larval temporal overlap for 9 frog species at 8 ponds over 6 years; Rudolf et al. (2018; DOI see source) also studied distributional phenology interactions. Our study must not present the **idea of cross-life-stage overlap** as wholly novel. The nontrivial question is directed, trophically verified stage ordering and how specific enemy guilds are affected by measured pond conditions, which this survey alone cannot prove.
