"""Plot the published species coefficients for Supplementary Figure S10."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "results/forest_use_wetland_species_20261111"


def main():
    traits = pd.read_csv(ROOT / "forest_traits_44_species.csv")
    coefficients = pd.read_csv(ROOT / "species.csv").query(
        "domain == 'all' and scale == 'rank' and term == 'woody_minus_herbaceous'")
    groups = [(2, "Forest-associated", "#137766"), (1, "Mixed habitats", "#805899"),
              (0, "Open or aquatic", "#946021")]
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 12.8), sharex=True, sharey=True)
    fig.subplots_adjust(left=.28, right=.975, top=.95, bottom=.055, wspace=.09)
    for within, ax in enumerate(axes):
        values = traits.merge(coefficients.loc[coefficients.within_route.eq(within), ["species", "estimate", "low", "high"]],
                              on="species", validate="one_to_one")
        assert len(values) == 44 and values[["estimate", "low", "high"]].notna().all().all()
        y = 0
        ticks, labels = [], []
        for score, name, color in groups:
            rows = values.loc[values.forest_score.eq(score)].sort_values("species")
            ax.text(.015, y, f"{name} ({len(rows)})", transform=ax.get_yaxis_transform(),
                    color=color, weight="bold", fontsize=9, va="center")
            for row in rows.itertuples():
                y += 1
                ax.hlines(y, row.low, row.high, color=color, lw=1)
                ax.plot(row.estimate, y, "o", ms=4, color=color,
                        markerfacecolor=color if row.routes >= 10 else "white")
                ticks.append(y)
                labels.append(row.species)
            y += 1.8
        ax.axvline(0, color="0.55", lw=.8, ls="--", zorder=0)
        ax.set_ylim(y-.6, -1)
        ax.set_yticks(ticks, labels, fontsize=8, fontstyle="italic")
        ax.tick_params(axis="y", length=0)
        ax.spines[["top","right","left"]].set_visible(False)
        ax.set_title(["A   Across sites", "B   Within survey routes"][within], loc="left", weight="bold")
        ax.grid(axis="x", alpha=.14)
    fig.supxlabel("Difference in slope change (woody minus herbaceous wetland)", y=.01, fontsize=10)
    fig.savefig(ROOT / "figure_s10.png", dpi=210)
    plt.close(fig)


if __name__ == "__main__":
    main()
