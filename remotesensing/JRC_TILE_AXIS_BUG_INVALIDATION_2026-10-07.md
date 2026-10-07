# JRC tile-axis bug and invalidated hydrology receipts — 2026-10-07

## Bug

The initial JRC extraction interpreted the two numeric GeoTIFF filename offsets as COLUMN_OFFSET-ROW_OFFSET.

A response-blind GeoTIFF transform audit showed that the verified convention is:

ROW_OFFSET-COLUMN_OFFSET

with row measured southward from 80 N and column measured eastward from 180 W.

Example: the file ending 0000360000-0000160000 has bounds -140 to -130 longitude and -20 to -10 latitude, proving that 360000 is the row offset and 160000 is the column offset.

After swapping the offsets, arbitrary U.S. test points returned expected MonthlyHistory classes (1 on inland non-water; 2 at a Lake Michigan water point).

## Invalidated outputs

The following pre-fix coverage/exposure runs are retained only as debugging provenance and are not scientifically interpretable:

- workflow run 37562119092, artifact 11458528342
- workflow run 37563586045, artifact 11460079682

Their near-zero valid-pixel coverage was an indexing artefact, not evidence that JRC lacks coverage at NAAMP stops.

Any later run using the corrected row-column convention supersedes these outputs.

## Scientific boundary

No hydrology-augmented frog concentration result had been calculated before the bug was identified.

Therefore the correction changes only remote-sensing coordinate IO, not an inspected ecological result or tuned effect direction.
