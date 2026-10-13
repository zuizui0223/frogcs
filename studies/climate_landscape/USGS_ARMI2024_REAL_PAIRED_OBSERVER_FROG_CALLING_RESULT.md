# Real 2024 USGS ARMI frog calling: same-site near-simultaneous observers and detected community agreement

**Executed on actual CC0 USGS original survey rows, 2026-10-14 JST. This is a descriptive observational comparison, NOT a randomized device experiment, causal ecological mechanism, new Blanchard's cricket frog recolonization discovery or extension of frozen JAE RC6/main.** Independent frogcs draft PR #135, original CEWH Murrumbidgee source question still pending and its metadata enquiry unsent.

## Authentic public source and frozen rules

- [USGS Roth et al. 2025 / ver. 1.1 April 2026](https://doi.org/10.5066/P19ZCGWM) and [USGS official overview](https://www.usgs.gov/data/amphibian-nighttime-call-data-midwest-armi-cricket-frog-surveys-2024). CC0, original 2024 night call field observations from the upper Midwest, US. [Real source and dictionary preflight run 38422071685](https://github.com/zuizui0223/frogcs/actions/runs/38422071685) verified a direct original **235,391-byte** public release CSV, SHA256 `dafd388c7ccb79e08dbadd37a25c604473a8caf4ff5c8318532740acb56a04e4`; exactly **1,934 source species lines**, **343 original site codes**, **51 observation dates**, **2 human observers** and **2 original methods** `Ear` (naked ear) and `Microphone` (Telinga parabolic mic/headphones).
- Original FGDC dictionary defines `Arrival_time` as **site-local survey start time**, `Number_heard` as count or range of calling individuals, and **NA when no anurans were heard**. Source had **220 explicitly encoded no-frog rows**, each exclusively a no-frog visit, **without falsely setting missing taxa to zeros**. No site, date, observer, species or coordinates are emitted in this audit.
- **Observation unit** is original `Site×Date×Observer` with one start time and method, not each species line. There were **797** distinct source site-date-observer keys; **one** had multiple start times and was excluded rather than joined silently; hence **796** unambiguous valid identified observer-opportunities, of which **220** had explicitly no frogs heard and **576** had ≥1 recorded frog species. This is a reported *detection/no-call* summary, **not evidence of true biological absence or perfect hearing**.
- **Frozen protocol BEFORE reading source species outcomes:** [paired observer/call source design](USGS_ARMI2024_FROZEN_PAIRED_OBSERVER_DETECTION_DISCORDANCE.md), with original [source gate](USGS_ARMI_2024_PUBLIC_SURVEY_OBSERVER_OPPORTUNITY_GATE.md).
- [**Successful actual public data analysis Actions 38423154215**](https://github.com/zuizui0223/frogcs/actions/runs/38423154215) · [source SHA-pinned reproducible code](scripts/analyze_usgs_armi2024_paired_observer_calling_v80.py) · [permanent aggregate executable receipt](receipts/USGS_ARMI2024_REAL_PAIRED_OBSERVER_FROG_CALLING_V80.json). The test suite verified strict source no-frog sentinel/candidate separation, two-observer site/day association, and zero-overlap Jaccard defined only when the union has ≥1 reported species.

## The paired near-simultaneous source result

There are **773** unique site×date values, among which **24** have both independent observers; original starts differ by at most **5 min** (median **0 min**). One pair used the *same* method and was excluded from the planned method-discordant primary contrast. **23 distinct physical source locations each contributed one eligible paired Ear vs Microphone observer–device observation** (not multiple fake independent species lines). Surveyor identity and method are **almost perfectly confounded**, so we deliberately name the contrast *observer–device package*, not an instrument effect.

| Same site/date within five minutes, 23 independent paired source opportunities | Actual number |
| --- | ---: |
| Both reported hearing ≥1 anuran species | **20** |
| Both explicitly reported no anurans heard | **2** |
| Only microphone-side observer reported ≥1 species | **1** |
| Only naked-ear-side observer reported ≥1 species | **0** |
| Mean distinct positively detected species, naked-ear observer | **1.869565** |
| Mean distinct positively detected species, microphone observer | **2.173913** |
| **Equal-source-site paired difference (microphone minus ear)** | **+0.304348 species** |
| 23-site descriptive 5,000-resample percentile 95% interval | **[+0.043478, +0.608696]** |

Paired detected-species richness differences: **6 of 23 sites** had more species reported by microphone-side observer, **1** had more reported by naked-ear observer, and **16** tied (median paired difference **0**). A positive descriptive site-bootstrap interval does **not** establish microphone causality, corrected ecological occupancy or an experimental confidence interval. Weather, sound direction and observer-specific skill remain possible causes.

Among **21 pairs** with ≥1 source-detected species in at least one observer, mean binary detected-species-list **Jaccard similarity was 0.817460** (median **1.0**). Exactly **7/21** had different reported species lists, and **14/21** matched completely. The two pairs where both report no frogs are counted as **separate explicit no-call agreement**, *not* spuriously assigned Jaccard=1. **The strongest interpretation is substantial within-event detectable frog assemblage agreement accompanied by non-negligible observer+method-specific variation.**

## Same-observer temporal repeatability cannot be estimated on the prespecified window

Although the original release contains source records from **306 site IDs with ≥2 distinct survey dates**, the fixed narrower requirement *same physical site, SAME observer+method, on 2 different dates 1–30 days apart* yielded **only 1 date-pair from 1 site**. Hence cross-date, observer-and-method-standardized community turnover is **NOT EVALUABLE** here. Do not convert 306 repeated site names into 306 independent valid matched temporal transitions, relax the 30-day window post-outcome to force a directional result, or call between-observer disagreement the biological turnover baseline.

This disconnect reflects source campaign/site visit design, not proof that frogs lack historical spatial structure.

## Ecological conclusion and source ceiling

- **Supported actual descriptive result:** two independent source observers surveying the same site within minutes typically agreed on the detected anuran species community; mean Jaccard **0.817** among nonempty unions. Yet the choice of observer+listening apparatus affected the observed *species list* at **one third of heard-call paired sites (7/21)**, and an observer-side richness difference existed even during effectively simultaneous observations.
- **Biological mechanism NOT identified:** source pair groups change both observer and method, and species detections are not corrected for undetected calls, weather, microphone amplification or operator competency. Reported no calls are **survey no-call results, not proven amphibian absence**.
- **Fidelity/temporal reassembly NOT identified:** only one within-30-day repeated site×observer×method comparison; no independent repeated calibrated acoustic panel and no wetland local water-level trajectories.
- [Burner et al. 2026](https://doi.org/10.1670/2719523) already found northward expansion of *Acris blanchardi* occupancy in a related 2003–2008 versus 2024 programme. Do **not** rebrand this previously reported distribution change as a new finding or conflate the source with our existing NAAMP/JAE network. The current result is a compact *new descriptive source check* relevant to separating biological and observational variability, not a validated independent manuscript-level ecological mechanism.
- The related [Doser et al. 2026 Minnesota occupancy model repository](https://github.com/doserjef/Doser_et_al_2026_JAE/tree/v1.0.0) explicitly **does not share raw survey observations**; model outputs are not a legitimate replacement for originals.

**Next scientifically defensible step:** only a genuinely new independently accessible, source-defined repeated **same-site same-observer/device** survey-opportunity panel, or paired water-depth logger archive, can test temporal environmental frog-history hypotheses. Stop repeated post-hoc arbitrary recuts of this 2024 file. Keep CEWH enquiry **UNSENT**; no TinyFish used, no JAE RC6/main modifications.
