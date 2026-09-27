# Novelty audit v0.6 — RC7 matrix-scale active-community expansion

## Reviewer-safe novelty statement

Rainfall effects on anuran calling, acoustic activity and observed richness are established and are **not** the novelty claim. Short-term variation in anuran calling-community composition and beta diversity is also established, and wetland inundation has already been linked to frog richness, abundance, chorusing and community composition.

The RC7 contribution is narrower and more structural:

> **It resolves a familiar rainfall-associated change into where new acoustic participation enters a fixed spatial community matrix, and shows that the realized community expands simultaneously across sites and species without a detectable collapse of among-site differentiation.**

The exact matrix decomposition itself is algebraic; the empirical novelty is the observed distribution of the rainfall-associated slope: approximately **92% crosses at least one spatial and/or taxonomic matrix boundary**, whereas about **8% is within-core rearrangement**.

## What prior work already owns

### Rainfall → calling activity and richness

**Xie et al. (2017, Ecological Indicators; DOI 10.1016/j.ecolind.2017.06.015)** estimated frog community calling activity and species richness from acoustic data and reported lagged rainfall associations with both quantities.

Therefore RC7 does not claim novelty for:
- rainfall-sensitive frog calling;
- lagged rainfall effects on acoustic activity;
- rainfall-associated changes in observed frog richness.

### Fine-scale acoustic community composition and beta diversity

**Sugai et al. (2021, Journal of Animal Ecology; DOI 10.1111/1365-2656.13399)** analysed assemblage-wide calling activity and short-timescale changes in species composition, explicitly including beta-diversity questions.

Therefore RC7 does not claim novelty for:
- treating a calling assemblage as a community-level object;
- fine-temporal variation in calling-community composition;
- beta diversity of acoustic anuran assemblages.

### Wetting/inundation → richness, chorusing and composition

**Sarker et al. (2022, Ecological Indicators; DOI 10.1016/j.ecolind.2022.109640)** showed that inundation can increase frog richness and abundance, alter community composition, and change chorusing in species- and site-specific ways.

Therefore RC7 does not claim novelty for:
- wetting-associated increases in frog richness;
- hydrological effects on community composition;
- species- and site-specific chorusing responses to wetting.

### Precipitation and alpha–beta–gamma diversity are not a new combination

Outside anurans, **Zhang et al. (2014, PLOS ONE; DOI 10.1371/journal.pone.0093518)** jointly analysed alpha, beta and gamma diversity along a precipitation gradient in grassland communities.

Therefore RC7 does not claim novelty merely because precipitation and alpha/beta/gamma diversity appear in the same paper.

## What RC7 adds beyond those comparison classes

### 1. One environmental association is localized across a fixed species × site matrix

The ten aligned NAAMP stops create a repeated spatial sampling unit. RC7 asks where the wet-minus-dry difference enters that same unit:

- does another stop become acoustically active?
- does an already-active stop deepen taxonomically?
- does a route-existing species spread to a newly active stop?
- does a route-new acoustic participant appear at an already-active stop?
- or are detections merely rearranged within the same active core?

This localization is finer than reporting total activity, richness, composition or beta diversity alone.

### 2. Spatial footprint, local alpha and route gamma expand together

Rainfall contrast is positively associated with:
- active-stop number;
- richness per active stop;
- route-level active richness.

The same-stop analysis shows that local deepening persists when stop identity and active status are held fixed.

### 3. Expansion does not present as detectable homogenization

The paper does not use a single non-significant beta test as evidence of invariance. It combines:
- pairwise Sørensen;
- Simpson turnover;
- nestedness-resultant dissimilarity;
- normalized Whittaker beta;
- a separately frozen practical-equivalence test for active-matrix fill.

The result is a specific joint pattern: the active community becomes larger while measured among-active-site differentiation does not detectably collapse and matrix fill remains within the prespecified equivalence margin.

### 4. The incidence increase is empirically concentrated at matrix boundaries

The four-way accounting identity must sum to total incidence change, but it does not require any particular coefficient shares.

Observed shares:
- corner expansion: **36.9%**;
- spatial spread: **15.2%**;
- taxonomic deepening: **39.9%**;
- within-core rearrangement: **8.0%**.

Thus the principal empirical statement is not the identity itself but that **about 92% of the rainfall-associated incidence slope opens at least one boundary of the observed active matrix**.

### 5. The pattern is geographically robust without pretending to be geographically uniform

Across all 21 leave-one-state-out refits, active-footprint, local-alpha and route-gamma coefficients remain positive and all corresponding 95% confidence intervals remain above zero.

