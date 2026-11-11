"""Render the primary acoustic figure from the paired route bootstrap results."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[2]
data = pd.read_csv(root / "research/results/sdm_flooded_omission_20261111/coefficients.csv")
primary = data.query("background == 'uniform' and arm == 'omit_flooded'")
terms = ["Odonata:Caudata", "Odonata:vegetation", "Caudata:vegetation", "Odonata:Caudata:vegetation"]
labels = ["Odonates × caudates", "Odonates × vegetation", "Caudates × vegetation",
          "Odonates × caudates × vegetation"]
fig, ax = plt.subplots(figsize=(7.8, 3.6), layout="constrained")
for within, offset, color, marker, label in [(0, -.13, "#136a64", "o", "Across sites"),
                                             (1, .13, "#865122", "s", "Within routes")]:
    rows = primary[primary.within_route.eq(within)].set_index("term").loc[terms]
    ax.errorbar(rows.beta, np.arange(4) + offset, xerr=[rows.beta-rows.lo, rows.hi-rows.beta],
                fmt=marker, color=color, capsize=3, label=label)
ax.set_yticks(range(4), labels)
ax.invert_yaxis()
ax.axvline(0, color="0.5", ls="--", linewidth=1)
ax.legend(frameon=False)
ax.set_xlabel("Interaction coefficient for strong frog calling (standardized ranks)")
ax.spines[["top", "right"]].set_visible(False)
fig.savefig(root / "editorial/figures/Figure1_Primary_Acoustic_Interactions.png", dpi=240)
