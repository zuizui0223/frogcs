# Analysis provenance ledger v0.1

This ledger records externally timestamped GitHub history from the original `zuizui0223/284b` frog incubator and the standalone `frogcs` repair branch. Its purpose is to distinguish analyses whose contracts were committed before effect readback from post-opening diagnostics added during pre-submission review.

All timestamps below are Git commit author timestamps in UTC. Commit links are public GitHub objects.

## Original NAAMP primary

| Stage | Commit | UTC timestamp |
|---|---|---|
| Freeze model before effects | `1d04c8c837f9` — Freeze NAAMP synchrony model before effects | 2026-09-24 15:10:55 |
| Implement frozen model | `17420ef3aa0e` | 2026-09-24 15:11:04 |
| Run frozen primary | `23eeaa6e0111` | 2026-09-24 15:11:07 |
| Freeze positive result receipt | `bee819d06263` | 2026-09-24 15:13:14 |

The model-freeze commit therefore predates primary effect execution.

## NAAMP secondary endpoints

| Stage | Commit | UTC timestamp |
|---|---|---|
| Freeze temperature + seasonal shoulder endpoints | `de881f059dce` | 2026-09-24 22:11:50 |
| Implement frozen secondary analyses | `5a51a9e5e20a` | 2026-09-24 22:11:58 |
| Run secondary analyses | `5e3b9b4954bb` | 2026-09-24 22:12:03 |

The later H3 hierarchy repair is explicitly labelled a specification repair, not a preregistered redefinition.

## NAAMP pairwise-network H4

| Stage | Commit | UTC timestamp |
|---|---|---|
| Freeze network endpoint | `d448f7e8577a` | 2026-09-24 22:17:51 |
| Implement H4 | `047a6728c28c` | 2026-09-24 22:17:54 |
| Run H4 | `946c774477d8` | 2026-09-24 22:17:57 |
| Close H4 unsupported | `89f2b803e9d5` | 2026-09-24 22:20:43 |

## Joint weather / seasonal robustness

| Stage | Commit | UTC timestamp |
|---|---|---|
| Freeze joint weather + DOY robustness | `2131191ee283` | 2026-09-24 22:20:45 |
| Implement | `c0dc75866fdc` | 2026-09-24 22:20:48 |
| Run | `579efacd22a1` | 2026-09-24 22:20:50 |

Recovered Actions run: `36066905845`; artifact `10836268800`.

## NAAMP activation versus conditional-overlap decomposition

| Stage | Commit | UTC timestamp |
|---|---|---|
| Freeze mechanism decomposition | `5a6a06fb3af7` | 2026-09-24 22:27:43 |
| Implement | `811f110c4f0d` | 2026-09-24 22:27:47 |
| Run | `be768ae8f45c` | 2026-09-24 22:27:50 |

Recovered Actions run: `36067567986`; artifact `10837505560`.

This decomposition predates the later pre-submission review that independently identified the same activation-versus-association issue.

## FrogID external validation

The FrogID programme underwent several structural/source repairs before weather effects were opened. The final ERA5 transport path is documented by:

| Stage | Commit | UTC timestamp |
|---|---|---|
| Freeze final ERA5 validation transport | `830d898fdf74` | 2026-09-25 00:30:22 |
| Document final contract | `f00abcc0a100` | 2026-09-25 00:30:25 |
| Implement final validation | `d6bf0b78a804` | 2026-09-25 00:31:52 |
| Run frozen validation | `8bc4e8de81bd` | 2026-09-25 00:31:55 |
| Freeze successful validation receipt | `df4cfb269f34` | 2026-09-25 00:41:50 |

The later reruns at fixed contracts were transport/reproducibility reruns and did not redefine the scientific endpoint.

## Spatial-confounding diagnostics

| Stage | Commit | UTC timestamp |
|---|---|---|
| Freeze within-space robustness | `35b7b3722f2f` | 2026-09-25 01:58:37 |
| Run diagnostics | `d6aa1d88abd0` | 2026-09-25 01:58:45 |
| Record results | `8af48714b758` | 2026-09-25 02:10:54 |

These diagnostics were explicitly post-opening robustness analyses.

## Standalone pre-submission repairs

The following are **not** described as original prospective tests:

- active-pool richness;
- observed-minus-independence co-calling residual;
- mean pairwise excess covariance;
- H3 hierarchy correction;
- DaysSinceRain range/sentinel audit;
- FrogID eventTime/timezone semantics audits.

For the NAAMP reviewer repair, `NAAMP_REVIEW_REPAIR_CONTRACT_V0_1.json` was committed before Actions run `36112049537`; the replacement H3 sensitivity was separately frozen before Actions run `36112267989`.

These analyses are labelled “reviewer-motivated post-opening diagnostics” or “specification repair” throughout the revised manuscript and cannot replace the original endpoint decisions.

## Wording rule

The revised paper should use:

> “versioned analysis contracts committed before the corresponding effect readbacks”

for the original primary/validation/secondary analyses.

It should **not** imply that the post-opening reviewer diagnostics were preregistered or prospectively conceived before the original data were seen.
