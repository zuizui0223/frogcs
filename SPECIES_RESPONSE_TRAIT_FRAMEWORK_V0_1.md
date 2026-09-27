# Species response-trait framework v0.1 — falsified activation-geometry candidate

## Status

**Superseded as a main-text response-trait interpretation by the frozen activation-geometry placebo gate.**

Activation geometry showed strong temporal and route-set repeatability, but those same species rankings were reproduced by reverse-direction gains, low-rain-contrast gains and baseline acoustic solitude tendency. RC6 therefore does **not** treat activation geometry as a rainfall-specific response trait.

This file is retained as an audit record of the concept that was tested and falsified.

## Candidate definition

The proposed coordinate asked:

> Conditional on a species gaining a species × stop incidence in the wetter run, does that gain enter a stop that was inactive in the paired drier run or a stop that was already active?

Operational quantity:
- success = wet-gain incidence at a stop inactive in the paired drier run;
- failure = wet-gain incidence at a stop already active in the paired drier run;
- opportunity correction = offset `logit(q_pair)`, where `q_pair` is the fraction of drier-run stops available in the inactive state.

The fitted species intercept was called activation geometry.

## Why the candidate initially looked compelling

### Temporal repeatability

Across 2001–2007 versus 2008–2015:
- overlap species = 16;
- Spearman rho = **0.774**;
- P = **0.000439**;
- WLS late-on-early slope = **0.910**, 95% CI 0.816–1.003;
- 15/16 species retained sign.

### Disjoint-route transfer

Across deterministic, completely non-overlapping route sets:
- overlap species = 26;
- Spearman rho = **0.785**;
- P = **2.09e-6**;
- WLS B-on-A slope = **0.832**, 95% CI 0.542–1.122;
- 21/26 species retained sign.

These validations established that the quantity was stable. They did not establish that the stability was rainfall-specific.

## Frozen placebo gate

Before placebo endpoint readback, RC6 specified that geometry would remain in the title only if the wet-gain species ranking was not strongly reproduced by three rain-independent or direction-reversed comparators.

The pre-existing strong-coupling rule was reused:
- Spearman rho >= 0.60;
- two-sided P < .05.

All three primary placebo comparisons exceeded that threshold:

| Comparator | rho with wet geometry | P |
|---|---:|---:|
| reverse dry-gain geometry | **0.929** | 1.94e-7 |
| bottom-quartile low-rain-contrast geometry | **0.953** | 1.21e-8 |
| opportunity-corrected baseline solitude geometry | **0.782** | 0.000341 |

Raw singleton-calling fraction was also strongly correlated:
- rho = **0.876**;
- P = 8.44e-6.

## Revised interpretation

The stable species ordering is better interpreted as a persistent **acoustic co-occurrence / gain-placement tendency** than as a rainfall-specific response geometry.

For example, species that commonly occur in singleton calling contexts tend to place both wetter-direction and drier-direction gain incidences at stops that are otherwise inactive. Conversely, species associated with multispecies calling contexts tend to place gains within already-active stops.

This explains why the ranking can transfer across time and route identities without requiring a rainfall-specific response mechanism.

## Relation to community matrix expansion

The community-level four-way incidence decomposition remains valid because it is an exact accounting identity applied to observed wet-minus-dry changes.

The placebo failure changes the **species-trait interpretation**, not the community-level decomposition.

RC6 may still say:
- rainfall-associated incidence growth crosses spatial and taxonomic matrix boundaries;
- more stops become active;
- local alpha and route gamma increase;
- matrix fill remains practically equivalent within the frozen margin.

RC6 must not say:
- species have a rainfall-specific activation geometry;
- repeatable geometry explains the rainfall effect;
- “spatial-edge activator” or “local taxonomic deepener” are validated rainfall-response trait categories;
- temporal or route-set repeatability rescues geometry after the placebo gate.

## Response magnitude comparison

A frozen cross-period diagnostic previously showed moderate rank coupling between early geometry and later wet-versus-dry response magnitude:
- rho = 0.415;
- P = .110;
- weighted slope = +0.354.

After the placebo failure this result is retained only as audit history. It does not rescue the rainfall-specific interpretation.

## Endpoint policy

The placebo gate is the final decision rule for activation geometry in RC6.

It failed.

No residualization, redefinition, alternative baseline correction, new threshold, or replacement species trait is authorized within the current manuscript.

Future work can revisit species-specific mechanism only with a new hypothesis family, preferably using independent data or independently sourced proximal traits.
