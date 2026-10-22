# NPS GLKN source transfer diagnostic and standard HTTP byte ranges — v0.5

Frozen 2026-10-22 after **three identical direct full GET truncations** (one initial workflow, two attempts under bounded retry): the official NPS frog source returned **14,538 bytes** rather than the SHA-pinned **68,581,307 bytes**. No expert frog outcome has yet been read in these attempts. Do not continue naive full-download retries.

## Scope limitation
This is **only a byte-transfer correction** to the frozen scientific v0.4 contract, never a new population, model, detection threshold, split or hypothesis. Earlier source-only preflight workflow **39722310835** successfully fetched official NPS source file (SHA256 **b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2**), and HTTP metadata probe **39721873226** verified NPS DataStore supports standard `Range: bytes=0-1023` with HTTP 206 and `Content-Range`.

## One transport diagnostic before use
On the exact original official source URL `https://irma.nps.gov/DataStore/DownloadFile/763377?Reference=2320505`, read only HTTP headers plus a bounded 16KB preview of a normal GET and a bounded 1KB Range at the start and end of the source. Log **only** metadata (status/content-type/content-length/content-range, observed preview byte counts, generic is_html indicator); do not log recording identifiers, scientific rows, audio, detection or occurrence values.

- If normal GET returns non-dataset HTML but Range returns valid native HTTP 206 byte ranges, allow **standard full file byte-range streaming** in chunks up to 4 MiB to reconstruct exactly the official source bytes.
- For each chunk require HTTP **206**, exact `Content-Range: bytes START-END/68581307`, exact chunk length, no HTML/error payload, and final complete-file SHA256 equal to `b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2`.
- No alternate host, proxy, credential/cookie injection, CAPTCHA/anti-bot circumvention, or third-party mirror. If any response indicates access denied, a mismatch, or normal range fails, **stop without outcome readback** and archive source availability as inconclusive.
- Raw bytes exist only in memory, never GitHub commit, file or artifact. The original expert status/ManualCIV QA checks and source population are immutable.

## Scientific interpretation
Until transfer succeeds and expert response QA completes, NPS independent biological replication remains **not tested**. Failed transfer cannot disconfirm the NAAMP partner network. NPS still cannot independently confirm aquatic macrophyte species, trophic mediation, NAAMP ten-stop fixed-margin null or animal attraction/competition.

No changes to frozen JAE RC6.