State-specific slopes nevertheless vary, including localized opposite-direction intervals for some responses. The correct claim is therefore:

> **robust to omission of any single sampled state, with local geographic heterogeneity**

—not “positive in every state”.

### 6. The result is not confined to the programme's 0–3 day rain-target window

After the NAAMP protocol feature was identified, a frozen design sensitivity required the drier member of a matched pair to occur at least four days after rain.

The resulting subset retained:
- **1,769 pairs**;
- **425 routes**;
- **20 states**.

All three headline coefficients remained 95%-CI positive:
- active stops: **0.374 [0.198, 0.551]**;
- local alpha: **0.0839 [0.0140, 0.154]**;
- route gamma: **0.289 [0.133, 0.446]**.

This is a robustness result, not a causal identification strategy.

### 7. Mechanistic interpretation is triangulated rather than reverse-engineered from a failed trait search

The attempted species-level activation-geometry trait failed a frozen rain-specificity placebo gate and remains demoted.

Independent literature instead provides biological plausibility for heterogeneous activation:
- species-specific meteorological response surfaces;
- rainfall- and flood-dependent breeding strategies;
- different rainfall thresholds and lags;
- inundation-driven habitat activation;
- moisture/hydration as a plausible proximal constraint.

RC7 therefore uses **heterogeneous activation thresholds** as a Discussion hypothesis, not as a fitted mechanism.

## Why the conjunction matters

None of the following alone is sufficiently novel:
- rain changes frog calling;
- rain changes richness;
- beta diversity can be analysed at short timescales;
- precipitation can affect alpha/beta/gamma diversity;
- species × site matrices can be decomposed.

The contribution is the conjunction:

> **A short environmental association recruits acoustic participation across both the spatial and taxonomic boundaries of a fixed landscape sampling matrix, while local compositional differentiation does not detectably collapse.**

That is the ecological result editors should evaluate.

## Closest alternative interpretation

A skeptical interpretation is that rainfall simply amplifies detectability or chorus intensity in an unchanged community.

RC7 constrains this interpretation because:
- more stops become active;
- richness increases at the same numbered stops active in both surveys;
- ~71% of the local-alpha slope lies beyond the second species;
- ~92% of incidence growth crosses a matrix boundary;
- recorded hearing/noise/wind and additional acoustic-quality sensitivities retain footprint/alpha/gamma effects;
- the geographic leave-one-state-out gate strong-passes;
- the three-day protocol-window sensitivity strong-passes.

Unmeasured species-specific detectability remains possible and is retained as a limitation.

## Remaining novelty risks

1. **The driver is familiar.** The first page must move immediately from “rainfall affects calling” to the matrix-localization question.
2. **The novelty is a joint structural pattern, not a new causal mechanism.** Do not oversell mechanistic identification.
3. **The beta component includes null results.** Novelty rests on the conjunction with positive footprint/alpha/gamma, matrix-fill equivalence and boundary-crossing incidence growth, not on P > .05 alone.
4. **The matrix decomposition can look tautological.** Always distinguish the accounting identity from the empirical coefficient allocation.
5. **The active-community framing is observation-process sensitive.** This is a feature of the biological question, but the manuscript must continue distinguishing acoustic realization from latent occupancy or abundance.
6. **Post-opening extensions require transparency.** The strength is frozen decision rules, retained failures and robustness convergence, not a claim that every analysis was preregistered.

## Priority language

Preferred:
- “resolve where a familiar rainfall-associated increase enters the spatial community matrix”
- “two-dimensional spatial and taxonomic expansion”
- “boundary-crossing growth of the behaviourally realized acoustic community”
- “expansion without detectable homogenization”
- “robust to omission of any single sampled state”
- “not confined to comparisons entirely within the 0–3 day protocol-target window”
- “heterogeneous activation thresholds are a biologically plausible hypothesis”

Avoid:
- “first evidence that rain increases frog richness”
- “first alpha–beta–gamma analysis of precipitation”
- “rainfall causes community expansion”
- “the response occurs in every state”
- “beta diversity is unchanged”
- “hydration mediates the effect”
- “the matrix decomposition proves mechanism”

## Preferred one-sentence novelty statement

> **We resolve a well-established rainfall–calling association into the geometry of a spatial community response: recent-rain surveys recruit both sites and species into the behaviourally realized community, about 92% of additional incidence growth crosses spatial and/or taxonomic matrix boundaries, and measured local differentiation does not detectably collapse as the active community expands.**
