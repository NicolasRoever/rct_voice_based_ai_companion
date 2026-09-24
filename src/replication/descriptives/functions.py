"""Baseline balance and participant flow."""

import pandas as pd
from scipy.stats import ttest_ind


def calculate_balance(df):
    d = df.copy().assign(
        female=df.gender_w1.eq("female").astype(int),
        meds=df.medication_w2.ne("I have never taken medication").astype(int),
        therapy=df.therapy_history_w1.ne("never").astype(int),
        employed=df.employment_w2.isin(
            ["Working full-time", "Working part-time"]
        ).astype(int),
    )
    specs = [
        ("age", "age_w1", 1),
        ("gad7", "gad7_score_w1", 1),
        ("phq8", "phq8_score_w2", 1),
        ("lonely", "ucla_loneliness_w2", 1),
        ("income", "income_w2", 1),
        ("female", "female", 100),
        ("employed", "employed", 100),
        ("meds", "meds", 100),
        ("therapy", "therapy", 100),
    ]
    values = {
        "n_treat": int(d.sonia_treatment.eq(1).sum()),
        "n_control": int(d.sonia_treatment.eq(0).sum()),
        "p_n": "-",
    }
    rows = []
    for key, column, scale in specs:
        treatment = d.loc[d.sonia_treatment.eq(1), column].dropna()
        control = d.loc[d.sonia_treatment.eq(0), column].dropna()
        p = float(ttest_ind(treatment, control, equal_var=False).pvalue)
        values[f"p_{key}"] = round(p, 2)
        for arm, data in [("treat", treatment), ("control", control)]:
            mean = float(data.mean()) * scale
            values[f"{key}_{arm}"] = (
                f"{round(mean):,}"
                if key == "income"
                else round(mean)
                if scale == 100
                else round(mean, 1)
            )
            rows.append(
                {
                    "variable": key,
                    "arm": arm,
                    "n": len(data),
                    "mean_or_percent": mean,
                    "welch_p_value": p,
                }
            )
    return values, pd.DataFrame(rows)


def calculate_flow(screening, sample):
    values = {
        "wave1_total": f"{len(screening):,}",
        "call_scheduled": f"{int(screening.cal_scheduled.sum()):,}",
        "attrition_wave_4_n": int(sample.gad7_score_w4.isna().sum()),
        "attrition_wave_4_perc": round(
            float(sample.gad7_score_w4.isna().mean() * 100), 2
        ),
    }
    counts = {
        "screened": len(screening),
        "phone_invited": int(screening.phone_screener_accepted_w1.sum()),
        "phone_scheduled": int(screening.cal_scheduled.sum()),
        "randomized": len(sample),
    }
    for name, arm in [("treatment", 1), ("control", 0)]:
        group = sample.loc[sample.sonia_treatment.eq(arm)]
        counts[f"{name}_allocated"] = len(group)
        counts[f"{name}_signed_up"] = int(group.signed_up_in_app.sum())
        counts[f"{name}_followup"] = int(group.gad7_score_w4.notna().sum())
    return values, counts


def calculate_screening_summary(screening):
    fail_conditions = {
        "Age < 18": screening.age_w1.lt(18),
        "High AI Privacy Concern": screening.ai_privacy_level_w1.ge(4),
        "Low AI Comfort": screening.ai_emotional_comfort_w1.lt(50),
        "Currently in Therapy": screening.therapy_history_w1.str.lower().eq(
            "currently"
        ),
        "GAD-7 Not in 13–20": ~screening.gad7_score_w1.between(13, 20),
        "Not iPhone User": screening.device_type_w1.str.lower().ne("iphone"),
        "Not US Resident": screening.us_resident_w1.ne(True),
    }
    return {
        "screened": len(screening),
        "phone_invited": int(screening.phone_screener_accepted_w1.sum()),
        "phone_scheduled": int(screening.cal_scheduled.sum()),
        "exclusions": {
            label: int(condition.sum()) for label, condition in fail_conditions.items()
        },
        "gad7_distribution": [
            {"score": int(score), "count": int(count)}
            for score, count in screening.gad7_score_w1.value_counts()
            .sort_index()
            .items()
        ],
    }
