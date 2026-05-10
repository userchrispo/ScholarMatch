"""
Visualization module for ScholarMatch.
Creates fit-score distribution charts using Matplotlib.
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np


def plot_score_distribution(ranked_df, user, top_n=10, save_path=None, show=False):
    """
    Generate a fit-score distribution histogram with top-N highlights.
    
    Shows:
    - Histogram of all scholarship scores (how results cluster across score range)
    - Top-N scholarships highlighted with distinct annotations
    - Clean styled chart with labeled axes
    
    Args:
        ranked_df: DataFrame from rank_scholarships() with 'fit_score' column
        user: User object (for title)
        top_n: Number of top scholarships to highlight
        save_path: Optional filepath to save the chart as PNG
    """
    scores = ranked_df["fit_score"].values
    
    # ── Figure setup ──
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Dark background style
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#161b22")
    
    # ── Histogram of all scores ──
    bins = np.linspace(0, 1, 25)
    n_vals, bin_edges, patches = ax.hist(
        scores, bins=bins,
        color="#1f6feb",
        edgecolor="#0d1117",
        linewidth=0.8,
        alpha=0.85,
        label=f"All Scholarships (n={len(scores)})",
        zorder=2
    )
    
    # ── Highlight top-N scores ──
    top_scores = scores[:top_n]
    ax.hist(
        top_scores, bins=bins,
        color="#f0883e",
        edgecolor="#0d1117",
        linewidth=0.8,
        alpha=0.95,
        label=f"Top {top_n} Matches",
        zorder=3
    )
    
    # ── Mean and median lines ──
    mean_score = np.mean(scores)
    median_score = np.median(scores)
    
    ax.axvline(mean_score, color="#58a6ff", linestyle="--", linewidth=1.5,
               label=f"Mean: {mean_score:.2f}", zorder=4)
    ax.axvline(median_score, color="#3fb950", linestyle=":", linewidth=1.5,
               label=f"Median: {median_score:.2f}", zorder=4)
    
    # ── Score zones ──
    ax.axvspan(0.75, 1.0, alpha=0.08, color="#3fb950", zorder=1)
    ax.axvspan(0.50, 0.75, alpha=0.06, color="#58a6ff", zorder=1)
    ax.axvspan(0.0, 0.50, alpha=0.04, color="#f85149", zorder=1)
    
    # Zone labels
    y_top = ax.get_ylim()[1] * 0.95
    ax.text(0.875, y_top, "★ Excellent", ha="center", va="top",
            fontsize=9, color="#3fb950", fontweight="bold", alpha=0.7)
    ax.text(0.625, y_top, "● Good", ha="center", va="top",
            fontsize=9, color="#58a6ff", fontweight="bold", alpha=0.7)
    ax.text(0.25, y_top, "○ Partial", ha="center", va="top",
            fontsize=9, color="#f85149", fontweight="bold", alpha=0.7)
    
    # ── Annotate the #1 match ──
    if len(ranked_df) > 0:
        best = ranked_df.iloc[0]
        best_score = best["fit_score"]
        best_name = best["name"][:35]
        
        # Find which bin the best score falls in
        bin_idx = np.searchsorted(bin_edges, best_score, side="right") - 1
        bin_idx = min(bin_idx, len(n_vals) - 1)
        bar_height = n_vals[bin_idx]
        
        ax.annotate(
            f"#1: {best_name}\nScore: {best_score:.2f}",
            xy=(best_score, bar_height),
            xytext=(best_score + 0.02, bar_height + max(n_vals) * 0.15),
            fontsize=8.5,
            color="#f0883e",
            fontweight="bold",
            arrowprops=dict(
                arrowstyle="->",
                color="#f0883e",
                lw=1.5,
                connectionstyle="arc3,rad=0.2"
            ),
            bbox=dict(
                boxstyle="round,pad=0.4",
                facecolor="#21262d",
                edgecolor="#f0883e",
                alpha=0.9
            ),
            zorder=5
        )
    
    # ── Styling ──
    ax.set_xlabel("Fit Score", fontsize=13, color="#c9d1d9", fontweight="bold", labelpad=10)
    ax.set_ylabel("Number of Scholarships", fontsize=13, color="#c9d1d9", fontweight="bold", labelpad=10)
    ax.set_title(
        f"Scholarship Fit-Score Distribution for {user.name}",
        fontsize=16, color="#f0f6fc", fontweight="bold", pad=20
    )
    
    # Axis formatting
    ax.set_xlim(0, 1.05)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0%}"))
    ax.tick_params(colors="#8b949e", labelsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#30363d")
    ax.spines["bottom"].set_color("#30363d")
    
    # Grid
    ax.yaxis.grid(True, color="#21262d", linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    
    # Legend
    legend = ax.legend(
        loc="upper left", fontsize=10,
        facecolor="#21262d", edgecolor="#30363d",
        labelcolor="#c9d1d9", framealpha=0.9
    )
    
    # ── Stats box ──
    stats_text = (
        f"Total Scholarships: {len(scores)}\n"
        f"Top {top_n} Avg Score: {np.mean(top_scores):.2f}\n"
        f"Excellent (>75%): {np.sum(scores >= 0.75)}\n"
        f"Good (50-74%): {np.sum((scores >= 0.50) & (scores < 0.75))}\n"
        f"Partial (<50%): {np.sum(scores < 0.50)}"
    )
    
    props = dict(boxstyle="round,pad=0.6", facecolor="#21262d",
                 edgecolor="#30363d", alpha=0.9)
    ax.text(
        0.98, 0.72, stats_text,
        transform=ax.transAxes, fontsize=9.5,
        verticalalignment="top", horizontalalignment="right",
        bbox=props, color="#c9d1d9", family="monospace"
    )
    
    plt.tight_layout()
    
    # ── Save or show ──
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor(), edgecolor="none")
        print(f"\n   [CHART] Saved to: {save_path}")
    
    if show:
        plt.show()
        print("   [CHART] Distribution chart displayed")
    else:
        plt.close(fig)
        print("   [CHART] Chart generated (saved to file)")
