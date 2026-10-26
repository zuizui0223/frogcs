# Landscape vegetation, urodele suitability and the ecological context of frog calling

Working discussion and manuscript architecture, 2026-10-26. Based on empirical snapshot
`65e5a6f16550c6212dc6318fc8d73f7971e2cbed`; the snapshot is not revised here.
This document develops the current association-first manuscript direction. It does not replace the
archived RC6 manuscript or treat the older integrated draft's prediction criteria as prerequisites.

## 論文の主筋

出発点は、繁殖活動を示す強い鳴き声が繰り返し記録される場所の特徴である。
4,248音響地点で見られたトンボ類適合度との弱い負の関連は、池性有尾類に適した地点で強い。
さらに冠水植生との交互作用にはトンボ類で負、有尾類で正の成分がある。
この組合せを、植生による被食者の退避、捕食者側の生息・生活史支援、捕食者間の制約という
異なる経路から考察する。主題は植生単独の効果でも、有尾類単独の効果でもなく、その文脈依存性である。

本文の順序は、(1) 観測した関連、(2) 有尾類による条件差、(3) 植生との非対称な関連、
(4) 独立実験が示す経路と対立する可能性、(5) 段階別シミュレーションが示す成立条件、
(6) 鳴き声への時間的接続と観測上の代替説明、とする。
水面・過去利用は背景の補助結果として残すが、植生との交互作用モデルがそれらをすべて調整したとは書かない。

## 1. Main empirical finding: conditional association rather than a uniform habitat response

Repeated strong calling was associated with the environmental suitability of other aquatic animal groups,
but the association depended on community and landscape context. Across 4,248 acoustic sites, the weak
negative relationship with odonate suitability became more negative in the high-suitability stratum for
pond-breeding urodeles. Low- versus high-urodele strata yielded correlations of 0.101 versus -0.284 under
uniform background sampling and -0.004 versus -0.183 under target-group background sampling.
These are alternative analyses of the same observations, not independent replications. Their shared
direction identifies a geographically structured pattern worth explaining, without establishing that
local predators suppressed frog reproduction.

Landscape flooded vegetation provided additional context. In the full rank-standardized model, the
odonate-by-vegetation term was negative under both backgrounds (-0.087 and -0.064), whereas the
pond-urodele-by-vegetation term had positive estimates (0.058 and 0.046). The latter interval included zero
under target-group sampling. These are conditional coefficients: the two-way terms describe changes at
zero on the other guild's standardized rank scale. They are neither marginal effects across every site
nor estimates of attack rates. Opposing point estimates should not be presented as a formal test of the
difference between two biological mechanisms. Nevertheless, they motivate considering how the same
vegetated landscape might have different meanings for different aquatic groups.

## 2. Refuge-mediated responses can be asymmetric between predator types

