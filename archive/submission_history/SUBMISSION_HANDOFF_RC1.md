# JAE submission handoff — RC1

## Article

**Title:** Recent rainfall predicts greater short-window co-calling in frog communities across continents

**Target:** Journal of Animal Ecology — Research Article

## Frozen scientific claim

Across independent North American and Australian acoustic monitoring systems, more recent rainfall is associated with greater short-window multispecies frog co-calling. The direction persists within repeatedly sampled spatial units. Prespecified analyses do not support seasonal-shoulder amplification or rainfall-driven pairwise network densification.

This is an observational association. The package does not claim causal rainfall effects, interspecific facilitation, fine-scale phase synchrony, reproductive success or demographic consequences.

## Scientific evidence locked for RC1

- NAAMP primary: 9,399 route-runs / 900 routes / 93,383 sampled stops; rain-recency OR = 0.969, 95% CI 0.941–0.998, P = 0.0388.
- NAAMP complete-10-stop sensitivity: P = 0.058; retained explicitly as a limitation.
- FrogID validation: 40,754 expert-validated recordings; dry-spell OR = 0.853, 95% CI 0.827–0.879, P = 1.13e-24.
- Within-route NAAMP diagnostic: beta = -0.01367, 95% CI -0.01998 to -0.00737, P = 2.15e-5.
- Within-cell FrogID diagnostic: beta = -0.04265, 95% CI -0.05175 to -0.03354, P = 4.30e-20.
- Seasonal-shoulder interaction: unsupported.
- Pairwise network densification: unsupported.

## Reproducibility boundary

The canonical scientific package on `main` is the verified 49-file export copied from the original frozen archive.

- source/target Git tree identity: `fb534743e229082328858943f9a544b7f4716907`
- canonical content identity: `16960cbf4f5f5f3aa9175115b108125409acfe9c7e2ef013e23d90a9b4cd27da`
- scientific result files on `submission/jae-v1` are unchanged from `main`
- submission branch changes are limited to standalone path repairs, QA workflows, DOCX generation and editorial submission documents

## Automated QA

Latest frogcs-native checks at the pre-RC handoff:

- submission QA: success
- anonymous DOCX generation: success
- manuscript guard: 3,111 words
- numbered abstract: 299 words
- keywords: 8
- deterministic figures: pass
- frozen scientific input hashes: pass

## Files for submission

- `MANUSCRIPT_JAE_V0_3.md`
- `JAE_TITLE_PAGE_V0_1.template.md`
- `figures/FIGURE_1_DESIGN_V0_1.svg`
- `figures/FIGURE_2_EFFECTS_V0_1.svg`
- `submission/COVER_LETTER_JAE_V0_1.md`
- generated anonymous DOCX from GitHub Actions

## Remaining blockers

No further ecological outcome search is authorized for RC1.

Only the following may delay actual journal submission:

1. final author set and order;
2. affiliations and corresponding-author metadata;
3. CRediT contributions;
4. funding / acknowledgements;
5. conflict-of-interest statement;
6. all-author approval and confirmation of no simultaneous submission;
7. repository/archive license confirmation;
8. archival DOI minting and insertion into Data Availability.

## DOI deposition preparation

`submission/ZENODO_METADATA_TEMPLATE.json` contains the non-human metadata already fixed by the project. Bracketed fields must be replaced before deposition. A dedicated Zenodo connector is not available in the current tool environment, so DOI minting remains an external publication action.
