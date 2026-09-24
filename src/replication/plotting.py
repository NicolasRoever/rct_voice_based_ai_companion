import textwrap

import matplotlib.pyplot as plt
import seaborn as sns


def wrap_labels(labels, width=25):
    """Wrap category labels to multiple lines."""
    return [textwrap.fill(str(label), width) for label in labels]


def set_plot_theme():
    sns.set_theme(
        style="white",  # consistent with file_context_0
        font="sans-serif",  # Changed to sans-serif for Arial
        font_scale=1.4,  # Increased font scale for larger text
    )

    palette = ["#1B2A4A", "#C17B7B", "#7BA7CC", "#00a087", "#f39b7f"]
    sns.set_palette(palette=palette, n_colors=5)

    plt.rcParams.update(
        {
            "text.usetex": False,  # Disabled LaTeX for Arial compatibility
            "font.family": "sans-serif",  # Enforce sans-serif
            "font.sans-serif": [
                "Arial",
                "DejaVu Sans",
                "Helvetica",
                "sans-serif",
            ],  # Prioritize Arial
            "axes.titlesize": 16,  # Increased title size
            "axes.labelsize": 16,  # Increased label size
            "legend.frameon": False,
            "figure.figsize": (8, 5),
            "lines.linewidth": 2,
            "lines.markersize": 6,
            "axes.grid": False,  # Disable grid
            "axes.titlepad": 40,
        }
    )


def finalize_plot(ax=None, fontsize=10, legend_linewidth=1.0, legend_fontsize=10):
    if ax is None:
        ax = plt.gca()

    sns.despine(ax=ax)

    ax.tick_params(axis="x", labelsize=fontsize)
    ax.tick_params(axis="y", labelsize=fontsize)

    legend = ax.get_legend()
    if legend is not None:
        for text in legend.get_texts():
            text.set_fontsize(fontsize=legend_fontsize)

    ax.figure.tight_layout()
