# Source attribution and reproduction

Kaczmarski, M., Kaczmarek, J. M., Radzińska, A. & Budka, M. (2025).
*Passive acoustic monitoring reveals seasonal patterns in European green toad calling activity but fails to accurately reflect population abundance.* Scientific Reports 15, 26447.
https://doi.org/10.1038/s41598-025-11706-3

Official supplementary material is preserved unchanged in `green_toad_supplement.zip` and the selected extracted `green_toad/SupplMat/` files. Download URL and hashes are in `access_receipt.json`. Article licence: [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/), as stated in the [author article](https://pmc.ncbi.nlm.nih.gov/articles/PMC12279945/). These third-party source materials are not relicensed under the repository's code licence. No author endorsement is implied.

`analyze_green_toad.py`, `ANALYSIS_DESIGN.md`, the calibration JSON and held-out prediction CSV are this repository's separate numerical reanalysis, not modifications to the original source tables. Run `python research/results/public_calibration_20261029/analyze_green_toad.py` with numpy, pandas, scipy and openpyxl. Both response and predictors are counts, not detection-corrected densities. This is not a NAAMP calibration or a three-guild mechanism test.
