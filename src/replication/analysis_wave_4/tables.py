import math

import numpy as np
import pandas as pd
from statsmodels.stats.proportion import confint_proportions_2indep


def compute_main_effect_estimates(
    main_gad7_points_model,
    main_phq_points_model,
    main_gad7_std_model,
    main_phq_std_model,
):
    """Single source of truth for the main wave-4 treatment-effect numbers."""

    def effect_and_ci(model, name="sonia_treatment"):
        b = model.params[name]
        lo, hi = model.conf_int().loc[name]
        return b, lo, hi

    g_pt, g_pt_lo, g_pt_hi = effect_and_ci(main_gad7_points_model)
    p_pt, p_pt_lo, p_pt_hi = effect_and_ci(main_phq_points_model)
    g_d, g_d_lo, g_d_hi = effect_and_ci(main_gad7_std_model)
    p_d, p_d_lo, p_d_hi = effect_and_ci(main_phq_std_model)

    return {
        "main_gad7_points_effect_w4": f"{g_pt:.2f}",
        "main_gad7_points_95ci_lower_w4": f"{g_pt_lo:.2f}",
        "main_gad7_points_95ci_upper_w4": f"{g_pt_hi:.2f}",
        "main_gad7_std_effect_w4": f"{g_d:.2f}",
        "main_gad7_std_95ci_lower_w4": f"{g_d_lo:.2f}",
        "main_gad7_std_95ci_upper_w4": f"{g_d_hi:.2f}",
        "main_phq8_points_effect_w4": f"{p_pt:.2f}",
        "main_phq8_points_95ci_lower_w4": f"{p_pt_lo:.2f}",
        "main_phq8_points_95ci_upper_w4": f"{p_pt_hi:.2f}",
        "main_phq8_std_effect_w4": f"{p_d:.2f}",
        "main_phq8_std_95ci_lower_w4": f"{p_d_lo:.2f}",
        "main_phq8_std_95ci_upper_w4": f"{p_d_hi:.2f}",
    }


def compute_main_psych_results_stats(
    df,
    main_gad7_points_model,
    main_phq_points_model,
    main_gad7_std_model,
    main_phq_std_model,
):
    """Compute statistics using the manuscript placeholder keys."""
    result = {}

    arms = {
        "ctrl": df[df["research_arm"] == "webapp"],
        "treat": df[df["research_arm"] == "sonia"],
    }
    outcomes = {
        "gad7": ("gad7_score_w1", "gad7_score_w4"),
        "phq8": ("phq8_score_w2", "phq8_score_w4"),
    }
    for outcome, (baseline_col, endline_col) in outcomes.items():
        for arm, group in arms.items():
            for wave, col in (("base", baseline_col), ("2wk", endline_col)):
                key = f"{outcome}_{wave}_{arm}"
                result[key] = f"{group[col].mean():.1f}"
                result[f"{key}_sd"] = f"{group[col].std(ddof=1):.1f}"

            paired = group[[baseline_col, endline_col]].dropna()
            reduction = paired[baseline_col] - paired[endline_col]
            result[f"{outcome}_reduction_{arm}"] = f"{reduction.mean():.1f}"

    for arm, group in arms.items():
        counts = [
            group[[base, follow]].count().tolist() for base, follow in outcomes.values()
        ]
        if counts[0] != counts[1]:
            raise ValueError(
                "The shared N row requires equal GAD-7 and PHQ-8 sample sizes."
            )
        result[f"table_baseline_{arm}_n"] = int(counts[0][0])
        result[f"table_followup_{arm}_n"] = int(counts[0][1])
    nobs = [
        model.nobs
        for model in [
            main_gad7_points_model,
            main_phq_points_model,
            main_gad7_std_model,
            main_phq_std_model,
        ]
    ]
    if len(set(nobs)) != 1:
        raise ValueError("The shared N row requires equal ANCOVA sample sizes.")
    result["table_ancova_n"] = int(nobs[0])

    result.update(
        compute_main_effect_estimates(
            main_gad7_points_model=main_gad7_points_model,
            main_phq_points_model=main_phq_points_model,
            main_gad7_std_model=main_gad7_std_model,
            main_phq_std_model=main_phq_std_model,
        )
    )

    return result


def _risk_diff_ci(k_t, k_c, n_t, n_c, alpha=0.05):
    """Treatment minus control with a Newcombe--Wilson CI, no continuity correction."""
    if n_t == 0 or n_c == 0:
        return np.nan, (np.nan, np.nan)
    rd = k_t / n_t - k_c / n_c
    ci = confint_proportions_2indep(
        k_t,
        n_t,
        k_c,
        n_c,
        method="newcomb",
        compare="diff",
        alpha=alpha,
        correction=False,
    )
    return rd, ci


