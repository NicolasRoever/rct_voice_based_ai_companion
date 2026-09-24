"""Week-2 ANCOVA models, with the manuscript's HC3 standard errors."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import statsmodels.formula.api as smf
from pystout import pystout

from replication.helper import fix_pandas_append_error


def fit_main_models(df):
    models = {}
    for outcome, baseline_wave in [("gad7", 1), ("phq8", 2)]:
        for scale, suffix in [("points", ""), ("std", "_std")]:
            formula = (
                f"{outcome}_score{suffix}_w4 ~ sonia_treatment + "
                f"{outcome}_score{suffix}_w{baseline_wave} + "
                "therapy_history_w1 + efficacy_human_therapy_w2"
            )
            models[f"{outcome}_{scale}"] = smf.ols(formula, data=df).fit(cov_type="HC3")
    return models


def fit_robustness_models(df, main_model):
    controls = [
        "wtp_human_therapy_rel_w2",
        "ai_efficacy_estimate_w1",
        "ai_emotional_comfort_w1",
        "ai_privacy_level_w1",
        "ever_med_w2 + income_w2",
    ]
    return [
        main_model,
        *[
            smf.ols(main_model.model.formula + " + " + extra, data=df).fit(
                cov_type="HC3"
            )
            for extra in controls
        ],
    ]


def model_coefficients(models):
    """Save every coefficient, standard error, CI, p-value and sample size."""
    rows = []
    for name, model in models.items():
        for term in model.params.index:
            lo, hi = model.conf_int().loc[term]
            rows.append(
                {
                    "model": name,
                    "term": term,
                    "estimate": model.params[term],
                    "standard_error": model.bse[term],
                    "ci_lower": lo,
                    "ci_upper": hi,
                    "p_value": model.pvalues[term],
                    "n": int(model.nobs),
                    "adjusted_r_squared": model.rsquared_adj,
                }
            )
    return pd.DataFrame(rows)


def make_robustness_table(models):
    labels = {
        "sonia_treatment": "Treatment",
        "wtp_human_therapy_rel_w2": r"\shortstack[l]{WTP Human Therapy / Income \\ (baseline survey)}",
        "ai_efficacy_estimate_w1": r"\shortstack[l]{AI Accuracy Estimate \\ (screener survey)}",
        "ai_emotional_comfort_w1": r"\shortstack[l]{Comfort with AI Emotional Support \\ (screener survey)}",
        "ai_privacy_level_w1": "AI Privacy Concern (screener survey)",
        "ever_med_w2": "Ever Taken Medication (baseline survey)",
        "income_w2": "Household Income (baseline survey)",
    }
    fix_pandas_append_error()
    with TemporaryDirectory() as directory:
        path = Path(directory) / "table.tex"
        pystout(
            models=models,
            file=str(path),
            digits=2,
            mgroups={
                "Dependent variable: Standardised GAD-7 score at the week 2 follow-up": [
                    1,
                    6,
                ]
            },
            stars={0.1: "*", 0.05: "**", 0.01: "***"},
            varlabels=labels,
            modstat={"nobs": "N", "rsquared_adj": r"Adj. R\sym{2}"},
            addrows={"Baseline Controls": [r"\checkmark"] * 6},
            exogvars=list(labels),
        )
        return path.read_text(encoding="utf-8")
