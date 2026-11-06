# Frozen numerical inputs for manuscript claim verification

These **28 original numerical tables and one required P1 source receipt** are copied without modification from six source-verified GitHub Actions artifacts. They allow the existing auditor to recompute the manuscript's 44 headline claims without downloading expiring Actions artifacts. The complete file and original ZIP hashes, artifact IDs, source commits and source run IDs are in [source_bundle_manifest.json](source_bundle_manifest.json).

Every numerical table matches the original `source_file_sha256` entry in the [archived PR165 source-QA receipt](../p1_g6_editorial_integration_20261106/source/pr165_claim_qa/submission_source_QA_receipt.json). The additional P1 JSON is copied from the hash-verified original P1 ZIP and is required for the auditor's exact old-context replay assertions. This collection is an input bundle for existing calculations, not new ecological data or a new model fit.

## Replay

From the repository root in a Python environment with NumPy 2.2.6 and pandas 2.2.3:

```console
python research/scripts/audit_submission_claims_20261105.py \
  --r2 research/results/submission_frozen_sources_20261106/R2 \
  --pr161 research/results/submission_frozen_sources_20261106/R3 \
  --r4 research/results/submission_frozen_sources_20261106/R4 \
  --g2 research/results/submission_frozen_sources_20261106/G2 \
  --g2b research/results/submission_frozen_sources_20261106/G2B \
  --p1 research/results/submission_frozen_sources_20261106/P1 \
  --main editorial/MAIN_TEXT_R1_R4_SUBMISSION_CANDIDATE_2026-11-05.md \
  --si editorial/SUPPLEMENTARY_METHODS_AND_EVIDENCE_R1_R4_2026-11-05.md \
  --out /tmp/frogcs-manuscript-claim-replay
```

The [CI workflow](../../../.github/workflows/research_submission_claim_source_QA_20261105.yml) verifies all 29 input hashes before executing the auditor, then separately replays the eight G6 tables using their previously committed original inputs. The original six source archives had scheduled expiry dates of 2–5 December 2026. The numerical inputs here are retained in Git and do not depend on those temporary downloads.

This bundle does not reacquire GBIF occurrences, regenerate SDMs, rerun the biological simulations, or include the external source rasters. Those stages have separate provenance and access conditions. A Git version is a reviewable source snapshot; no new archival DOI is claimed.