A relevant mechanism is that altered refuge use changes exposure to one predator more than another.
Davenport and Chalcraft (2013) found that dragonfly risk induced tadpoles to use leaf litter, reducing
their vulnerability to foraging adult newts. The reciprocal behavioral pathway did not similarly alter
dragonfly foraging. Litter availability was held constant in those experiments: the study demonstrates
behavior-mediated asymmetry in a structured habitat, not an experimental effect of increasing vegetation
cover. It nevertheless supplies a plausible route by which habitat use could decouple exposure to two
predator types. [Primary study](https://doi.org/10.1002/ece3.691)

Applied as a hypothesis to our pattern, vegetated habitat might allow frogs to use environments also
suitable for urodeles while reducing particular encounters with them. The odonate association need not
respond in the same direction if odonates use different microsites, attack differently, or respond
differently to prey retreat. This explanation requires actual differences in space use; a positive
urodele-by-vegetation coefficient alone does not demonstrate refuge use or a beneficial urodele effect.
Our pond-breeding grouping includes both newts and ambystomatid salamanders, whose adult and larval
foraging roles cannot be treated as interchangeable.

## 3. Refuge provision and support of odonate life stages can coexist

The negative odonate-by-vegetation term does not imply that structure necessarily improves larval
capture efficiency. Hossie and Murray (2010) experimentally showed that leaf-litter structure altered
the functional response of dragonfly larvae, with high cover producing a type III rather than type II
response. The effect involved several components of foraging and depended on prey density; it was not
a general rule that more cover always raises or lowers predation. [Primary study](https://doi.org/10.1007/s00442-010-1568-6)

Vegetation can also support a different part of the odonate life cycle. Experimental artificial plants
showed that structure and mechanical defenses affected emergence-site use and survival during emergence
(Grof-Tisza et al., 2017). This is evidence about transition into the terrestrial stage, not evidence of
increased local aquatic predator density in a later year. [Primary study](https://doi.org/10.1002/ece3.2705)

The ecological distinction is between an effect on encounters per predator and an effect on habitat
use or demographic completion. These could operate simultaneously and in different directions.
Thus a landscape association with odonate suitability can coexist with local refuge benefits.
Explaining a stronger negative calling association through emergence support would additionally require
recruitment, retention or repeated habitat use across time; this is a hypothesis, not a consequence of
the observed coefficient. The seasonal model below deliberately keeps emergence support separate from
aquatic attacks so that this missing feedback is not supplied implicitly.

## 4. Urodeles are also constrained by other predators

Urodeles need not contribute an independent, additive pressure on frogs. In Kishida et al. (2009), caged
dragonfly risk cues altered salamander behavior and morphology and reduced tadpole mortality caused by
salamanders. Dragonflies could not consume the experimental amphibians in that treatment, so the result
isolates an indirect pathway rather than showing a beneficial net effect of freely feeding dragonflies.
[Primary study](https://doi.org/10.1890/08-0238.1)

This distinction matters for the present interpretation. Stronger negative calling associations in
urodele-suitable landscapes are not evidence that indirect benefits are absent; neither does a positive
three-way coefficient establish that those benefits occurred. Direct attacks, predator removal and
behavioral suppression may oppose each other. Vegetation can change exposure of prey to predators and
of one predator to another. Protecting a urodele from a dragonfly could even restore urodele foraging,
producing the opposite of the simple frog-refuge prediction. In a different, salamander-centered pond
experiment, predator identity and habitat structure jointly affected indirect outcomes, providing a
precedent for such context dependence rather than a direct replication of our frog pattern
(Anderson and Semlitsch, 2016). [Primary study](https://doi.org/10.1111/1365-2656.12462)

In our full model, the positive three-way estimate under uniform-background sampling (0.037,
95% interval 0.008 to 0.068) means that the negative odonate-by-urodele component becomes less negative
as vegetation increases on the model scale. It does not imply a positive total odonate effect.
The target-group interval crossed zero, and within-route comparisons did not clearly retain this term.
We therefore treat vegetation-dependent non-additivity as a provisional interpretation rather than a
demonstrated three-species interaction.

## 5. Developmental stages distinguish when constraints act

Stage information provides a way to specify these alternative mechanisms rather than an additional
observed explanation of the NAAMP pattern. Manipulative experiments show that predator-prey arrival
differences can interact with environmental conditions, with responses differing between salamander-frog
and dragonfly-frog systems (Rudolf, 2022). [Primary study](https://doi.org/10.1002/ecy.3704)
Predator-prey direction can also change: observations of Australian frogs consuming emerging dragonflies
complement earlier evidence of those dragonfly larvae consuming tadpoles (Beranek et al., 2023).
This is a different species pair from the Japanese cue experiments and is not a verified edge for every
species in our North American suitability pool. [Primary study](https://doi.org/10.1002/ecy.4108)

We use a separate, explicitly synthetic cohort model to ask when these pathways reinforce or oppose
one another. It tracks survival and stage transitions of all three groups, separates four assumed
vegetation functions, and compares matched two- and three-group communities. Size-gated reciprocal
predation and postmetamorphic frog predation during odonate emergence are individually removable.
The latter edge can constrain odonate completion without benefiting already-completed frog larvae
within the same season. Such a distinction prevents a biologically appealing reversal from being used
as an automatic explanation for earlier calling activity. Full methods and simulated results are in
the [companion stage-network report](STAGE_VEGETATION_SIMULATION_REPORT_2026-10-26.md); none of its parameter values is estimated from the acoustic data.

All simulated departures from independent mortality were antagonistic: predators only suppress or
remove each other, without facilitating attacks or growth. This is structural, not a general ecological
discovery. The model does not reproduce the negative empirical odonate-by-urodele term. It illustrates
how antagonistic pathways coexist with a negative total predator effect and how stage reversal constrains
odonates without changing the current frog cohort's larval survival. Urodele refuge changes mortality
but does not release cue-induced behavioral suppression; the latter remains an untested hypothesis.

## 6. Connecting aquatic mechanisms to adult calling

The response variable is the frequency of survey visits with at least one monitored frog taxon at call
index >=2, not sound amplitude, egg production or larval survival. It also differs from the frozen RC6
rainfall-conditioned concentration statistic. A larval interaction could be associated with adult
calling through breeding-site selection, earlier recruitment shaping the adult population, or recurring
environmental conditions affecting both stages. The present analysis does not choose among these routes.

Breeding-site choice is plausible but species-specific. Resetarits and Wilbur (1989) found reduced
oviposition by Hyla chrysoscelis in ponds containing Ambystoma larvae, but not in ponds with the tested
adult Notophthalmus or larval Tramea. Female oviposition decisions cannot be substituted for male chorus
placement, and that experiment cautions against treating all predators as interchangeable avoidance
cues. [Primary study](https://doi.org/10.2307/1938428)

Persistent habitat quality and variation in the calling frog assemblage remain ecological alternatives.
Because the outcome pools monitored frog taxa, species turnover or differences in calling phenology can
generate a site-level association without changing the response of any particular frog species.
Vegetation-dependent acoustic propagation or survey detection is another observation-process hypothesis,
not a measured correction in this model. Similarly, the suitability predictors are derived from
environmental variables, including land-cover information; their interactions with landscape vegetation
can reflect nonlinear shared environmental structure rather than a functioning food web. We have not
isolated an effect independent of all environmental variation or estimated a mediation pathway.

## 7. Contribution and boundaries

The contribution is the identification of conditional spatial associations: a weak overall odonate
association becomes stronger in urodele-suitable environments, and vegetation-associated modification
differs between the two groups. This supplies a focused ecological question about habitat use and
direct versus indirect constraints. Our mechanistic discussion and scenario model explain why several
outcomes are possible; they do not identify which mechanism generated the observed association.

The 3-km landscape covariate, derived from coarse historical land cover, is not a measurement of stems,
submerged refuges or current pond vegetation. Only 506 of the 4,248 sites had positive flooded-vegetation
context at this radius; the apparent contrast should not be interpreted as a smoothly sampled gradient
of pond complexity. Mean cover and spatial SD were almost identical information (rho=0.99984).
Within-route and 1-km sensitivities delimit the spatial support of the result. Model uncertainty remains
conditional on fitted suitability scores, without multiple-comparison correction or propagation of
species-model uncertainty. These limits specify the claims while retaining the value of the broad-scale
pattern. More detailed stage and habitat observations, potentially including validated methylation-eDNA
state markers, would address the next mechanistic question; those markers alone would not document feeding.

## Result-to-claim audit

| Result or evidence | Permitted discussion | Unsupported shortcut |
|---|---|---|
| Negative odonate association is stronger in high-urodele stratum | Conditional spatial pattern; combined constraints are a candidate | Both predators were present and jointly killed more tadpoles |
| Odonata x vegetation negative; urodele x vegetation positive estimate | Potentially asymmetric habitat relationships | Vegetation experimentally favors one group or protects frogs from urodeles |
| Three-way positive estimate, sensitive to background/scale | Candidate change in non-additivity | Positive net effect of dragonflies; universal buffering |
| Constant-litter behavioral experiment | Refuge use can affect predator types asymmetrically | Manipulated plant-cover effect |
| Caged dragonfly-cue experiment | Nonconsumptive suppression of salamander foraging | Positive net effect of a freely feeding dragonfly |
| Emergence experiments | Plant traits can affect transition survival | More local predatory nymphs next year |
| New stage simulation | Consequences and counterexamples under explicit assumptions | Fit, independent validation, measured stage reversal or coexistence |

## Mathematical reading to retain during editing

For standardized ranks O, S, V and response Y, the model contains every lower-order term:

`Y = b0 + bO O + bS S + bV V + bOS OS + bOV OV + bSV SV + bOSV OSV`.

`dY/dO = bO + bOS S + bOV V + bOSV SV`.
`d²Y/dO dV = bOV + bOSV S`; `d²Y/dO dS = bOS + bOSV V`.
These are derivatives of the fitted rank-scale surface, not biological response rates. A coefficient
or its separate interval cannot supply the uncertainty of a compound slope; that requires joint draws.
Do not interpret unobserved combinations of ranks as supported local ecological contrasts.

## Source navigation

Empirical tables: `../results/naamp_remote_vegetation_20261026/network_rank_coefficients.csv`,
`../results/naamp_odonata_caudata_associations_20261026/stratified_correlations.csv`.
Independent literature audit: [primary evidence](VEGETATION_THREE_GUILD_PRIMARY_EVIDENCE_2026-10-26.md).
Model design: [stage/vegetation assumptions](STAGE_VEGETATION_MODEL_DESIGN_2026-10-26.md).
