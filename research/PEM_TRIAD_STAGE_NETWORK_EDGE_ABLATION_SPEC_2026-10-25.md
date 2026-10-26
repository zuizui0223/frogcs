# PEM seasonal three-guild network: mechanism ablation before output

2026-10-25, simulation-only diagnosis; no field-estimated NWI PEM, frog larval recruitment, GloBI kill rates, or true biotic competition. This explicitly follows the prior synthetic result where nonzero relative predator-stage offsets improved three-resident-rare-invader screen in 96/96 settings; this earlier result may reflect *chosen model structure* and MUST be challenged.

Keep exact 2026-10-25 parameter-generating distribution, 3 illustrative PEM water windows × 3 salamander offsets × 3 odonate offsets × 2 shelter levels × 2 D-risk cue strengths, **32 common parameter draws**, one fixed frog cohort width (0.05 year-cycle); annual stage kernel means unchanged. Simulate 220 years and calculate three missing-species invasion log rates into their own resident species pairs, conditional on resident stability.

Mechanistic ablations (exact same parameter draws, hydrology, seasonal phases, stem/refuge and initial populations):
- `full`: all existing annual-map trophic terms.
- `no_risk_cue`: disable ONLY the D-risk-mediated reduction of S→F consumption, **keeping the direct D→S mortality edge** and all direct frog attacks.
- `no_reverse_frog_dragonfly`: set frog postmetamorph→emerging dragonfly attack and its feeding benefit to zero; other edges unchanged.
- `no_direct_dragonfly_frog`: set direct D-nymph→frog tadpole attack and its feeding benefit to zero; risk cue to salamander remains.

For each matched habitat×phase×parameter regime, calculate `unconditional_mutual_invasion_draw_fraction` and `frog_rare_invasion_mean_log_growth`. For each ablation compare `full−ablated`, counts positive/negative/ties and ranges, and **phase-offset advantage vs synchronized** under each mechanism.

Output: one machine-readable synthetic JSON + compact comparative CSV, source code, CI. No p-values: arbitrary parameter-draw frequencies are not prevalence in natural PEM wetlands. If absence of the risk cue leaves the phase-shift direction unchanged, then claiming tritrophic behavioural mediation as necessary for the observed toy result is invalid; similarly reverse feeding may be dispensable. Do not confuse no_D→F ablation with documented food-web relationships in the same Japanese species assemblage: the full toy joins motifs reported in different regions and taxa.

The decision objective is **falsification and identifying *which edge matters***, not making all triad roles necessary by construction.
