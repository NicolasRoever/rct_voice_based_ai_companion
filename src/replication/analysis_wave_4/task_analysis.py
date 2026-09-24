import pandas as pd

from replication.analysis_wave_4.power import calculate_preregistered_power
from replication.analysis_wave_4.regressions import (
    fit_main_models,
    fit_robustness_models,
    make_robustness_table,
    model_coefficients,
)
from replication.analysis_wave_4.tables import (
    compute_clinical_outcomes,
    compute_main_psych_results_stats,
)
from replication.config import CLEAN_DATA, RESULTS, SRC, TABLES
from replication.helper import write_csv, write_json


def task_week2_analysis(
    depends_on={
        "data": CLEAN_DATA,
        "code": [SRC / "analysis_wave_4" / f for f in ("regressions.py", "tables.py")],
        "helper": SRC / "helper.py",
    },
    produces={
        "main": RESULTS / "main_results.json",
        "clinical": RESULTS / "clinical_outcomes.json",
        "coefficients": RESULTS / "coefficients.csv",
        "robustness": TABLES / "effect_robustness_wave_4.tex",
    },
):
    df = pd.read_csv(depends_on["data"], low_memory=False)
    models = fit_main_models(df)
    values = compute_main_psych_results_stats(
        df,
        models["gad7_points"],
        models["phq8_points"],
        models["gad7_std"],
        models["phq8_std"],
    )
    write_json(produces["main"], values)
    write_json(produces["clinical"], compute_clinical_outcomes(df))
    robustness = fit_robustness_models(df, models["gad7_std"])
    all_models = {
        **models,
        **{f"robustness_{i}": model for i, model in enumerate(robustness, start=1)},
    }
    write_csv(produces["coefficients"], model_coefficients(all_models))
    produces["robustness"].parent.mkdir(parents=True, exist_ok=True)
    produces["robustness"].write_text(
        make_robustness_table(robustness), encoding="utf-8"
    )


def task_power(
    depends_on=[SRC / "analysis_wave_4/power.py", SRC / "helper.py"],
    produces=RESULTS / "power.json",
):
    write_json(produces, calculate_preregistered_power())
