# NAAMP × NWI: vegetation-specific ecological hierarchies of frog acoustic metacommunities

**Executed and validated 2026-10-23.** Ecology-first observational macroanalysis, NOT a predictive scoring exercise and NOT a new literature reanalysis. 2001–2015 original USGS NAAMP standardized frog acoustics + validated USFWS NWI 250-m mapped vegetation and wetland polygon classes. The JAE RC6 paper, main, SI and submission remain frozen and unchanged.

## New biological conclusion

**Mapped wetland vegetation type is associated with local frog acoustic taxon richness across a geographically broad survey network, but the spatial scale of this association depends strongly on vegetation type.** Local emergent-wetland/PEM signals survive adjustment for overall wetland polygon cover and other mapped plant/wetland classes; woody wetland signals do not. A major non-obvious result is a **sign reversal across spatial scales**: PEM–frog richness covariance is positive among stops of the same route-night yet negative among state means. This is descriptive scale-dependent association, not a demonstrated direct effect of plants on frogs.

## Source authority and structure

- Original standardized NAAMP complete 10-stop surveys: **7,848**; NWI/sound/temp complete nights: **6,236**, giving **62,360 stop × night records**, **499 physical monitoring routes**, **20 States**.
- Mapped NWI source: **5,147 SiteIDs** across 12 validated geographic shards; original outcome-blind source [Actions #39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).
- Physical mapped site counts: total wetland **4,743**, PEM emergent **1,286**, woody/shrub wetland **2,682**, aquatic-bed **66**. These *overlap*: **844** physical sites overlap both woody and PEM polygons, **33** overlap PEM and aquatic-bed. Absence of mapped class is NOT true absence of plants; percentages are buffer polygon coverage NOT observed 2001–2015 living plant cover.
- Taxon richness is number of NAAMP calling-index monitoring taxon labels per surveyed stop, **not abundance or stable demographic occupancy**. Sites surveyed sequentially. Year effects and local conditions are not all identified.

## Result 1: Within-night vegetation–richness association (same landscape and weather)

For each vegetation class, compare mean acoustically detected taxa at mapped-positive versus mapped-negative stops *within the exact same 10-stop survey night*. Average the resulting effect once per independent route (not as 62,360 independent records); route Student-t CI, 4,999 route sign flips and BH FDR over all eight pre-fixed class × calling-strength tests.

| NWI mapped class | CI>=1 richness difference in taxon units/stop | 95% route CI | Independent routes | CI>=2 difference |
|---|---:|---:|---:|---:|
| **PEM emergent** | **+0.27150** | +0.22505 to +0.31795 | **388** / 20 States | **+0.17637** |
| Aquatic-bed | +0.24006 | +0.10792 to +0.37220 | 46 / 12 States | +0.17041 |
| Woody/shrub wetland | +0.10737 | +0.05727 to +0.15747 | 405 / 20 States | +0.08285 |
| Any mapped wetland | +0.21407 | +0.13833 to +0.28981 | 227 / 20 States | +0.11788 |

All eight fixed BH q values were below 0.01, but **these are separate, overlapping, unadjusted contrasts**; aquatic-bed is sparse and repeated exposure at 66 mapped physical sites cannot be multiplied into independent replications. PEM CI>=1 was positive in **19/20 States** with mapped positive-negative comparison, and both retrospective era splits (2001–09/2010–15) had the same sign. This is real macroecological acoustic richness structure, not causation.

Source result: [Actions #39879561078](https://github.com/zuizui0223/frogcs/actions/runs/39879561078) SUCCESS, original linked source [Actions #39879084643](https://github.com/zuizui0223/frogcs/actions/runs/39879084643) SUCCESS.

## Result 2: Vegetation-type hierarchy after simultaneously adjusting other mapped types and local conditions

This is an explicitly **post-positive-result** explanatory analysis, NOT preregistration or independent confirmation. Fit within-10-stop-night fixed-effects count-mean OLS on exactly the same **62,360** site records, controlling *jointly* for binary PEM, woody/shrub, aquatic-bed, total mapped wetland fraction (+10 pp units), stop air temperature, acoustic masking and nine survey stop-position effects. All original nights and zero-call stops retained. Whole physical route equal weights, 499-route clustered uncertainty; independent 20-State cluster sensitivity and 20 leave-one-State-out fits. BH over **8** fixed adjusted coefficients.

| Habitat covariate conditional on all others | CI>=1 adjusted difference | Route CI95 | State CI95 | BH q | CI>=2 adjusted difference |
|---|---:|---|---|---:|---:|
| **PEM present** | **+0.23777** | **+0.19648 to +0.27906** | **+0.17716 to +0.29837** | **1.15×10^-25** | **+0.15042** |
| Aquatic-bed present | +0.21273 | +0.08451 to +0.34095 | +0.06695 to +0.35850 | 0.00191 | +0.16345 |
| Woody/shrub present | +0.03233 | -0.01637 to +0.08102 | -0.03008 to +0.09473 | 0.193 | +0.03162 |
| Total mapped wetland fraction +10 pp | +0.03744 | +0.02172 to +0.05316 | +0.01806 to +0.05682 | 7.40×10^-6 | +0.02728 |

The adjusted strong-call PEM confidence interval is **+0.12015 to +0.18069** under route clustering, **+0.10679 to +0.19405** under 20-State clustering. The **PEM effect stays positive in all 20 leave-one-State-out analyses** in both call-strength definitions: CI>=1 coefficient range **+0.22649–+0.25524**, CI>=2 **+0.14322–+0.16218**.

**Nontrivial distinction:** the initial woody class +0.107 richness contrast falls to +0.032 after conditioning on other mapped wetland habitat attributes (non-supported), whereas PEM and aquatic-bed retain distinct **conditional statistical** richness associations. Other unmeasured water/hydroperiod/plant-quality confounders remain possible. Aquatic-bed source-site scarcity remains a fundamental limitation even with a positive State CI.

Source: [Actions #39880097620](https://github.com/zuizui0223/frogcs/actions/runs/39880097620) SUCCESS, aggregate [result artifact](https://github.com/zuizui0223/frogcs/actions/runs/39880097620/artifacts/12470082517).

## Result 3: Exact hierarchical partition of where vegetation and frog variability occur

Variance of mapped continuous PEM fraction versus local frog acoustic taxon richness, **equal weighting of 20 States, then equal routes, nights, stops**:

| Variance level | PEM mapped 250m fractional cover | CI>=1 frog richness | CI>=2 frog richness |
|---|---:|---:|---:|
| Between States | 4.65% | 5.54% | 3.24% |
| Between physical routes within State | 19.99% | 15.35% | 13.33% |
| Between survey nights within route | 0.06% | 24.19% | 28.33% |
| Between ten stops of one route-night | **75.29%** | **54.93%** | **55.10%** |

The NWI source is **static by construction**, so its near-zero temporal component is unsurprising and should NOT be sold as a biological discovery. What matters is the scale of vegetation–frog *covariance* and a significant within-night richness association. Equal-route nationwide weighting independently gives PEM within-night 76.91% and CI>=1 richness within-night 54.01%, showing this variance hierarchy does not depend on giving small States equal national weight.

## Result 4: Exact plant–frog covariance confirms scale-dependent sign changes

We decomposed actual across-stop covariance using the law of total covariance (independent numerical reconstruction against direct weighted covariance, 8 habitat × calling-index pairs, two geography weightings). The fractions below are **signed contributions with absolute-value denominator**, NOT four additive percentages of net covariance.

| Spatial/temporal level | Binary PEM × CI>=1 richness signed covariance | Contribution as percent of sum of absolute components |
|---|---:|---:|
| **Among States** | **−0.01257** | −18.97% |
| Routes within State | +0.01275 | +19.24% |
| Between nights within route | −0.000129 | −0.19% |
| **Stops within same night** | **+0.04082** | **+61.59%** |

For strong calling, the **local stop-level absolute share = 65.09%**, while between-State covariance remains negative. Under alternate equal-route weighting, CI>=1 local stop share is **64.71%**, again positive, and between-State covariance remains negative.

This is a **Simpson-like cross-scale sign reversal**: geography-scale average environments and route-local habitat contrasts can point in opposite directions. It does not require direct interspecific competition or indicate plants cause the differences.

**Habitat architectures show distinct signatures** in the CI>=1 covariance decomposition:
- **PEM:** within-night stop covariance dominates (61.6% of absolute component magnitude), with an opposing negative State component.
- **Woody/shrub wetland:** covariance is concentrated mainly **among routes within State (68.8%)**, with only 28.9% within-night stops. Its local adjusted class coefficient did not pass FDR.
- **Aquatic-bed:** within-night stops 52.3%, routes 37.3%, but only 66 mapped physical sites.
- **Total wetland extent:** roughly State 31.8% / routes 33.2% / local stops 35.0%, i.e. a genuinely multi-scale broad habitat signal.

Source: [Actions #39880672474](https://github.com/zuizui0223/frogcs/actions/runs/39880672474) SUCCESS; [numerical covariance artifact](https://github.com/zuizui0223/frogcs/actions/runs/39880672474/artifacts/12470461797).

## Result 5: Community and biological organization are not reducible to vegetation richness alone

For all NWI-complete route-nights, equal-route descriptive means:
- **CI>=1** stop alpha 1.4353 units, whole 10-stop gamma 3.7434 units, normalized Whittaker beta 0.2410 (zero-gamma nights retained in richness, not beta).
- **CI>=2** alpha 0.8240, gamma 2.3489, Whittaker beta 0.3178. The higher normalized beta for stronger calls partly reflects sparse detection; not necessarily higher ecological species sorting.

Earlier distinct-source-grain evidence was deliberately **not promoted to causality**:
- First-order mapped PEM taxon-specific strong-call placement: **5 positive / 25** eligible monitoring taxa, FDR supported.
- Second-order residual pair-network after crossfitted habitat and exact species/stop margins: **43/127** CI>=1 signed acoustic edges (20 positive, 23 negative), **14/57** CI>=2 (9 positive, 5 negative).
- Global irreducible third-order centred acoustic-moment excess: **not established** (CI>=1 P≈0.695; CI>=2 P≈0.108), and fish/insect predators are not jointly observed or experimentally manipulated.

The earlier richness-adjusted PEM-boundary Sørensen macroanalysis had a **null boundary effect** (+0.087 pp, route P=.714, 285 routes). It does not contradict the positive within-route *alpha richness* association: local number of calling taxa and residual compositional dissimilarity are **different levels of organisation**.

## Ecological spine and publication boundaries

1. **Local species-number organisation:** mapped structurally different wetland vegetation contexts co-vary positively with local acoustic taxon richness, especially PEM, even after adjustment for mapped wetland area and conditions.
2. **Scale dependence:** plant–frog association arises primarily at local stop/landscape levels; coarse among-State PEM gradients can have the **opposite sign**. Ignoring hierarchical grain could conceal or reverse the pattern.
3. **Network organisation:** recorded taxon-specific PEM affinities and residual pair co-calling networks are real exploratory acoustic structures, but are not identifiable biological interactions, fish/odonate mechanisms or a supported causal third-order network.

These are **nonpredictive source-linked macroecological findings**. NWI polygons are **not time-matched plant species/cover**, and the source only measures *calling*, not adult/tadpole occupancy, breeding outcome or survival. Geographic study-state samples vary widely. No new source data were harvested, no new papers were reanalysed, and JAE RC6 remains untouched.

## Reproducible location

- Main code and variance/paired contrasts: `exploration/run_naamp_hierarchical_vegetation_macro_v0_1.py`; [Actions #39879561078](https://github.com/zuizui0223/frogcs/actions/runs/39879561078) (PASS); [artifact](https://github.com/zuizui0223/frogcs/actions/runs/39879561078/artifacts/12470036309).
- Source-adjusted 15-covariate within-run model: `exploration/run_naamp_multitype_vegetation_hierarchy_v0_1.py`; [Actions #39880097620](https://github.com/zuizui0223/frogcs/actions/runs/39880097620) (PASS).
- Covariance hierarchy: `exploration/run_naamp_plant_frog_covariance_hierarchy_v0_1.py`; [Actions #39880672474](https://github.com/zuizui0223/frogcs/actions/runs/39880672474) (PASS).
- All protocols frozen before each *respective new analysis*; the adjusted/covariance follow-ups are explicitly labelled **post-readback**, and none is represented as independent confirmatory biological replication.
