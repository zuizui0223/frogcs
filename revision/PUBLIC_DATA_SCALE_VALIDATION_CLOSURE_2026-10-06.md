# Public-data scale validation reopening and closure — 2026-10-06

## Authority

After RC6 scientific closure, the project was explicitly reopened for a **finite, user-directed validation extension** motivated by the scale of the public NAAMP archive.

Only two new outcome analyses were authorized:

1. blocked spatial/temporal transferability of the frozen within-taxon concentration endpoint;
2. a future-rain temporal negative control for the existing 72-h rainfall-amount analysis.

No new endpoint, threshold, trait screen, landscape metric, lower-level mechanism family or external dataset was authorized.

## Frozen-before-result records

Blocked transferability:
- `exploration/NAAMP_BLOCKED_TRANSFERABILITY_CONTRACT_V0_1.json`
- `exploration/run_naamp_blocked_transferability.py`
- `exploration/NAAMP_BLOCKED_TRANSFERABILITY_RECEIPT_V0_1.json`

Future-rain negative control:
- `exploration/NAAMP_FUTURE_RAIN_NEGATIVE_CONTROL_CONTRACT_V0_1.json`
- `exploration/run_naamp_future_rain_negative_control.py`
- `exploration/NAAMP_FUTURE_RAIN_NEGATIVE_CONTROL_RECEIPT_V0_1.json`

Synthesis:
- `revision/PUBLIC_DATA_SCALE_VALIDATION_SYNTHESIS_V0_1.md`

## Results

### Blocked State transferability

Using species rainfall-response slopes trained with each focal State entirely excluded:

- 2,916 pairs, 439 routes, 20 States;
- observed concentration = **1.6503**;
- predicted = **1.3557**;
- conditional residual = **0.2947**;
- null 95% = **−0.1203 to 0.1298**;
- plus-one P = **0.000999**.

Classification: **excess_transfers**.

### Blocked temporal transferability

Species rainfall response and local physical-site history were frozen through 2008 and evaluated in 2009–2015:

- 1,095 held-out pairs, 211 routes, 18 States;
- observed concentration = **3.0058**;
- predicted = **2.4288**;
- residual = **0.5771**;
- null 95% = **−0.2253 to 0.2377**;
- plus-one P = **0.000999**.

Classification: **excess_transfers**.

These are conditional within-programme transferability results. They are not full forecasts or independent confirmation because the focal estimand still conditions on realised activation magnitude and broader taxonomic support.

### Future-rain negative control

On 2,835 pairs:

- antecedent 72-h prediction = **1.4345**, residual **0.2791**;
- future +1 to +72 h prediction = **1.4291**, residual **0.2845**;
- future residual null 95% = **−0.1316 to 0.1343**;
- future upper-tail P = **0.000999**.

Classification: **future_placebo_rejected**.

Future rainfall does not explain the focal concentration excess. However, its same-seed prediction is very similar to the antecedent-rainfall prediction. Therefore the incremental 72-h rainfall-amount fit is **not interpreted as evidence of antecedent temporal specificity**.

## Manuscript consequence

Authorized manuscript changes are limited to:

- compact blocked-transferability methods/results/generalization language;
- future-rain negative-control language in the weather result and limitations;
- Supporting Information details;
- synchronized evidence/provenance records.

The title, focal endpoint, principal comparator and central biological conclusion remain unchanged.

## Closure

This finite reopening is now **closed**.

No further same-data NAAMP endpoint, weather window, future/antecedent lag, regional split, temporal cutoff, trait, mechanism, landscape or threshold analysis is authorized for RC6 without a new explicit reopening record.

WFTS remains not pursued. The landscape line remains closed. External confirmation remains untested.
