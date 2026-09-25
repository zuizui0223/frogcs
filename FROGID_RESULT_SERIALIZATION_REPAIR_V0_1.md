# FrogID result serialization repair v0.1

## Problem

`run_frogid_rain_validation_earthmover.py` wrote the terminal JSON result with a literal backslash+n suffix rather than a newline. The downstream within-cell script therefore contained a compatibility repair that stripped a terminal literal `\\n` before JSON parsing.

## Repair

Only the result-file terminator is changed:

- before: literal `\\n` characters;
- after: a real newline.

The canonical daily-weather digest construction is **not changed**. Its byte convention is already embedded in the frozen `required_daily_weather_sha256` provenance and is outside this serialization-only repair.

## Scientific boundary

This repair changes no sample, exposure, model, coefficient, threshold or claim. Legacy result files with the old literal suffix remain readable by the compatibility code in `run_frogid_within_cell_robustness.py`.
