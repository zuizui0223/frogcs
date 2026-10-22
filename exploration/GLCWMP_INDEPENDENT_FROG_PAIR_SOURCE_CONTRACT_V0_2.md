# External GLCWMP pinned-source retrieval extension v0.2 — 2026-10-22

**Scope:** correct source byte retrieval only. Frozen original `GLCWMP_INDEPENDENT_FROG_PAIR_SOURCE_CONTRACT_V0_1.md` remains authoritative for sample grain, biological questions, no-outcome preflight, key uniqueness, eligibility and follow-up decision.

## Diagnostic result before opening biological responses

GitHub Actions run [39720879022](https://github.com/zuizui0223/frogcs/actions/runs/39720879022) made authenticated-free requests to BOTH:
- https://datadryad.org/api/v2/files/3932974/download and file 3932975;
- official dataset ZIP https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.hmgqnk9v8/download.

All returned **HTTP 401 Unauthorized** with no bearer token. This is an API access control condition, **not a negative ecology finding**. The workflow archived source-only failure artifact 12401141631; no occurrence values were opened or model tested.

## Only allowed correction

Dryad has an official **public web UI** download route `https://datadryad.org/downloads/file_stream/{id}` (and an older `/stash/downloads/file_stream/{id}` form redirects there). Try **only** these verified Dryad-owned UI endpoints, in addition to the original API routes. No third-party mirror, browser impersonation, CAPTCHA bypass, credential forwarding or scraping of protected content.

The expected bytes must match metadata of original version **350431** precisely:
- file **3932974** `CWMP_MaxOcc.csv`: **4,004,194 bytes** and SHA-256 **9b6e1b11d371a6bfac2b49e0aee369a57ed4fdeaeb7378c81ea79dc92c9b2587**;
- file **3932975** `README.md`: **13,021 bytes** and SHA-256 **70a0753ddcfbde7fd41178045843c68333136495d4b64f63b3af6c579865c7e8**.

If this official UI path returns HTTP 403, JavaScript bot validation, a nonmatching digest, or anything except verified source bytes, halt without frog response readback and record the exact failure. **No biology claims.**

## Decision

After one audit of this corrected path:
- PASS: freeze source-only key/grain/coverage audit before biological modeling.
- FAIL: stop the Dryad ingestion effort here, preserve the diagnostic receipt, and switch future planning to another *independently available* public wetland/frog dataset. Do not repeatedly circumvent source controls or ask the user for personal access tokens.

No RC6 paper/SI/main edits.
