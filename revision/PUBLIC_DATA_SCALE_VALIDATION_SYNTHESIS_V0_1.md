# Public-data scale validation synthesis v0.1

## Purpose

The large public NAAMP archive was used not only for discovery but for two additional post-hoc validation questions that exploit its spatial and temporal extent:

1. whether the focal conditional spatial-allocation result transfers across held-out States and into a later time period; and
2. whether rainfall amount occurring only after a survey behaves like antecedent rainfall amount, as a temporal negative control.

These analyses do not change the frozen focal endpoint and are not independent external replication.

## 1. Blocked spatial transferability

Contract: `exploration/NAAMP_BLOCKED_TRANSFERABILITY_CONTRACT_V0_1.json`  
Receipt: `exploration/NAAMP_BLOCKED_TRANSFERABILITY_RECEIPT_V0_1.json`

Each focal pair used a species rainfall-response slope trained with the entire focal State excluded. Strictly-prior local physical-site history remained available because it precedes the focal pair. Observed total wet activation remained conditioned on, matching the original estimand.

Coverage:
- 2,916 pairs;
- 439 routes;
- 20 States.

Result:
- observed concentration coefficient = **1.6503**;
- blocked prediction = **1.3557**;
- conditional residual = **0.2947**;
- simulated 95% residual interval = **−0.1203 to 0.1298**;
- plus-one upper-tail **P = 0.000999**;
- classification = **excess_transfers**.

The result is almost unchanged from the current principal comparator despite removing the focal State from species-response training.

### Interpretation

The within-taxon concentration excess is not dependent on calibrating species rainfall-response slopes inside the same State being evaluated.

This is a **conditional spatial transferability** result, not full geographic forecasting: the analysis still conditions on the existing taxonomic support, strictly-prior local site history and observed response magnitude.

## 2. Blocked temporal transferability

Species rainfall responses were trained only on **2001–2008**. Physical-site history was also frozen at **2008**. The test used only pairs with both surveys in **2009–2015**.

Coverage:
- 1,095 held-out pairs;
- 211 routes;
- 18 States;
- 41 species had estimable pre-2009 rainfall responses.

Result:
- observed concentration coefficient = **3.0058**;
- pre-2009 prediction = **2.4288**;
- conditional residual = **0.5771**;
- simulated 95% residual interval = **−0.2253 to 0.2377**;
- plus-one upper-tail **P = 0.000999**;
- classification = **excess_transfers**.

### Interpretation

The focal conditional spatial-allocation excess is present in a later seven-year period even when species rainfall-response parameters and the local site-history template are frozen before that period.

As above, this is conditional transferability rather than a full forecast: response magnitude and the broader stratum species support remain conditioned on by the focal estimand.

## 3. Future-rain temporal negative control

Contract: `exploration/NAAMP_FUTURE_RAIN_NEGATIVE_CONTROL_CONTRACT_V0_1.json`  
Receipt: `exploration/NAAMP_FUTURE_RAIN_NEGATIVE_CONTROL_RECEIPT_V0_1.json`

The same 2,835-pair weather/prior-history sample was modelled with either:
- antecedent 72-h ERA5 rainfall amount; or
- a non-overlapping 72-h ERA5 rainfall window beginning one hour after the survey midpoint.

Coverage:
- 2,835 pairs;
- 428 routes;
- 20 States;
- 7,559 route-runs with both weather windows.

Observed concentration coefficient on the common sample = **1.7136**.

With the same Monte Carlo seed for the two amount models:
- antecedent prediction = **1.4345**, residual = **0.2791**;
- future-rain prediction = **1.4291**, residual = **0.2845**;
- future-rain residual 95% null interval = **−0.1316 to 0.1343**;
- future-rain plus-one upper-tail **P = 0.000999**;
- classification = **future_placebo_rejected**.

The run-level log1p antecedent–future rainfall correlation was only **0.0519**, yet the two flexible amount models produced very similar predictions.

### Interpretation

Future rainfall amount does **not** reproduce the focal concentration excess: a large positive residual remains.

However, antecedent rainfall amount is only marginally more explanatory than future rainfall amount in this flexible model. Therefore the manuscript should **not** use the 72-h amount analysis as evidence that the concentration structure is temporally specific to antecedent rainfall amount.

The safe inference is narrower:
- measured antecedent rainfall amount is insufficient to explain the spatial-allocation excess;
- future rainfall amount is also insufficient;
- the similar amount-model predictions suggest that whatever small improvement rainfall amount provides may partly reflect broad weather-regime/model-flexibility information rather than a uniquely antecedent 72-h mechanism.

The earlier 6.5% residual-removal value and the 16.2% value in the negative-control run should not be compared as fixed biological quantities because they arise from different 1,000-draw Monte Carlo seeds. The direct same-seed antecedent-versus-future predictions/residuals above are the relevant descriptive comparison.

## 4. Manuscript consequence

### Promote to main text

The blocked generalization result is worth a compact main-text statement because it uses the scale of the public archive in a way that the existing leave-one-State robustness does not.

Recommended claim:

> **The conditional within-taxon concentration excess persisted when species rainfall responses were learned without the focal State and when both species response and site-history templates were frozen through 2008 and evaluated only in 2009–2015.**

This should be described as a **post-hoc blocked transferability assessment**, not independent validation.

### Retain in Supporting Information / limitations

The future-rain negative control should remain supporting/limitation evidence. It strengthens the statement that measured rainfall amount does not account for the focal residual, but weakens any attempt to interpret the incremental 72-h rainfall-amount improvement as specifically antecedent.

### Do not change

Do not change:
- the title;
- the focal endpoint;
- the principal 2,916-pair comparator;
- the conclusion that response magnitude and first-order taxon/site propensities do not fully describe realised spatial allocation;
- the boundary against causal rainfall, literal synchrony, movement, occupancy, individual memory or a unique mechanism.

## 5. Overall consequence of using the public large-scale dataset

The strongest added value of the public archive is now not merely sample size. It is that the same conditional ecological pattern can be challenged under:
- whole-State exclusion;
- a seven-year temporal holdout;
- a temporally reversed rainfall-amount placebo.

The first two support generality of the spatial-allocation pattern. The third prevents overclaiming temporal specificity of one weather covariate.
