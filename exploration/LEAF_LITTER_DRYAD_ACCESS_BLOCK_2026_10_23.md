# Dryad leaf-litter source gate: access blocked (2026-10-23)

## Executed source checks (not a negative biological result)
External published dataset: DiGiacopo & Hua (2022), [article DOI](https://doi.org/10.1007/s10452-021-09893-y), [Dryad dataset DOI](https://doi.org/10.5061/dryad.np5hqbztq). The publicly returned Dryad REST metadata identifies both `Litter_Toad_Ecology_DiGiacopo_Hua_2021.xlsx` and `LITTER_TOAD_ECOLOGY_readme.txt`. HAL version/file identifiers were resolved and metadata-level checks completed.

Two distinct public download routes were tested without unauthorized credentials:
- Official `GET /api/v2/files/{id}/download`: HTTP **401 Unauthorized**, [Actions 39794294546](https://github.com/zuizui0223/frogcs/actions/runs/39794294546). Dryad metadata endpoint was reachable; binary content was **not** returned.
- Landing-page `GET /downloads/file_stream/{id}`: HTTP **403 Forbidden**, [Actions 39857737134](https://github.com/zuizui0223/frogcs/actions/runs/39857737134). This is a separate public path; file content again **not** returned.

The `exploration/probe_dryad_leaf_litter_source_v0_1.py` source gate correctly remains **failed/blocked** rather than producing a false success receipt. It did not open animal or parasite response values and did not generate a numerical effect or publish third-party data. No further authentication-guessing or request sweeps are justified. The author paper reports relevant outcomes, but they are **literature evidence**, not new frogcs estimates.

## Decision
Do **not** promote plant-conditioned parasite changes to a newly fitted frogcs causal interaction or use reported figure values as trial-level pseudo-data. Do **not** repeatedly re-run this gate without a genuine change in authorized source access. Pivot to an open, checksum-verifiable, simultaneously randomized source or prospectively perform the `P×F×O×C` experiment. The frozen JAE RC6 main/paper/SI/submission stays untouched.

The source-only file and gate are retained for reproducibility, not portrayed as completed analysis.
