"""Render the verified G6 tables without fitting, ranking or selecting models."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--results", type=Path, required=True)
args = parser.parse_args()
gains = pd.read_csv(args.results / "G6_context_gains.csv")
ranks = pd.read_csv(args.results / "G6_R1_observed_and_heldout_rank_contrasts.csv")
if len(gains) != 216 or len(ranks) != 42:
    raise ValueError("Incomplete G6 tables")

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(2, 2, figsize=(13.2, 9.0), gridspec_kw={"height_ratios": [1, 1.15]})
comparators = ("flex_add", "flex_prior_00", "flex_all", "env_add")
comparator_labels = ("Nonlinear environment", "Both mechanisms off (00)",
                     "Four free interactions", "Simple additive environment")
candidates = ("env_add", "env_all", "flex_add", "flex_all", "flex_prior_00", "flex_prior_11")
candidate_labels = ("Simple additive environment", "Simple + free interactions", "Nonlinear environment",
                    "Nonlinear + free interactions", "Source shape 00", "Source shape 11")
for col, (bg, title) in enumerate((("uniform", "Uniform SDM"), ("target_group", "Target-group SDM"))):
    ax = axes[0, col]
    for j, baseline in enumerate(comparators):
        for v, offset, color, marker in ((0, -.13, "#667584", "o"), (1, .13, "#007f78", "s")):
            row = gains[(gains.background == bg) & (gains.partition == "V")
                        & (gains.baseline == baseline) & (gains.V == v)].iloc[0]
            value = 1000 * row.gain_per_visit
            ax.errorbar(value, 3 - j + offset,
                        xerr=[[1000 * (row.gain_per_visit - row.gain_ci_low)],
                              [1000 * (row.gain_ci_high - row.gain_per_visit)]],
                        color=color, marker=marker, capsize=3, lw=1.5, markersize=5)
    ax.axvline(0, color="#8c8c8c", lw=1)
    ax.set_yticks(range(4), list(reversed(comparator_labels)))
    ax.set_xlim(-25, 16)
    ax.set_ylim(-.5, 3.6)
    ax.grid(axis="x", alpha=.15)
    ax.set_xlabel("11 model improvement over comparator\nNLL per 1,000 visits (positive = better)")
    ax.set_title(("A. " if col == 0 else "B. ") + title, loc="left", weight="bold")

    ax = axes[1, col]
    z = ranks[(ranks.background == bg) & (ranks.subset == "all")]
    observed = z[z.response == "observed_rate"].iloc[0]
    ax.axvspan(observed.contrast_ci_low, observed.contrast_ci_high, color="#e4e8ed", alpha=.85)
    ax.axvline(observed.contrast_high_minus_low, color="#333c49", ls="--", lw=1.6)
    for j, candidate in enumerate(candidates):
        row = z[z.response == candidate].iloc[0]
        color = "#7b4596" if candidate == "flex_prior_11" else "#667584"
        ax.errorbar(row.contrast_high_minus_low, 5 - j,
                    xerr=[[row.contrast_high_minus_low - row.contrast_ci_low],
                          [row.contrast_ci_high - row.contrast_high_minus_low]],
                    color=color, marker="s" if candidate == "flex_prior_11" else "o",
                    capsize=3, lw=1.3, markersize=5)
    ax.axvline(0, color="#999999", lw=.8)
    ax.set_yticks(range(6), list(reversed(candidate_labels)))
    ax.set_xlim(-1.05, .4)
    ax.set_ylim(-.7, 5.7)
    ax.grid(axis="x", alpha=.15)
    ax.set_xlabel("High-S minus low-S Spearman correlation\nof O suitability with observed/predicted calling")
    ax.set_title(("C. " if col == 0 else "D. ") + "Original field association", loc="left", weight="bold")

fig.suptitle("Where the fixed mechanism shape agrees with frog calling", x=.04, ha="left",
             y=.985, fontsize=17, weight="bold")
fig.legend(handles=[
    Line2D([0], [0], color="#667584", marker="o", ls="none", label="V0: 3,742 sites / 55,918 visits"),
    Line2D([0], [0], color="#007f78", marker="s", ls="none", label="V1: 506 sites / 7,262 visits"),
    Line2D([0], [0], color="#333c49", ls="--", label="Observed R1 contrast (band: block interval)"),
], loc="upper center", bbox_to_anchor=(.53, .948), ncol=3, frameon=False, fontsize=9)
fig.text(.04, .018,
         "V denotes recorded flooded vegetation in the 3-km landscape proxy. Intervals: 999 whole-block draws, fixed archived fits.\n"
         "Retrospective diagnosis; no refitting or causal vegetation contrast. Rank correlations of smooth predictions and noisy rates are descriptive.",
         fontsize=8.4, color="#4d5560")
fig.tight_layout(rect=(.02, .065, .99, .90), h_pad=2.2, w_pad=2.5)
fig.savefig(args.results / "G6_field_mechanism_context_diagnostic.png", dpi=200, facecolor="white")
svg_path = args.results / "G6_field_mechanism_context_diagnostic.svg"
fig.savefig(svg_path, facecolor="white")
svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text().splitlines()) + "\n")
plt.close(fig)
