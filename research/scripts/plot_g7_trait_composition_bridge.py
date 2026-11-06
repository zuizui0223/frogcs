"""Plot only frozen G7 coefficient and held-out score summaries; no refitting."""
from pathlib import Path
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot(result_dir):
    root = Path(result_dir)
    coefficient = pd.read_csv(root / "G7_coefficient_summary.csv")
    gain = pd.read_csv(root / "G7_heldout_paired_gains.csv")
    order = [("primary", "uniform"), ("primary", "target_group"),
             ("pooled_newt_sensitivity", "uniform"),
             ("pooled_newt_sensitivity", "target_group")]
    labels = ["Newt separate · uniform", "Newt separate · target group",
              "Newt pooled · uniform", "Newt pooled · target group"]
    colors = {"uniform": "#426A98", "target_group": "#A96B26"}
    positions = [3.2, 2.4, 1.1, .3]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none", "svg.hashsalt": "frogcs-g7-20261106"})
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
    for ax, table, value, multiplier in ((axes[0], coefficient, "theta", 1.),
                                        (axes[1], gain, "gain_nll_per_survey", 1000.)):
        for y, (variant, background) in zip(positions, order):
            row = table[(table.variant == variant) & (table.background == background)]
            if len(row) != 1:
                raise ValueError("Missing or duplicate frozen G7 summary row")
            row = row.iloc[0]
            point, lower, upper = np.array([row[value], row.bootstrap_95_low,
                                            row.bootstrap_95_high], float) * multiplier
            if not np.isfinite([point, lower, upper]).all() or lower > point or point > upper:
                raise ValueError("Invalid G7 point or interval")
            ax.errorbar(point, y, xerr=[[point-lower], [upper-point]],
                        fmt="o" if variant == "primary" else "s", markersize=7,
                        color=colors[background], markeredgewidth=1.5,
                        markerfacecolor=colors[background] if variant == "primary" else "white",
                        capsize=4, elinewidth=1.7, zorder=3)
        ax.axvline(0, color="#333333", linewidth=1.1, zorder=1)
        ax.axhline(1.75, color="#CED3D8", linewidth=.8)
        ax.set_ylim(-.3, 3.8)
        ax.set_yticks(positions, labels)
        ax.grid(axis="x", color="#E6E8EB", linewidth=.7)
        ax.tick_params(axis="y", length=0)
    axes[0].set_title("A  Vegetation × species-group contrast", loc="left", pad=14, fontsize=12)
    axes[1].set_title("B  Prediction in held-out regions", loc="left", pad=14, fontsize=12)
    axes[0].set_xlabel("Change in vegetation log-odds association\nper SD of the suitability contrast", labelpad=10)
    axes[1].set_xlabel("NLL reduction per 1,000 completed visits\nPositive values favor adding the contrast", labelpad=10)
    axes[0].set_xlim(-.26, .36)
    axes[1].set_xlim(-3.4, .8)
    axes[0].set_xticks([-.2, -.1, 0., .1, .2, .3])
    axes[1].set_xticks([-3, -2, -1, 0])
    fig.suptitle("G7: salamander-group composition and frog calling", x=.035,
                 ha="left", y=.98, fontsize=16)
    fig.text(.035, .915, "4,248 sites · 63,180 visits · 56 geographic blocks · both SDM backgrounds use the same observations",
             fontsize=10.5, color="#444C55")
    fig.text(.035, .115, "Primary comparison: two tiger salamanders versus two other Ambystoma, with newts separate.\n"
             "95% intervals: 999 block refits (A); 999 paired block resamples of saved predictions (B). Open squares: fixed pooled-newt sensitivity.\n"
             "Suitability contrasts do not measure local larval duration or arrival time.",
             fontsize=9.5, color="#444C55", va="top", linespacing=1.5)
    fig.subplots_adjust(left=.235, right=.97, bottom=.29, top=.81, wspace=.3)
    fig.savefig(root / "G7_trait_composition_bridge.png", dpi=180, facecolor="white")
    vector = root / "G7_trait_composition_bridge.svg"
    fig.savefig(vector, facecolor="white", metadata={"Date": None})
    vector.write_text("\n".join(line.rstrip() for line in vector.read_text().splitlines())+"\n")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    plot(parser.parse_args().results)
