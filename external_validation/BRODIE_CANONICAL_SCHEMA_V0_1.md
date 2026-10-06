# Brodie external validation canonical schema v0.1

**Frozen before Brodie raw frog-response rows are inspected or analysed.**

The raw Research Data JCU file structure is not assumed here. A later raw-to-canonical adapter may
only rename/recode documented fields and must be frozen before calculating the external endpoint.

## File 1 — chorus.csv

One row per positive or explicit-zero species × date × site observation.

Required columns:

| column | type | rule |
|---|---|---|
| date | YYYY-MM-DD | recording-night date |
| site | string | physical breeding-site identifier |
| species | string | stable taxon label |
| chorus_minutes | numeric >=0 | nightly minutes of chorus activity |

Duplicate date × site × species rows are forbidden.

The analysis will construct zero chorus values only for a date × site marked recorded in
`recording_status.csv` and for species known in the canonical chorus table. Missing recording status
is never converted to zero.

## File 2 — recording_status.csv

One row per date × site.

Required columns:

| column | type | rule |
|---|---|---|
| date | YYYY-MM-DD | recording-night date |
| site | string | same physical site coding as chorus.csv |
| recorded | 0/1 | 1 only when the night is known to have usable recording coverage |

Duplicate date × site rows are forbidden.

The primary analysis requires exactly three physical sites because the frozen Brodie contract defines
deep activation as k=3.

## Optional weather.csv

Used only for the prespecified secondary rain analysis.

Required if supplied:

| column | type | rule |
|---|---|---|
| date | YYYY-MM-DD | same night/date convention |
| rainfall | numeric | the published same-night rainfall quantity selected by raw-to-canonical mapping |

Exactly one rainfall value per date. No alternative weather window may be substituted after frog
outcome readback.

## Raw-to-canonical freeze rule

Before running the real external endpoint, create a mapping receipt containing:
- original filenames and cryptographic digests;
- original column names;
- explicit mapping to canonical columns;
- date parsing rule;
- site-label mapping;
- how usable recording status is identified;
- how explicit zeros versus absent rows are represented;
- species-label normalization, if any.

No ecological summaries, species rankings, deep/shallow counts, historical alignments or endpoint
values may be inspected before that mapping receipt is frozen.
