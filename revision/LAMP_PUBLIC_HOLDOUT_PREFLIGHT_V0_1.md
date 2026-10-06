# LAMP public holdout preflight v0.1 — 2026-10-06

## Status

This document opens a **separate external/public-data validation branch**. It does not reopen the closed RC6 NAAMP analysis and does not alter the current submission unless a later, explicitly governed decision is made.

No LAMP species × stop outcome matrix has been inspected for the frogcs endpoint before this preflight was frozen.

## Candidate

Louisiana Amphibian Monitoring Program (LAMP), 1997–2017.

Public source:
- Carter, J. (2021), *Louisiana Amphibian Monitoring Program Survey Frog Call Observation Data: 1997–2017*, U.S. Geological Survey data release, DOI 10.5066/P9VNBWM2.
- LAMP is Louisiana's state chapter of NAAMP and follows the NAAMP calling-survey protocol.

Public design documentation establishes:
- 10 fixed stops per route;
- 5-minute listening surveys;
- ordinal Calling Index 0–3 / blank-to-3 representation with CI3 = full continuous overlapping chorus;
- repeated Run 1/2/3 surveys across years;
- survey date, temperature, wind/sky information and time since last significant precipitation.

## Independence boundary

LAMP is **not an independent monitoring programme** from NAAMP. The national NAAMP raw release includes Louisiana and LAMP used NAAMP protocol and coordination.

However, the frozen frogcs discovery endpoint used 21 states and contains no Louisiana state observations. Therefore LAMP may be evaluated only as a **held-out geographic outcome dataset outside the analysed 21-state discovery sample**, never as independent-programme replication.

Before any outcome calculation:
1. derive the canonical set of discovery RouteNumber/State identifiers from the existing frogcs pair dataset;
2. verify that no Louisiana route contributed to the 4,236 discovery comparisons or the 2,916 strictly-prior-history focal comparisons;
3. if any physical route overlap is detected, exclude those routes before outcome readback and record the exclusion.

Failure of this separation gate makes LAMP ineligible for a held-out validation claim.

## Schema/estimand gate — frozen before response readback

LAMP is eligible for the frozen primary endpoint only if the public release contains, without outcome-dependent reconstruction:

1. route identifier;
2. stable stop identifier or stable StopNumber within route;
3. RunNumber/seasonal window;
4. survey date/year;
5. taxon-level call index at each stop;
6. a numeric or exactly documented field that can reproduce rainfall recency comparably across surveys;
7. sufficient repeated prior history for taxon × physical-stop propensity;
8. enough complete 10-stop route-runs to form matched wetter–drier comparisons and deterministic route folds.

If rainfall recency is only an incomparable category/text field, do not invent a post-readback mapping. Classify the frozen primary test as **estimand-incompatible**.

## Frozen population construction

If the schema gate passes:

- use 2001 onward for direct comparability with the unified-protocol discovery period;
- retain complete 10-stop route-runs under the same validity logic as far as LAMP metadata permit;
- stratify by Route × RunNumber;
- order eligible runs by year and pair adjacent observed years;
- exclude equal-rainfall-recency pairs;
- label the survey closer to rain as wetter and the other as drier;
- require strictly prior history for the focal comparator.

No subset may be selected based on the direction or magnitude of the concentration result.

## Frozen primary endpoint

Use the existing frogcs endpoint without redefinition.

For each taxon absent from all ten stops in the drier/reference run and present at one or more stops in the wetter/target run:

- k_i = number of wetter-run calling stops;
- e_i = max(k_i - 1, 0);
- C = sum_i choose(e_i, 2).

The observed conditional within-taxon concentration is compared against a route-cross-fitted comparator.

## Frozen comparator

Where LAMP fields permit, represent only:

- taxon-specific rainfall response trained on the opposite deterministic route fold;
- strictly prior taxon × physical-stop propensity;
- focal dry-state persistence;
- one common magnitude-matching shift so expected wetter-run incidence matches the realised activation magnitude.

Do not add taxon × stop rainfall interactions, traits, landscape terms, new thresholds or new environmental windows after outcome readback.

Use 1,000 simulations and the same plus-one upper-tail P convention as frogcs.

## Primary interpretation

PASS: observed conditional concentration exceeds the upper 95% comparator distribution in the preregistered direction.

FAIL is reported whether or not it is favourable to the current manuscript. It is not converted into a new endpoint.

Because LAMP shares the NAAMP programme family, a PASS would support **held-out geographic transfer within the NAAMP protocol family**, not transferability to an independent monitoring programme.

## Frozen secondary checks

Only after the primary result is produced:

1. silence -> CI2/3 and silence -> CI3 transitions;
2. marginal third-and-later / fourth-and-later participation using the same definitions as frogcs;
3. strictly-prior strong-site targeting using prior CI2/3 or CI3, matching the existing definition as closely as the schema permits;
4. the already-frozen prospective prediction that broad activation need not erase spatial selectivity.

Secondary checks cannot rescue a failed primary endpoint and cannot replace the headline endpoint.

## One-shot disclosure rule

If LAMP passes the structural gate and the primary outcome is opened, its result must be retained and reported in this branch regardless of direction. Do not screen additional public networks and report only a successful one.

## Manuscript boundary

No LAMP result enters RC6 automatically. RC6 remains scientifically closed. Any incorporation requires a separate explicit manuscript-reopening decision after the preregistered LAMP analysis has been completed and fully disclosed.
