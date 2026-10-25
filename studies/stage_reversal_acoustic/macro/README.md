# ONTO-TIME — 独立・発生段階×捕食役割×危険情報マクロ生態学

**Independent macro study, NOT a re-analysis or scientific extension of Beranek (2023), and NOT part of frozen frogcs JAE RC6.**

## Central question

When do life-history stage transitions change **who can eat whom**, how long does a prey remain behaviourally wary after true capture becomes impossible, and can breeding/consumer cues forecast or inform those windows?

Keep three distinct biological responses:
1. **Reciprocal trophic role reversal** (direct observed A(stage1) eats B(stage2), later B(stage3) eats A(stage4)).
2. **Escape and cue persistence** (a prey exits the lethal size window, yet response to predator sensory cues remains).
3. **Cue identity across metamorphosis** (receiver responds similarly or differently to predator stage-specific odor or acoustic signals).

A fourth, weaker dataset class is **observation-level seasonal contact opportunity**. It can reveal geography of co-reporting seasons but cannot establish attacks, stage switching, risk perception, alarm function or causal effects. **Do not mix all four as a common response variable.**

## First independent macro analysis: Australia 2018–2023

- Original public GBIF/FrogID, **108 date-scoped source API queries**, 6 latitude bands × 6 years × 3 record streams.
- 1,026,737 frog acoustic-positive **species occurrence rows** (not 1,026,737 unique audio submissions).
- 16,148 explicitly adult Odonata occurrence rows; 114,179 Odonata rows with known months regardless of life-stage metadata. 263 year-only, month-missing odonate records were identified and excluded, not counted as biological zeros.
- **34/36** prespecified qualifying band–year panels.
- Month-fraction overlap: mean observed 0.445764, 12-month rotation descriptive baseline 0.442050, excess **+0.003714**; **17/34** positive, **17/34** non-positive. There is no consistent nationwide surplus alignment.
- Geographic contrast in *reported* seasonal alignment: excess mean +0.097300 in 32–26°S (5/6 eligible years positive), but −0.133600 in 14–10°S (0/4 eligible years positive). These geographically heterogeneous reporting-season differences are **exploratory**, post-selected, and affected by observation/annotation effort. Not a causal latitude effect or stage-reversal result.
- Explicit-Adult vs all-Odonata monthly overlap differs by average **−0.060541**, emphasizing nonrandom observation of stages.
- No pre-registered independent holdout or calibrated uncertainty interval yet. An independent result here means original self-constructed source panel, **not a confirmatory ecological inference**.

## New independent source-critical ecological checks (2026-10-25)

**Otago Harbour intertidal (Mouritsen et al. 2011)** is a *different ecosystem*, not more observations from Preston's California pond, and the 2024 GitHub repository is a mirror of the original 2011 dataset. Original typed data: **180 nodes, 1,924 links** with 10 different interaction categories. Literal `Predation` accounts for **1,206 links**, not all 1,924. Across all categories at species-and-stage level, 50 pairs have reciprocal links and 27 have stage-mismatched reciprocal directions; **all 27 involve parasite source groups** (Trematode or Acanthocephalan). Keeping **only original `LinkType=Predation`** reduces reciprocal pairs to **12** and stage-different pairs to **zero**. All original `LinkEvidence` cells are blank, so no attack observation can be certified directly from that source. This is **type conflation in a network of host-parasite energy flows**, not direct evidence for 27 free-living ontogenetic trophic switches. [Original source receipt and exact all-50 link-type classification](results/OTAGO2011_ORIGINAL_STAGE_RECIPROCITY_PARASITE_CLASS_V0_1.json); [pinned source code](audit_otago_original_stage_edges.py), [8/8 source-replay QA](https://github.com/zuizui0223/frogcs/actions/runs/40169870840).

