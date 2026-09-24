import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from replication.plotting import finalize_plot, set_plot_theme


def plot_baseline_vs_w4_scatter(
    df,
    baseline_col,
    w4_col,
    xlabel,
    ylabel,
    group="treatment",
    figsize=(7, 6),
    return_stats=False,
):
    """Plot paired scores, optionally returning the unjittered worsening statistics."""
    set_plot_theme()

    if group == "treatment":
        mask = df["sonia_treatment"] == 1
    elif group == "control":
        mask = df["sonia_treatment"] == 0
    else:
        mask = pd.Series([True] * len(df), index=df.index)

    d = df.loc[mask, [baseline_col, w4_col]].dropna().copy()
    got_worse = d[w4_col] > d[baseline_col]
    pct_worse = got_worse.mean() * 100

    rng = np.random.default_rng(seed=42)
    jitter = 0.2
    d[baseline_col] = d[baseline_col] + rng.uniform(-jitter, jitter, len(d))
    d[w4_col] = d[w4_col] + rng.uniform(-jitter, jitter, len(d))

    color_better = sns.color_palette()[0]
    color_worse = sns.color_palette()[1]

    fig, ax = plt.subplots(figsize=figsize)

    pct_better = 100 - pct_worse

    ax.scatter(
        d.loc[~got_worse, baseline_col],
        d.loc[~got_worse, w4_col],
        color=color_better,
        alpha=0.6,
        label=f"Improved / No Change ({pct_better:.1f}%)",
        s=40,
    )
    ax.scatter(
        d.loc[got_worse, baseline_col],
        d.loc[got_worse, w4_col],
        color=color_worse,
        alpha=0.6,
        label=f"Any Worsening ({pct_worse:.1f}%)",
        s=40,
    )

    all_vals = pd.concat([d[baseline_col], d[w4_col]])
    lo, hi = all_vals.min(), all_vals.max()
    ax.plot([lo, hi], [lo, hi], color="grey", linestyle="--", linewidth=1)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(frameon=True)

    finalize_plot(ax=ax)
    plt.close()
    if return_stats:
        return fig, {"n_worse": int(got_worse.sum()), "pct_worse": pct_worse}
    return fig


def plot_gad7_baseline_vs_w4(df, group="treatment", figsize=(7, 6), return_stats=False):
    return plot_baseline_vs_w4_scatter(
        df=df,
        baseline_col="gad7_score_w1",
        w4_col="gad7_score_w4",
        xlabel="GAD-7 score (screener survey)",
        ylabel="GAD-7 score (week 2 follow-up)",
        group=group,
        figsize=figsize,
        return_stats=return_stats,
    )


def plot_phq8_baseline_vs_w4(df, group="treatment", figsize=(7, 6), return_stats=False):
    return plot_baseline_vs_w4_scatter(
        df=df,
        baseline_col="phq8_score_w2",
        w4_col="phq8_score_w4",
        xlabel="PHQ-8 score (baseline survey)",
        ylabel="PHQ-8 score (week 2 follow-up)",
        group=group,
        figsize=figsize,
        return_stats=return_stats,
    )
