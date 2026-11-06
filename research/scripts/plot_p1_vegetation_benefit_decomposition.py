"""Draw the complete, source-checked P1 vegetation-effect decomposition.

The source experiment was fixed before its original outcomes. This decomposition
is a post hoc interpretation of that experiment, not a new field test. The plot
retains all four timing conditions and all four focal vegetation-function arms.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


TIMINGS = ("LS", "LL", "ES", "EL")
TERMS = ("refuge", "feeding_support", "nonadditivity", "net")
CHANGES = ("pure_arrival", "pure_duration", "arrival_x_duration", "EL_minus_LS")
COLORS = {
    "refuge": "#286A95",
    "feeding_support": "#BD632E",
    "nonadditivity": "#777583",
    "net": "#202936",
}
MARKERS = {"refuge": "o", "feeding_support": "s", "nonadditivity": "^", "net": "D"}
TERM_LABELS = {
    "refuge": "Refuge from salamanders",
    "feeding_support": "Odonate feeding support",
    "nonadditivity": "Nonadditive component",
    "net": "Both functions minus neither",
}
TIMING_LABELS = (
    "Late / short\nDay 40; 40 days",
    "Late / long\nDay 40; 60 days",
    "Early / short\nDay 0; 40 days",
    "Early / long\nDay 0; 60 days",
)
CHANGE_LABELS = (
    "Greater refuge\nbenefit",
    "Lower feeding-\nsupport cost",
    "Nonadditive\nchange",
    "Net change",
)


def require(condition: bool, message: str) -> None:
    if not bool(condition):
        raise ValueError(message)


def source_points(source_path: Path) -> pd.DataFrame:
    """Recompute each plotted mean directly from all 4,096 source scenarios."""
    raw = pd.read_csv(source_path, dtype={"arm": str, "stage_design": str})
    require(len(raw) == 4096 and raw.source_id.nunique() == 256,
            "Expected all 4,096 P1 scenarios and 256 source backgrounds")
    require(not raw.duplicated(["source_id", "stage_design", "arm"]).any(),
            "Duplicate P1 source background / timing / function arm")
    columns = pd.MultiIndex.from_product([TIMINGS, ("00", "10", "01", "11")])
    values = raw.pivot(index="source_id", columns=["stage_design", "arm"],
                       values="mean_log_F_B").reindex(columns=columns).to_numpy()
    require(values.shape == (256, 16) and np.isfinite(values).all(),
            "Missing P1 timing condition or focal-function arm")
    values = values.reshape(256, 4, 4)
    terms = np.stack([
        values[:, :, 1] - values[:, :, 0],
        values[:, :, 2] - values[:, :, 0],
        values[:, :, 3] - values[:, :, 1] - values[:, :, 2] + values[:, :, 0],
        values[:, :, 3] - values[:, :, 0],
    ], axis=2)
    require(np.allclose(terms[:, :, :3].sum(axis=2), terms[:, :, 3],
                        rtol=0, atol=1e-12), "Source factorial identity failed")
    changed = np.stack([
        (terms[:, 2] - terms[:, 0] + terms[:, 3] - terms[:, 1]) / 2,
        (terms[:, 1] - terms[:, 0] + terms[:, 3] - terms[:, 2]) / 2,
        terms[:, 3] - terms[:, 2] - terms[:, 1] + terms[:, 0],
        terms[:, 3] - terms[:, 0],
    ], axis=1)
    records = []
    for kind, contrasts, array in (("timing", TIMINGS, terms), ("change", CHANGES, changed)):
        for ci, contrast in enumerate(contrasts):
            for ti, term in enumerate(TERMS):
                records.append({"kind": kind, "contrast": contrast, "term": term,
                                "mean": float(array[:, ci, ti].mean())})
    return pd.DataFrame(records).set_index(["kind", "contrast", "term"])


def load_summary(summary_path: Path, source_path: Path) -> pd.DataFrame:
    summary = pd.read_csv(summary_path)
    fields = {"kind", "contrast", "term", "mean", "mc95_low", "mc95_high", "n_sources"}
    require(fields <= set(summary.columns), "Decomposition summary is missing required fields")
    require(not summary.duplicated(["kind", "contrast", "term"]).any(),
            "Duplicate decomposition summary keys")
    summary = summary.set_index(["kind", "contrast", "term"])
    raw = source_points(source_path)
    require(set(summary.index) == set(raw.index),
            "Summary must retain all four timing conditions and all four changes")
    summary = summary.loc[raw.index]
    require(summary.n_sources.eq(256).all(), "Source background count changed")
    numeric = summary[["mean", "mc95_low", "mc95_high"]].to_numpy(float)
    require(np.isfinite(numeric).all(), "Non-finite estimate or interval")
    require((summary.mc95_low <= summary["mean"]).all() and
            (summary["mean"] <= summary.mc95_high).all(), "Invalid pointwise interval")
    require(np.allclose(summary["mean"], raw["mean"], rtol=0, atol=1e-12),
            "A plotted mean does not reproduce the original P1 source")
    return summary.sort_index()


def draw_interval(ax, row, ypos: float, term: str, *, marker_size: float = 6.3) -> None:
    mean = float(row["mean"])
    low = float(row["mc95_low"])
    high = float(row["mc95_high"])
    ax.errorbar(
        mean, ypos, xerr=np.array([[mean - low], [high - mean]]),
        color=COLORS[term], marker=MARKERS[term], markersize=marker_size,
        markerfacecolor="white" if term == "nonadditivity" else COLORS[term],
        markeredgewidth=1.3, linewidth=1.5, capsize=3.0, capthick=1.2,
        linestyle="none", zorder=5 if term == "net" else 4,
    )


def style_axis(ax) -> None:
    ax.axvline(0, color="#7B8087", linewidth=1.0, zorder=2)
    ax.grid(axis="x", color="#E4E7EA", linewidth=0.7, zorder=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#6F7780")
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(axis="y", length=0, pad=11)
    ax.tick_params(axis="x", width=0.8, length=3, pad=6)


def run(summary_path: Path, source_path: Path, output: Path) -> tuple[Path, Path]:
    summary = load_summary(summary_path, source_path)
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10.5,
        "axes.labelsize": 11.0, "axes.titlesize": 12.5,
        "xtick.labelsize": 10.0, "ytick.labelsize": 10.4,
        "text.color": "#202936", "axes.labelcolor": "#202936",
        "xtick.color": "#424B56", "ytick.color": "#202936",
        "figure.facecolor": "white", "axes.facecolor": "white",
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })
    fig = plt.figure(figsize=(14.4, 7.7))
    axes = fig.subplots(1, 2, gridspec_kw={"width_ratios": (1.16, 1.0)})
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.21, top=0.72, wspace=0.63)
    fig.text(0.025, 0.955, "Why the vegetation effect changes sign",
             ha="left", va="top", fontsize=18.3, weight="bold")
    fig.text(0.025, 0.907,
             "P1 model experiment  |  Salamander arrival and aquatic duration, with two vegetation functions crossed",
             ha="left", va="top", fontsize=11.3, color="#4D5763")
    handles = [Line2D([0], [0], color=COLORS[term], marker=MARKERS[term],
                      markerfacecolor="white" if term == "nonadditivity" else COLORS[term],
                      linewidth=1.5, markersize=6.3, label=TERM_LABELS[term]) for term in TERMS]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.02, 0.86),
               ncol=4, frameon=False, fontsize=10.5, columnspacing=2.1,
               handlelength=2.1, handletextpad=0.65)

    ax = axes[0]
    ypos = np.arange(len(TIMINGS), dtype=float)
    offsets = {"refuge": -0.27, "feeding_support": -0.09,
               "nonadditivity": 0.09, "net": 0.27}
    for yi, timing in zip(ypos, TIMINGS):
        for term in TERMS:
            draw_interval(ax, summary.loc[("timing", timing, term)], yi + offsets[term], term)
        if yi < 3:
            ax.axhline(yi + 0.5, color="#ECEEF0", linewidth=0.7, zorder=0)
    ax.set_yticks(ypos, TIMING_LABELS)
    ax.set_ylim(3.55, -0.58)
    ax.set_xlim(-0.32, 0.32)
    ax.set_xticks(np.arange(-0.3, 0.31, 0.1))
    ax.set_xlabel("Effect on log frog cohort abundance", labelpad=10)
    ax.set_title("A   All four developmental conditions", loc="left", pad=15, weight="bold")
    style_axis(ax)

    ax = axes[1]
    ypos = np.array([0, 1, 2, 3.3])
    selected = summary.loc[("change", "EL_minus_LS")].loc[list(TERMS)]
    for yi, term in zip(ypos, TERMS):
        row = selected.loc[term]
        draw_interval(ax, row, yi, term, marker_size=7.3)
        ax.text(0.485, yi, f"{row['mean']:+.3f}", ha="right", va="center",
                color=COLORS[term], fontsize=11.0,
                weight="bold" if term == "net" else "normal")
    ax.axhline(2.65, color="#C7CDD3", linewidth=0.8)
    ax.set_yticks(ypos, CHANGE_LABELS)
    ax.set_ylim(3.9, -0.6)
    ax.set_xlim(-0.055, 0.50)
    ax.set_xticks(np.arange(0.0, 0.41, 0.1))
    ax.set_xlabel("Change in the vegetation effect (log scale)", labelpad=10)
    ax.set_title("B   From late / short to early / long", loc="left", pad=15, weight="bold")
    style_axis(ax)

    fig.text(0.025, 0.11,
             "Post hoc decomposition of the complete model factorial: 256 matched food-web backgrounds; all four function arms retained.",
             fontsize=10.0, ha="left", color="#4D5763")
    fig.text(0.025, 0.077,
             "Points show means; intervals are pointwise 95% paired source-bootstrap ranges (10,000 resamples). Components sum to the net effect.",
             fontsize=10.0, ha="left", color="#4D5763")
    fig.text(0.025, 0.044,
             "Both-minus-neither switches only the two focal functions. Values describe simulated aquatic frog cohorts, not measured field responses.",
             fontsize=10.0, ha="left", color="#4D5763")

    output.mkdir(parents=True, exist_ok=True)
    png = output / "P1_vegetation_benefit_decomposition.png"
    pdf = output / "P1_vegetation_benefit_decomposition.pdf"
    title = "P1 model vegetation benefit decomposition"
    provenance = (f"Post hoc P1 model decomposition; 256 backgrounds. "
                  f"Summary SHA256: {hashlib.sha256(summary_path.read_bytes()).hexdigest()}. "
                  f"Original source SHA256: {hashlib.sha256(source_path.read_bytes()).hexdigest()}.")
    fig.savefig(png, dpi=210, metadata={"Title": title, "Description": provenance})
    fig.savefig(pdf, metadata={"Title": title, "Subject": provenance,
                              "Creator": Path(__file__).name})
    plt.close(fig)
    print(f"P1_DECOMPOSITION_FIGURE_SOURCE_MEANS_VERIFIED {png}")
    print(f"P1_DECOMPOSITION_VECTOR_EXPORT {pdf}")
    return png, pdf


if __name__ == "__main__":
    repo_research = Path(__file__).resolve().parents[1]
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--summary", type=Path, default=repo_research / "results" /
                     "p1_vegetation_benefit_20261106" / "p1_decomposition_summary.csv")
    cli.add_argument("--source", type=Path, default=repo_research / "results" /
                     "submission_frozen_sources_20261106" / "P1" /
                     "P1_original4096_isolated_timing_duration_80year.csv.gz")
    cli.add_argument("--output", type=Path, default=repo_research / "results" /
                     "p1_vegetation_benefit_20261106")
    args = cli.parse_args()
    run(args.summary, args.source, args.output)
