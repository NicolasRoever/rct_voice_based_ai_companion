"""Score the public trial sample using the full screener score distribution."""

import json
import re

import numpy as np
import pandas as pd


def score_items(df, columns, mapping):
    """Match original scoring: sum observed items; entirely missing stays missing."""
    numeric = df[columns].apply(lambda col: col.map(mapping))
    unknown = df[columns].notna() & numeric.isna()
    if unknown.any().any():
        raise ValueError("Unexpected questionnaire response category.")
    return numeric.sum(axis=1, min_count=1)


def income_midpoint(value):
    """Use interval midpoints; the open upper category is missing, as originally."""
    if pd.isna(value):
        return np.nan
    amounts = [int(n.replace(",", "")) for n in re.findall(r"\$([\d,]+)", value)]
    if value.startswith("Less than") and amounts:
        return amounts[0] / 2
    if value.startswith("Between") and len(amounts) == 2:
        return sum(amounts) / 2
    return np.nan


def standardize(values, reference):
    return (values - reference.mean()) / reference.std(ddof=1)


def clean_replication_data(raw, screening):
    """Return the cleaned randomized sample, without changing either input."""
    if raw.replication_id.isna().any() or raw.replication_id.duplicated().any():
        raise ValueError("Replication IDs must be unique and nonmissing.")
    df = raw.copy()
    response_map = {
        "Not at all": 0,
        "Several days": 1,
        "More than half the days": 2,
        "Nearly every day": 3,
    }
    df["phq8_score_w2"] = score_items(
        df, [f"phq_8_{i}_w2" for i in range(1, 9)], response_map
    )
    df["gad7_score_w4"] = score_items(
        df, [f"Q1_{i}_w4" for i in range(1, 8)], response_map
    )
    df["phq8_score_w4"] = score_items(
        df, [f"Q3_{i}_w4" for i in range(1, 9)], response_map
    )
    df["ucla_loneliness_w2"] = score_items(
        df,
        [f"ucla_lonely_{i}_w2" for i in range(1, 4)],
        {"Hardly ever": 1, "Some of the time": 2, "Often": 3},
    )
    for responses in (df, screening):
        scores = responses.gad7_answers_w1.map(lambda x: sum(json.loads(x)))
        if not np.allclose(scores, responses.gad7_score_w1):
            raise ValueError("Screening GAD-7 items disagree with recorded totals.")
    for wave in (1, 4):
        df[f"gad7_score_std_w{wave}"] = standardize(
            df[f"gad7_score_w{wave}"], screening.gad7_score_w1
        )
    df["signed_up_in_app"] = df.signed_up
    df["income_w2"] = df.income__w2.map(income_midpoint)
    df["employment_w2"] = df.employment__w2
    df["efficacy_human_therapy_w2"] = df.efficacy_human_thera_1_w2
    df["wtp_human_therapy_rel_w2"] = df.wtp_human_therapy_1_w2 / df.income_w2
    df["ever_med_w2"] = df.medication_w2.isin(
        [
            "I have taken medication in the past, but not currently",
            "I am currently taking medication, please tell us which:",
        ]
    ).astype(int)
    df["sonia_safe_w4"] = df.safety_sonia_binary_w4.map({"Yes": 1, "No": 0})
    sample = df
    assignment = sample.research_arm.map({"sonia": 1, "webapp": 0})
    if assignment.isna().any() or not assignment.eq(sample.sonia_treatment).all():
        raise ValueError("Treatment assignment disagrees with the export.")
    for wave in (2, 4):
        sample[f"phq8_score_std_w{wave}"] = standardize(
            sample[f"phq8_score_w{wave}"], sample.phq8_score_w2
        )
    return sample