def compute_clinical_outcomes(
    df,
    *,
    gad_case_cutoff=10,
    gad_remit_cutoff=4,  # remission: score <= 4
    gad_sub10_cutoff=10,  # GAD-7 < 10 == below clinical-anxiety screening threshold
    phq_case_cutoff=10,
    phq_remit_cutoff=4,  # remission: score <= 4
    phq_sub10_cutoff=10,  # PHQ-8 < 10 == below clinical-depression screening threshold
    response_fraction=0.50,
    alpha=0.05,
):
    """Compute baseline caseness, follow-up symptom states, and response."""

    def _arm_stats(arm, indicator, eligible):
        """Proportion of an outcome within the *eligible* (denominator) sample.

        ``eligible`` is a boolean column flagging the participants who have the
        data required to evaluate this outcome (e.g. a non-missing wave-4
        score). Because of attrition by 2 weeks, this denominator is generally
        smaller than ``len(arm)`` and differs across outcomes, so it must be
        computed per outcome rather than as the full arm size.
        """
        elig = arm[arm[eligible]]
        n = len(elig)
        if n == 0:
            return np.nan, 0, 0
        k = elig[indicator].sum()
        p = k / n
        return p, int(k), int(n)

    def _format_pct_n(p, k, n):
        if n == 0 or pd.isna(p):
            return "NA"
        return f"{100 * p:.1f}\\% ({k}/{n})"

    def _format_rd_ci(rd, ci):
        if pd.isna(rd):
            return "NA"
        try:
            lo, hi = ci
            if pd.isna(lo) or pd.isna(hi):
                return "NA"
        except (TypeError, ValueError):
            return "NA"
        return f"[{100 * lo:.1f}, {100 * hi:.1f}]"

    def _response(baseline, followup, fraction):
        eligible = baseline.notna() & followup.notna()
        reduction = (baseline - followup) / baseline.where(baseline > 0)
        return reduction >= fraction, eligible

    df = df.copy()

    df["gad_case_w1"] = df["gad7_score_w1"] >= gad_case_cutoff
    df["gad_case_elig"] = df["gad7_score_w1"].notna()

    df["gad_remit_w4"] = df["gad7_score_w4"] <= gad_remit_cutoff
    df["gad_remit_elig"] = df["gad7_score_w4"].notna()

    df["gad_sub10_w4"] = df["gad7_score_w4"] < gad_sub10_cutoff
    df["gad_sub10_elig"] = df["gad7_score_w4"].notna()

    df["gad_resp_w4"], df["gad_resp_elig"] = _response(
        df["gad7_score_w1"], df["gad7_score_w4"], response_fraction
    )

    df["phq_case_w2"] = df["phq8_score_w2"] >= phq_case_cutoff
    df["phq_case_elig"] = df["phq8_score_w2"].notna()
    df["phq_improvement_elig"] = df["phq_case_w2"] & df["phq8_score_w4"].notna()

    df["phq_remit_w4"] = df["phq8_score_w4"] <= phq_remit_cutoff

    df["phq_sub10_w4"] = df["phq8_score_w4"] < phq_sub10_cutoff

    df["phq_resp_w4"], _ = _response(
        df["phq8_score_w2"], df["phq8_score_w4"], response_fraction
    )

    ctrl = df[df["research_arm"] == "webapp"]
    trt = df[df["research_arm"] == "sonia"]

    res = {}

    def add_outcome(prefix, col_name, elig_name, *, show_ci=True):
        p_c, k_c, n_c = _arm_stats(ctrl, col_name, elig_name)
        p_t, k_t, n_t = _arm_stats(trt, col_name, elig_name)

        res[f"{prefix}_ctrl"] = _format_pct_n(p_c, k_c, n_c)
        res[f"{prefix}_trt"] = _format_pct_n(p_t, k_t, n_t)

        rd, ci = _risk_diff_ci(k_t, k_c, n_t, n_c, alpha=alpha)
        res[f"{prefix}_rd"] = f"{100 * rd:.1f}" if not pd.isna(rd) else "NA"
        res[f"{prefix}_rd_ci"] = _format_rd_ci(rd, ci) if show_ci else "---"
        return rd, ci

    def add_nnt(prefix, rd, ci):
        res[f"{prefix}_arr"] = "NA"
        res[f"{prefix}_nnt"] = "NA"
        res[f"{prefix}_nnt_ci"] = "NA"
        if pd.isna(rd) or rd <= 0:
            return
        lo, hi = ci
        if pd.isna(lo) or pd.isna(hi):
            return
        res[f"{prefix}_arr"] = f"{100 * rd:.1f}"
        res[f"{prefix}_nnt"] = f"{math.ceil(1 / rd)}"
        if lo <= 0:
            res[f"{prefix}_nnt_ci"] = "--"
        else:
            res[f"{prefix}_nnt_ci"] = f"[{math.ceil(1 / hi)}, {math.ceil(1 / lo)}]"

    add_outcome("gad_case", "gad_case_w1", "gad_case_elig", show_ci=False)
    add_outcome("gad_resp", "gad_resp_w4", "gad_resp_elig")
    rd_sub10, ci_sub10 = add_outcome("gad_sub10", "gad_sub10_w4", "gad_sub10_elig")
    add_nnt("gad_sub10", rd_sub10, ci_sub10)
    add_outcome("gad_remit", "gad_remit_w4", "gad_remit_elig")

    add_outcome("phq_case", "phq_case_w2", "phq_case_elig")
    add_outcome("phq_remit", "phq_remit_w4", "phq_improvement_elig")
    add_outcome("phq_resp", "phq_resp_w4", "phq_improvement_elig")
    rd_phq_sub10, ci_phq_sub10 = add_outcome(
        "phq_sub10", "phq_sub10_w4", "phq_improvement_elig"
    )
    add_nnt("phq_sub10", rd_phq_sub10, ci_phq_sub10)

    return res
