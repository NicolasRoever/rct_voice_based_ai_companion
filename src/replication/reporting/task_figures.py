import matplotlib.pyplot as plt
import pandas as pd

from replication.analysis_wave_4.plots import (
    plot_gad7_baseline_vs_w4,
    plot_phq8_baseline_vs_w4,
)
from replication.benchmarking.plots import make_metaanalysis_plot
from replication.config import (
    CLEAN_DATA,
    FIGURE_NAMES,
    FIGURES,
    RESULTS,
    SCREENING_DATA,
    SRC,
)
from replication.descriptives.plot_consort import plot_consort_diagram_w124
from replication.plotting import set_plot_theme


def task_figures(
    depends_on={
        "data": CLEAN_DATA,
        "screening": SCREENING_DATA,
        "benchmarks": RESULTS / "benchmarks.csv",
        "code": [
            SRC / "plotting.py",
            SRC / "descriptives/plot_consort.py",
            SRC / "descriptives/functions.py",
            SRC / "analysis_wave_4/plots.py",
            SRC / "benchmarking/plots.py",
        ],
    },
    produces={name: FIGURES / f"{name}.pdf" for name in FIGURE_NAMES},
):
    df = pd.read_csv(depends_on["data"], low_memory=False)
    screening = pd.read_csv(depends_on["screening"], low_memory=False)
    benchmarks = pd.read_csv(depends_on["benchmarks"])
    figures = {"consort_diagram_w124": plot_consort_diagram_w124(screening, df)}
    for scale, plot in [
        ("gad7", plot_gad7_baseline_vs_w4),
        ("phq8", plot_phq8_baseline_vs_w4),
    ]:
        for group in ["treatment", "control"]:
            figures[f"{scale}_baseline_vs_w4_scatter_{group}"] = plot(df, group=group)
    for cohort in ["anxiety", "depression"]:
        set_plot_theme()
        figures[f"metaanalysis_digital_{cohort}"] = make_metaanalysis_plot(
            benchmarks.loc[benchmarks.cohort.eq(cohort)]
        )
    for name, fig in figures.items():
        produces[name].parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(
            produces[name],
            bbox_inches="tight",
            metadata={"CreationDate": None, "ModDate": None},
        )
        plt.close(fig)