**Australian post-hoc stage-label sensitivity:** Under the exact same 34 original eligible latitude×year panels, the year-specific seasonal-overlap surplus changes sign in **9/34** when explicitly Adult-tagged Odonata are replaced by *all* Odonata with known month. Mean rotated surplus is **+0.003714** (Adult only) vs **+0.020152** (all; 22/34 panels positive vs 17/34 adult). The 32–26°S extreme remains positive in both streams (**+0.097300 / +0.107502**) and 14–10°S extreme remains negative (**−0.133600 / −0.151796**), but far-north original 2018/2020 panels failed the original Adult minimum and its early-period sensitivity has only **one eligible year**. This is an explicit **post-hoc reporting/annotation robustness check**, not external validation or the acoustic cue tracking an actual predation transition. [Auditable monthly source robustness](results/AU_36_PANEL_POSTHOC_STAGE_LABEL_AND_ERA_ROBUSTNESS_V0_1.json), [pure-Python replay](analyze_au_phase_annotation_era_sensitivity.py), [8/8 CI PASS](https://github.com/zuizui0223/frogcs/actions/runs/40169870769).

**Implication for the independent macro question:** A genuine developmental role switch cannot be inferred from the existence of stage labels plus reciprocal trophic links without considering `interaction type`, `evidence strength`, `named species/stages`, and `time/space`. Even after source taxonomy and ontology are correct, habitat/effort and behaviour remain missing in the current cross-systems. See [the Japanese source-based scientific synthesis](results/ONTO_TIME_ORIGINAL_STAGE_CUE_MACRO_SYNTHESIS_20261025.md).

## Original-data assets and auditability

| Purpose | File |
| --- | --- |
| Source requests and exact monthly counts | [108 original GBIF monthly facets](results/ORIGINAL_GBIF_AU_6LAT_6YEAR_3STREAM_MONTHLY_V0_1.json) |
| All 36 panel results | [36-panel results](results/AU_36_PANEL_STAGE_ACOUSTIC_PHASE_RESULTS_V0_1.json) |
| Latitude × year compact summary | [6-band CSV](results/AU_36_PANEL_SUMMARY_V0_1.csv) |
| Full biological interpretation / limitations | [Scientific result](results/INDEPENDENT_MACRO_SCIENTIFIC_RESULT_20261025.md) |
| Original analysis reproduction | [Pure-Python runner](analyze_australian_phase_atlas.py) |
| Multi-system hypothesis and clock registry | [9-context comparison register](registry/COMPARATIVE_INTERACTION_CLOCK_ATLAS_V0_1.json) |
| Design specified before 36 panels | [Frozen exploration scope](FROZEN_GEO_YEAR_SOURCE_DESIGN_V0_1.json) |

Reproduce without downloading raw point occurrences:

```bash
python studies/stage_reversal_acoustic/macro/analyze_australian_phase_atlas.py --out /tmp/onto_time_result.json
python -m unittest discover -s studies/stage_reversal_acoustic/tests -p "test_australian_macro_stage_phase.py" -v
```

GitHub Actions: [original-source-derived **11/11 tests PASS**, original 36-panel exact-readback PASS](https://github.com/zuizui0223/frogcs/actions/runs/40163951946). No sensitive threatened-species point coordinates distributed.

## Independent comparison systems

The nine named case contexts include direct reciprocal predation (frog×dragonfly, asp×bleak, predatory mites), a partially modelled gape-based role reversal (pike×stickleback), experimental light×stage-dependent fish/frog exposure (Xenopus×Gambusia), odor-memory generalization vs reset across beetle/salamander metamorphosis (wood-frog tadpole receiver), size refuge with persistent nonconsumptive response (Zhangixalus×Notonecta), and nonreciprocal giant-salamander larval predation control.

**Nine documented contexts do not represent nine exchangeable effect sizes; we did not fit a pooled trophic-reversal meta-model.** Original study data for novel sensory-response systems are documented but not yet jointly available for such a model.

## Second independent original-data layer: original stage-coded trophic edges × measured cue memory

**Source-supported, but do not pool numerical endpoints across different experiments.** The new integration is documented in [the original-evidence macro synthesis (Japanese)](results/ONTO_TIME_ORIGINAL_STAGE_CUE_MACRO_SYNTHESIS_20261025.md).

**Stage-resolved food-web reconstruction** — Independently replayed the [actual 2012 Quick Pond original source](https://github.com/globalbioticinteractions/preston2012), pinned commit `10676b041317d933f16c089b819f6669da42396b` and two file Git blob hashes. Of **1,905** source food-web links, **1,000 predation links** comprise **50 observed / 40 inferred / 910 modelled** source evidence categories. Under species-level stage labels, **126** non-self directed predation links form **68** species pairs, **11** of which have links in both directions. Only **one** reciprocal pair has two source-tagged `observed` directions, and it is **larval *Anax junius* ↔ larval *Taricha torosa***, not an ontogenetic switch. **Zero reciprocal species pairs have observed-to-observed trophic role transition across distinct stages.** e.g. larval *Anax junius* → larval *Anaxyrus boreas* is source-observed, but the reverse adult-toad → dragonfly links are only source-modelled. **This is an evidence-quality finding, not proof that natural stage reversals do not exist.** Data: [all 11 pairs and link evidence](results/PRESTON2012_ORIGINAL_STAGE_RECIPROCITY_EVIDENCE_TIER_V0_1.json). Re-run: [pinned original parser](audit_preston_original_stage_edges.py), [8/8 CI PASS](https://github.com/zuizui0223/frogcs/actions/runs/40167052076).

**Source-original predator-stage odor learning experiment** — Retrieved 2024 Thapa et al. *Behavioral Ecology* source Excel (DOI [10.1093/beheco/arae014](https://doi.org/10.1093/beheco/arae014)) from **NLM/PMC official open data** `PMC10965031.1` (SHA256 `a200b66072c5de204efe91536066d66c9cf8b513c5075c321fc44391544d9fa5`). 588 published original rows across two experimental sheets (**308 beetle, 280 salamander**), each 18 independently conditioned pails (six per odor-training arm). Source-recorded tested n in article is larger (360 / 357); discrepancy unconfirmed. Salmonander control had one missing adult cue pail; no imputation. Equal-pail analysis of `post-pre` movement shows:

| Predator source | Cross-stage cue transfer minus sham | Same-stage minus sham | Cross minus same (10k pail-bootstrap 95% percentile) |
| --- | ---: | ---: | ---: |
| Beetles | **−3.709** | **−4.130** | **+0.421** [−2.261,+3.520] |
| Salamanders | **+0.789** | **−6.044** | **+6.834** [+0.026,+13.482] |

Negative means stronger movement suppression relative to untrained sham exposed to same cue. Both average transfer directions preserved in the raw. Salamander source-derived cross–same difference maintains positive sign under all 18 leave-one-pail-out evaluations. **Crucial post-hoc hierarchy sensitivity:** all six original salamander clutches each contain one pail per training arm. Paired-by-clutch cross-minus-within stage = +6.834 (5/6 clutches positive), but 95% df5 Student-t interval **[−5.547,+19.214]** and six-clutch bootstrap interval **[−1.004,+15.985]** both include zero. Therefore the barely positive pail-bootstrap lower bound **does not survive the stronger clutch-level uncertainty audit**. This is a directional original-observation result, NOT robust inferential evidence for a universal salamander-specific cue reset. These are **chemical predator odors**, not frog acoustic alarm signals and not experiments on the attack-direction switch. Raw XLSX itself is not redistributed. [Original pail-level 10k bootstrap results](results/THAPA_ORIGINAL_588_PAIL_REANALYSIS_20261025.json), [reproduce from NLM](analyze_thapa_original_pail.py), [8/8 CI PASS](https://github.com/zuizui0223/frogcs/actions/runs/40167052212).

**Source accessibility:** Urushihara & Takatsu 2026 size refuge/backswimmer and Baker 2025 salamander predation Dryad original CSV downloads remain 401/unavailable (6 of 7 originally identified files); source metadata, headers/experimental design from public README are not original outcome tests.

**New core framing:** ecological risk transition R(stage, environment), consumer stage-specific receiver recognition I(stage, modality) and realized spatiotemporal opportunity O(region,time) are *distinct state dimensions*. In no source are all three observed jointly for the same species pair/site/time. Therefore a universal joint effect or frog-call warning role remains a **future test**, not an established effect.

## Next scientifically discriminating macro dataset

The required primary source is a **stage-specific directed trophic event**:
`source_study_id, site, date/time, species_A, A_stage, species_B, B_stage, predator, prey, actual_attack_observed, opportunity/effort`. Acoustic/olfactory reception is a *separate* `cue_event, receiver_response, control` table with verified common event/site/time keys.

Only after that source ledger is independently populated should we test whether stage transitions cause a genuine direction switch more often than one-way predation or size escape, and separately whether receivers update their risk response to those transitions.

**Source limitation as of 2026-10-25:** National GBIF stage annotation is insufficient to construct this directed event table. GloBI interaction gaps are not biological absence. The IWS 2018–19 site×visit original call table remains unacquired. No claim that frog mating calls are an evolved interspecific alarm signal.

The original frozen RC6 mainline remains unchanged; keep development in this Draft PR / separate lane.
