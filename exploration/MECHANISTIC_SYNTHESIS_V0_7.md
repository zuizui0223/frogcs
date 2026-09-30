# Mechanistic synthesis v0.7: hydric state releases a recurrent local chorus network

**Status:** exploratory synthesis only. The JAE submission authority remains `015a675324800f2e5ac9ab0985b080fe88adc375`. None of the analyses below changes the frozen RC11 submission.

## One-sentence result

Rain-associated frog-community expansion is best described as **recurrent chorus activation on a persistent species × site template, with dynamic soil-water change providing an additional and broadly transportable hydric-state axis that predicts both strong chorus recruitment and how deeply activated species spread across stops**.

The evidence does **not** support a simple causal chain in which rainfall works only by making the wet-side soil wetter. Rain recency and soil-water change retain partly distinct information.

## 1. The response is entry into chorus activity, not mainly louder calling

Across 4,236 NAAMP matched comparisons, the rainfall coefficient for total CallingIndex change was **2.841**. The dry-zero → wet-positive activation component was **1.855 (65.3%)**, whereas intensity change among cells already positive in both surveys was only **0.196 (6.9%)**.

Most of the activation signal is not weak CI1 detection. Dry-zero → wet-CI2/3 had a rainfall coefficient of **1.615 (95% CI 0.493–2.737)** and carried **87.1%** of the activation coefficient. New CI3 full choruses also increased with rainfall contrast (**beta = 0.441, 95% CI 0.114–0.768**), including in same-observer pairs retaining the same ten physical SiteIDs (**beta = 0.514, 0.101–0.927**).

Thus rainfall-associated expansion includes emergence of overlapping and full choruses.

## 2. “New” acoustic cells are mostly recurrent local states

Using only observations from years **before** the focal comparison, the strong CI2/3 rainfall coefficient was **1.750**. The recurrent component was **1.794**, while the component with no prior route-season record was approximately zero (**−0.044**).

For strong recruitment:

- prior-route recurrence accounts for about **102.5%** of the rainfall coefficient;
- prior occurrence at the same physical SiteID accounts for about **84.4%**;
- prior CI2/3 at the same SiteID accounts for about **70.0%**.

This does not prove continuous occupancy, but it strongly favors **reactivation of previously observed local acoustic states** over one-off appearance of entirely unseen local states.

## 3. The local template is species-specific, not merely a generally productive site

Within the **same focal pair and same species**, prior CI2/3 at a physical SiteID predicts wet-side CI2/3 at that SiteID (**beta ≈ 0.151, 95% CI 0.129–0.173**). The same-observer estimate is **≈0.159 (0.134–0.183)**.

The signal survives controls for:

- prior SiteID sampling opportunity;
- generic prior strong-chorus richness of other species;
- general prior any-caller richness.

Across estimable species, **19/20** own-site template slopes are positive (sign-test **P ≈ 2×10⁻⁵**).

Memory is spatially local. Exact same-SiteID history is more informative than adjacent-site history, and memory strength declines with metric distance.

The formal ≥4-year memory gate was underpowered in route count, so a durable multi-year headline is not authorized, although older-memory coefficients remain descriptively positive.

## 4. The matrix anomaly is activation depth, not special placement geometry

Rainfall-associated route-new species do not become exceptional mainly because more taxa enter or because more taxa reach a second stop.

The excess appears at **third and later occupied stops**:

| Component | Rainfall coefficient |
| --- | ---: |
| Route-new species | 0.185 |
| Second-stop incidence | 0.132 |
| Third-plus-stop incidence | **0.473** |
| Fourth-plus-stop incidence | **0.363** |

The third-plus component lies above both primary null families. About **97.3%** of its coefficient is carried by species reaching CI2/3, and about **95.4%** in the same-observer + same-physical-stop subset.

Once species identity and realized wet-side stop count **k** are fixed, special stop placement is not required (history-weighted placement **P ≈ 0.179**; persistence-weighted placement **P ≈ 0.212**). MPD, MST and route-adjacency diagnostics likewise do not establish unusual clustering conditional on k.

The mechanistic degree of freedom is therefore **how spatially deep an activated species becomes**, not an unusual geometric arrangement after depth is fixed.

## 5. The strongest tested environmental axis is soil-water change

Recent-rain amount initially predicted strong chorus recruitment, but instantaneous humidity/VPD, barometric pressure and current light rain did not explain it.

When ERA5 soil water is added, the picture changes sharply.

For shallow soil-water change (swvl1):

- strong CI2/3 recruitment: **beta ≈ 1.573, 95% CI 0.923–2.223**;
- same-observer + same-physical-stop: **≈1.624, 0.824–2.423**;
- new CI3 full chorus: **≈0.342, 0.154–0.529**.

The 72-hour precipitation coefficient is no longer independently supported once soil-water change is included. Layer-2 soil water gives the same direction.

### Relative change is more consistent than a fixed threshold

When wet-side and dry-side soil state are entered separately:

- wet-side swvl1: **+2.286 (1.229–3.344)**;
- dry-side swvl1: **−2.612 (−3.674 to −1.550)**.

Their sum does not differ detectably from zero (**P = 0.216**), consistent with a largely symmetric wet-minus-dry change contrast. The same-observer version gives the same result (**P = 0.431**), as does CI3 (**P = 0.771**).

A fixed upper-quartile soil-moisture threshold is not supported. Thus the evidence fits **relative hydric-state change** better than a universal absolute wetness threshold.

## 6. The soil-water signal is highly robust within NAAMP

The same soil-water model was tested without retuning.

### Disjoint route split

