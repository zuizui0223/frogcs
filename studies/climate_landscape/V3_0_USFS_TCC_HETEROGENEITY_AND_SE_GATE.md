# v2.9–v3.0: two independent environmental measurements diverge at Iowa's five mapped NLCD forest-loss cells

**2026-10-08, experimental environmental-source audit.** This work does not change RC6, reopen the negative route-scale climate prediction, or infer amphibian habitat-use effects. Sites were selected **after** inspecting older NLCD C1V0 mapped transitions and are NOT independent random samples.

## Completed USDA quantitative tree canopy pixels, source verified

The [v2.9 USFS Science TCC source-only Actions run](https://github.com/zuizui0223/frogcs/actions/runs/37770883686) passed: original year-specific **v2025.6 Science Tree Canopy Cover** images for 2011, 2012 and 2013, 30m EPSG:5070 exactly matched to the original NLCD change-cell grid, with original catalogue hashes. Source [receipt/artifact](https://github.com/zuizui0223/frogcs/actions/runs/37770883686/artifacts/11547512233).

At **route 360104, stop 3 (SiteID 6613)**, three originally C1V0-labelled forest→nonforest cells had USDA Science TCC values:

| 30m mapped cell | 2011 | 2012 | 2013 | Change 2011→2013 |
|---|---:|---:|---:|---:|
| 1 | 23% | 9% | 8% | **−15 pp** |
| 2 | 35% | 8% | 6% | **−29 pp** |
| 3 | 9% | 3% | 2% | **−7 pp** |

All three show model-estimated canopy decline. Yet separately postprocessed **NLCD TCC** is zero in all three cells and all three years; the source's categorical masking changes the interpretation.

At **route 360412, stop 7 (SiteID 7247)**, two originally C1V0-labelled forest→nonforest cells had Science TCC 3%→3% and 3%→3% from 2011 to 2013, **no change**; NLCD TCC is zero throughout. At this nominal site, the old forest-class fraction also rose in the aggregate despite some gross loss cells.

**Interpretation:** The five category transitions are **heterogeneous**. A minority of source-selected locations, especially the field/forest edge at 360104, have quantitative canopy decline signals; others appear boundary/classification transitions without quantitative canopy decline. Neither TCC model is independent *ground truth*: different remote-sensing pipelines may share Landsat source imagery, and forest canopy percent is not necessarily frog breeding habitat. The five pixels were preselected by the earlier categorical decline and the historical 2001–2015 physical station continuation remains **unverified**.

## Exactly how uncertainty will be assessed (not a hypothesis test)

Official [USFS Science TCC Standard Error original image service](https://imagery.geoplatform.gov/iipp/rest/services/Vegetation/USFS_EDW_TCC_Science_SE_CONUS/ImageServer) reports standard error/ensemble prediction dispersion in 16-bit cells scaled ×100, with missing sentinels 65534/65535. [Year-source CI run](https://github.com/zuizui0223/frogcs/actions/runs/37771382406) verified original **2011, 2012, 2013** v2025.6 catalogue items and U16 encoding. The [pixel readout source-only workflow](https://github.com/zuizui0223/frogcs/actions/runs/37772164538) requires all three annual U16 SEs at each of the same five original mapped cells.

Annual modeled SE should NOT be treated as an automatically calibrated frequentist year-to-year change error; year-model correlation and spatial covariance are not known. The reported `abs(tree canopy change) > SE_t1 + SE_t2` is at best a **descriptive magnitude-versus-marginal-dispersion check**, not a 95% CI, P-value, causal evidence or replication. Do not tune the site/year selection after SE results.

## Still unresolved

- Original Annual NLCD Collection **1.2** pixels and confidence are **not** retrieved. The original [ScienceBase source](https://www.sciencebase.gov/catalog/item/697b9279b66b0197c3043cc3) is confirmed, but the HTTP Range endpoint previously returned HTML rather than the actual large ZIP. Do not silently substitute C1V0 or an unofficial unversioned asset.
- No independently dated route-coordinate or stop-relocation evidence for **2001–2015**. Post-study DNR map-coordinate matching does not prove contemporaneous physical site use.
- No new-route `Counts.csv`, forest-induced acoustic spatial redistribution, reproductive success, movement or anthropogenic climate causal result established.

**Decision:** Keep 360104 as a *source-selected canopy-decline candidate requiring error and ground-source checking*, and 360412 as a *nonreproduced categorical forest-loss candidate*. Neither is a confirmatory ecological effect. If SE/field-station gates remain unresolved, classify environmental tracking versus acoustic-site legacy **not identifiable** rather than searching more forest-loss windows or species.
