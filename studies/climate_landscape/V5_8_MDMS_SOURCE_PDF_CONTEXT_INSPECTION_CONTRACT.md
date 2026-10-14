# v5.8 — targeted literal context inspection of official MDMS metadata PDF

**2026-10-10 JST; independent study draft PR #135; no frog outcomes or site geometries.** This contract is written before any new PDF semantic-context read. Source PDF retrieval and literal token counts were verified in v5.7.

## Question

Does the official 2-page Australian Government document actually **define** the meaning of `DESCRIPTIO`, `DATATYPENA`, and `SAMPLECOUN`, or only mention their field names? Could it support a scientific **point→independent wetland unit** mapping without further source information?

## Scope and safe extraction

- The **same public official metadata PDF** only, resource `52a2a361-b1a0-466a-a971-8e046bf99e75`, pinned exact SHA-256 `b802f313e58981e6919baa08a300303adeca86ea451a630c06c6b8ba63509b7a`.
- Extract only line-oriented text neighborhoods containing one of the **three already-observed literal field names**, with up to one neighboring line on either side; ≤160 printable characters per line; never print an entire page or complete publication. Report page number and small snippets to permit manual semantic classification.
- Drop lines with identifiable coordinate patterns, email addresses, or unrestricted geographic URL text, and collapse numerical coordinate-looking or link material. Do not fetch/print the MDMS GeoJSON, matched site labels, `NAME`, `SAMO_ID`, fauna records, or individual point-level attributes.
- The exact printed snippets are from a **public metadata PDF**, not protected monitoring data. They do **not** establish wetland identity by themselves. An appearance of “description” must not be equated to a wetland parent identifier.

## Classification rules

A verified field definition requires an explicit schema row unambiguously naming the field and explaining its purpose. If names appear without such a definition, classify as `MENTION_ONLY`. If semantics remain ambiguous, classify `NOT_RESOLVED_FROM_PDF`; neither is a biological null. Explicit point/wetland mapping requires a government-documented unit key with site version semantics, not shared description strings, point coordinates, or guesswork. Even an explicit field definition is not sufficient if it only says “point name” or “site description”.

## Frozen outcomes

If the metadata document lacks an authoritative parent wetland key, stop public-source inference, improve the *unsent* metadata enquiry to request exactly the missing source dictionary. Do not re-fit the 579-row frog table, revise the RC6 paper, infer 16 wetlands, or upgrade the v5.2 descriptive sign reversal to species-specific reproductive payoffs. No messages should be sent to custodians automatically.