- Fold A: **beta = 1.075, 95% CI 0.470–1.680**
- Fold B: **beta = 2.132, 1.055–3.209**

### Temporal split

- 2001–2008: **beta ≈ 1.550, 0.912–2.188**
- 2009–2015: **beta ≈ 1.637, 0.720–2.553**

### Same-observer + same-physical-stop route split

- Fold A: **beta ≈ 0.987, 0.209–1.765**
- Fold B: **beta ≈ 2.298, 1.002–3.594**

### Leave one state out

All **21/21** omitted-state refits retain a positive, CI-supported soil-water coefficient.

State-specific estimates remain heterogeneous: 13/15 estimable states are positive and 7/15 individually CI-supported. The pooled NAAMP-domain result is therefore highly robust without implying identical state-level effects.

## 7. The soil signal is not just the 0–3-day survey protocol

When the drier member is required to be at least four days after rain, removing comparisons wholly inside the 0–3-day target window:

- **1,722 pairs / 411 routes**
- soil-water beta **1.950 (1.118–2.783)**
- 72-hour rain amount is not independently supported.

In the same-observer + same-physical-stop subset:

- **1,293 pairs / 338 routes**
- soil-water beta **1.884 (0.799–2.970)**.

The much smaller subset in which **both** surveys are ≥4 days after rain remains positive (**1.377**) but imprecise because only 174 pairs remain. Therefore simple 0–3-day protocol targeting is insufficient to explain the soil-water association, but all scheduling confounding is not eliminated.

## 8. Soil wetting is not a necessary on/off gate for the rain-recency effect

A deliberately sharp falsification divided pairs according to whether the survey defined as wetter by DaysSinceRain was **actually wetter in swvl1**.

- soil-wetting concordant: 2,805 pairs;
- soil-wetting discordant: 1,303 pairs.

The rain × positive-soil-wetting interaction is essentially absent:

- **beta = 0.192**
- 95% CI **−1.446–1.830**
- **P = 0.818**.

The same-observer + physical-stop interaction is **−0.005, P = 0.996**.

Rainfall contrast remains positive even in soil-discordant pairs (**beta = 1.128, 95% CI 0.071–2.185**).

Therefore soil-water change is **not** a demonstrated necessary mediator or binary gate for rain recency. The data support partially distinct rainfall-recency and hydric-state information.

## 9. Soil-water change and historical template jointly predict spatial depth

Among 1,927 activated pair-species observations from 325 routes and 44 species, third-plus-stop depth is predicted independently by:

- historical strong-chorus breadth: **beta = 0.627, 95% CI 0.481–0.773**;
- soil-water change: **beta = 0.137, 0.036–0.237**.

The full-sample template × soil interaction is not supported (**0.073, −0.020–0.166**). Rain contrast and 72-hour rain amount are no longer supported after these two axes enter.

In the same-observer subset, both main effects remain positive and an interaction appears, but because the full-sample interaction is absent, the safest general interpretation is **two largely additive axes** rather than a universal multiplicative gate.

## 10. Falsification hierarchy

The following explanations are not sufficient:

- common uniform activation;
- persistence-favouring common activation;
- transferable species-specific rain shifts alone;
- local acoustic memory alone;
- a single cross-fit rain × local-memory parameter;
- observer turnover or physical stop relocation;
- measured hearing/noise/wind/traffic conditions;
- CI1-only weak-call detectability;
- simple attraction to existing chorus stops;
- an exclusively same-night / 0–1-day pulse;
- broad NWI hydroperiod;
- Palustrine versus Riverine/Lacustrine class;
- instantaneous VPD/RH;
- barometric pressure;
- current light rain;
- 72-hour precipitation amount once soil water is included;
- a fixed soil-moisture threshold;
- a binary requirement that the wet-side survey have greater soil water;
- generic good-frog-site quality;
- special stop placement once species identity and activation depth are fixed.

## Mechanistic ceiling

The strongest defensible exploratory interpretation is:

> **Rain-associated chorus recruitment is the re-expression of a latent, species-specific local acoustic network. Historical species × site use provides the spatial template, while dynamic environmental wetness—best captured among tested variables by wet-minus-dry soil-water change—provides an additional hydric-state axis that predicts both entry into substantial chorus activity and the spatial depth of that activation. Rain recency and soil-water change are related but not reducible to a single binary hydric gate.**

This remains an observational acoustic inference.

The data still cannot separate:

1. persistent local populations from persistent species-specific microhabitat suitability;
2. frog hydration from breeding-site water availability/inundation;
3. endocrine/reproductive readiness from other correlated consequences of wet conditions.

No claim is authorized about demographic colonization, abundance, continuous occupancy, individual philopatry or reproductive success.

## Generality

**Within NAAMP:** strong for the pooled mechanism. Soil-water and local-template effects transport across routes, time periods and leave-one-state-out analyses, while state-specific strength remains heterogeneous.

**Across taxa:** strong within NAAMP. Site-template effects are positive in 19/20 estimable species and strong-activation contributions are diffuse rather than concentrated in one or two taxa.

**Across continents:** not established. No external public dataset yet supplies a comparable, effort-complete multi-site species × site matrix, and the prefixed AnuraSet site tests did not reproduce the NAAMP threshold-dominance rule.

## Stop rule

At this point further post-readback NAAMP regression fishing would add more risk than information. The next genuinely discriminating evidence would be:

1. direct survey-night water-level / inundation / soil-hydrology measurements;
2. individual-level mark-recapture or telemetry testing persistent local populations;
3. an independent effort-complete multi-site acoustic time series.

