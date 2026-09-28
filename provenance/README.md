# Provenance JSON

Root-level JSON files are intentionally prohibited. Scientific provenance is grouped here by role.

- contracts/: frozen analysis definitions and decision rules.
- summaries/: durable compact outputs used by the manuscript, SI, README or submission audits.
- receipts/: detailed machine-readable run outputs and audit receipts.
- repairs/: versioned implementation or estimability repairs.
- metadata/: claim boundaries, source identities, manifests, ledgers and other provenance metadata.

Active scripts and workflows reference these paths directly. Historical release branches preserve the old root-level layout.
