import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from replication.plotting import finalize_plot, wrap_labels


def hedges_g_and_ci_from_d(d, n1, n2, alpha=0.05):
    """Convert Cohen's d to Hedges' g with confidence intervals."""
    df = n1 + n2 - 2
    if df <= 2:
        return {"g": np.nan, "ci_low": np.nan, "ci_high": np.nan, "se_g": np.nan}

    J = 1 - (3 / (4 * df - 1))
    g = J * d
    var_g = (n1 + n2) / (n1 * n2) + (g**2) / (2 * (n1 + n2 - 2))
    se_g = np.sqrt(var_g)
    z_val = 1.96

    return {
        "g": g,
        "ci_low": g - z_val * se_g,
        "ci_high": g + z_val * se_g,
        "se_g": se_g,
    }


def make_row(
    study,
    year,
    sample_n,
    outcome,
    typ,
    g=None,
    ci_low=None,
    ci_high=None,
    d=None,
    n1=None,
    n2=None,
    note="",
):
    """Create a row for the forest plot dataframe."""
    if g is None and d is not None and n1 is not None and n2 is not None:
        result = hedges_g_and_ci_from_d(d, n1, n2)
        g = result["g"]
        ci_low = result["ci_low"]
        ci_high = result["ci_high"]

    type_desc = "meta-analysis" if typ == "Meta-analysis" else "individual program"
    n_label = f"N={sample_n}" if sample_n is not None else "N=—"

    return {
        "Study": study,
        "Year": year,
        "Outcome": outcome,
        "Type": typ,
        "TypeDesc": type_desc,
        "SMD_g": g,
        "CI_low": ci_low,
        "CI_high": ci_high,
        "N_total": sample_n,
        "n1": n1,
        "n2": n2,
        "Label": f"{study} {year} ({type_desc}) [{n_label}]",
        "Note": note,
    }


def make_metaanalysis_plot(df, wrap_width=30):
    dfp = df.copy()

    dfp["is_this_study"] = (
        dfp["Study"].astype(str).str.strip().str.casefold().eq("this study")
    )

    dfp["y_label"] = dfp.apply(
        lambda row: (
            ("This Study" if row["is_this_study"] else f"{row['Study']} {row['Year']}")
            + f" — {row['Outcome']} ({row['TypeDesc']}) "
            f"[N={int(row['N_total']) if pd.notna(row['N_total']) else '—'}]"
        ),
        axis=1,
    )

    dfp = dfp.sort_values("SMD_g", ascending=False).reset_index(drop=True)

    n_studies = len(dfp)
    fig, ax = plt.subplots(figsize=(10, 8))
    y_positions = np.arange(n_studies)

    if {"CI_low", "CI_high"}.issubset(dfp.columns) and dfp[
        ["CI_low", "CI_high"]
    ].notna().any().any():
        xmin = np.nanmin(dfp["CI_low"].to_numpy())
        xmax = np.nanmax(dfp["CI_high"].to_numpy())
        pad = (
            0.15 * (xmax - xmin) if np.isfinite(xmax - xmin) and (xmax > xmin) else 0.2
        )
        xlim = (xmin - pad, xmax + pad)
    else:
        xlim = (-0.2, 1.4)

    primary = plt.rcParams["axes.prop_cycle"].by_key()["color"][0]
    highlight_color = "red"

    for i, row in dfp.iterrows():
        y = y_positions[i]

        g = row["SMD_g"]
        lo = row.get("CI_low", np.nan)
        hi = row.get("CI_high", np.nan)

        if pd.isna(g):
            continue

        color = highlight_color if row["is_this_study"] else primary

        if pd.notna(lo) and pd.notna(hi) and (hi >= lo):
            left = g - lo
            right = hi - g
            if left >= 0 and right >= 0:
                ax.errorbar(
                    g,
                    y,
                    xerr=[[left], [right]],
                    fmt="D",
                    markersize=9,
                    color=color,
                    ecolor=color,
                    elinewidth=1.5,
                    capsize=5,
                    markeredgecolor="black",
                    markeredgewidth=0.6,
                    zorder=5,
                )
            else:
                ax.plot(
                    g,
                    y,
                    "D",
                    markersize=9,
                    color=color,
                    markeredgecolor="black",
                    markeredgewidth=0.6,
                    zorder=5,
                )
        else:
            ax.plot(
                g,
                y,
                "D",
                markersize=9,
                color=color,
                markeredgecolor="black",
                markeredgewidth=0.6,
                zorder=5,
            )

        x_right = g + 0.06
        x_left = g - 0.06
        if x_right <= xlim[1] - 0.02:
            x_text = x_right
            ha = "left"
        else:
            x_text = max(x_left, xlim[0] + 0.02)
            ha = "right"
        ax.text(
            x_text,
            y + 0.18,
            f"SMD = {g:.2f}",
            fontsize=13,
            ha=ha,
            va="center",
            color=highlight_color if row["is_this_study"] else "black",
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="none", pad=0.3),
            zorder=6,
        )

    ax.axvline(x=0, linestyle="--", color="gray", linewidth=0.8, zorder=1)

    wrapped = wrap_labels(dfp["y_label"].tolist(), width=wrap_width)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(wrapped, fontsize=14)
    for label, is_this_study in zip(ax.get_yticklabels(), dfp["is_this_study"]):
        if is_this_study:
            label.set_color(highlight_color)
    ax.set_ylim(-0.7, n_studies - 0.3)
    ax.invert_yaxis()

    ax.set_xlim(*xlim)
    ax.set_xlabel(
        "Standardized Mean Difference; positive values favor intervention", fontsize=14
    )
    ax.tick_params(axis="x", labelsize=14)

    ax.grid(True, axis="x", alpha=0.3, linestyle="-", linewidth=0.4)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(True)

    fig.subplots_adjust(left=0.38, right=0.97, top=0.95, bottom=0.12)

    finalize_plot(ax=ax)
    return fig
