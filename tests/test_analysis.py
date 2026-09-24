"""Checks for the denominator, scoring and time-window rules that affect results."""

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from replication.analysis_wave_4.power import calculate_preregistered_power
from replication.analysis_wave_4.tables import _risk_diff_ci, compute_clinical_outcomes
from replication.config import DATA, RAW_DATA, SCREENING_DATA
from replication.data_cleaning.functions import (
    clean_replication_data,
    score_items,
    standardize,
)
from replication.engagement.functions import usage_in_window
from replication.helper import inject_values
from replication.reporting.functions import combine_values


def test_scoring_preserves_missing_and_partial_responses():
    raw = pd.DataFrame(
        {
            "a": [None, "Several days", "Not at all"],
            "b": [None, None, "Nearly every day"],
        }
    )
    result = score_items(
        raw, ["a", "b"], {"Not at all": 0, "Several days": 1, "Nearly every day": 3}
    )
    assert np.isnan(result.iloc[0])
    assert result.iloc[1:].tolist() == [1, 3]
    with pytest.raises(ValueError, match="Unexpected"):
        score_items(pd.DataFrame({"a": ["invalid"]}), ["a"], {"Not at all": 0})


def test_phq_improvement_uses_baseline_caseness_and_observed_followup():
    raw = pd.DataFrame(
        {
            "research_arm": ["sonia"] * 3 + ["webapp"] * 3,
            "gad7_score_w1": [15] * 6,
            "gad7_score_w4": [7, 7, None, 8, 8, None],
            "phq8_score_w2": [12, 8, 12, 12, 8, 12],
            "phq8_score_w4": [4, 0, None, 8, 0, None],
        }
    )
    values = compute_clinical_outcomes(raw)
    assert values["phq_remit_trt"] == r"100.0\% (1/1)"
    assert values["phq_remit_ctrl"] == r"0.0\% (0/1)"
    assert values["phq_case_trt"] == r"66.7\% (2/3)"


def test_newcombe_interval_reverses_with_arm_order():
    difference, interval = _risk_diff_ci(122, 62, 193, 197)
    reverse, reverse_interval = _risk_diff_ci(62, 122, 197, 193)
    assert difference == pytest.approx(122 / 193 - 62 / 197)
    assert reverse == pytest.approx(-difference)
    assert reverse_interval == pytest.approx((-interval[1], -interval[0]))
    assert 0 < interval[0] < difference < interval[1]


def test_usage_windows_include_boundary_days_and_nonusers():
    data = pd.DataFrame({f"duration_day_{day}": [0, 0] for day in range(-2, 15)})
    for day, value in [(-2, 100), (-1, 1), (6, 2), (7, 4), (13, 8), (14, 16)]:
        data.loc[0, f"duration_day_{day}"] = value
    assert usage_in_window(data, "duration_", -1, 6).tolist() == [3, 0]
    assert usage_in_window(data, "duration_", 7, 13).tolist() == [12, 0]
    with pytest.raises(ValueError, match="Missing relative-day"):
        usage_in_window(data.drop(columns="duration_day_0"), "duration_", -1, 6)


def test_cleaning_scores_public_sample_without_mutating_input():
    raw = pd.read_csv(RAW_DATA, low_memory=False)
    before = raw.copy(deep=True)
    screening = pd.read_csv(SCREENING_DATA, low_memory=False)
    sample = clean_replication_data(raw, screening)
    assert_frame_equal(raw, before)
    assert len(screening) == 10490 and len(sample) == 400
    assert sample.gad7_score_w4.notna().sum() == 390
    assert (
        sample.gad7_score_std_w1.std() < 0.5
    )  # SD reference is the full screener, not the selected sample.
    assert sample.phq8_score_std_w2.std() == pytest.approx(1)
    assert sample.phq8_score_std_w2.mean() == pytest.approx(0, abs=1e-12)


def test_standardization_uses_supplied_reference_sample_sd():
    assert standardize(pd.Series([3.0]), pd.Series([1.0, 3.0, 5.0])).iloc[0] == 0
    assert standardize(pd.Series([5.0]), pd.Series([1.0, 3.0, 5.0])).iloc[0] == 1


def test_power_matches_prospective_claims():
    values = calculate_preregistered_power()
    assert values["prereg_n_complete_total"] == 380
    assert 0.83 < values["prereg_power_ttest_proportion"] < 0.84
    assert 0.88 < values["prereg_power_ancova_proportion"] < 0.90


def test_missing_or_conflicting_table_values_fail(tmp_path):
    path = tmp_path / "example.tex"
    path.write_text(r"\roever{effect}{} and \roever{percentage}{}", encoding="utf-8")
    with pytest.raises(KeyError, match="Missing"):
        inject_values(path, effect="-0.63")
    inject_values(path, effect="-0.63", percentage=r"63.2\% (122/193)")
    assert path.read_text(encoding="utf-8") == r"-0.63 and 63.2\% (122/193)"
    with pytest.raises(ValueError, match="Conflicting"):
        combine_values([{"effect": 1}, {"effect": 2}])


def test_rendered_validation_catches_missing_duplicate_and_wrong_values():
    from replication.reporting.functions import rendered_tables_match

    expected = [{"source": "Table 1", "key": "effect", "value": "-0.63"}]
    templates = {"Table 1": r"\roever{effect}{}"}
    assert rendered_tables_match({"Table 1": "-0.63"}, templates, expected)
    for invalid in ["", "-0.63-0.63", "0.63", r"\roever{effect}{}"]:
        assert not rendered_tables_match({"Table 1": invalid}, templates, expected)
    assert not rendered_tables_match({}, templates, expected)


def test_table_injection_preserves_unicode(tmp_path):
    path = tmp_path / "unicode.tex"
    path.write_bytes("Röver: ≥10; \\roever{n}{}".encode("utf-8"))
    inject_values(path, n=400)
    assert path.read_bytes() == "Röver: ≥10; 400".encode("utf-8")


def test_safety_categories_must_match_reported_concerns():
    from replication.safety.functions import calculate_safety

    sample = pd.DataFrame({"sonia_treatment": [1], "sonia_safe_w4": [0]})
    duplicate = pd.DataFrame({"category": ["privacy", "privacy"], "count": [1, 1]})
    with pytest.raises(ValueError, match="unique"):
        calculate_safety(sample, duplicate)
    wrong_count = pd.DataFrame({"category": ["privacy"], "count": [2]})
    with pytest.raises(ValueError, match="equal respondents"):
        calculate_safety(sample, wrong_count)


def test_public_data_are_documented_and_safety_counts_are_unlinked():
    import re

    participants = pd.read_csv(RAW_DATA, low_memory=False)
    dictionary = pd.read_csv(DATA / "data_dictionary.csv")
    documented = dictionary.loc[dictionary.file.eq("participants.csv"), "variable"]
    assert set(participants.columns) == set(documented)
    assert len(participants) == 400
    assert participants.replication_id.is_unique
    assert not any(
        re.search(
            r"timestamp|created_at|StartDate|Page_Submit|safety_events|research_identifier|email|phone",
            c,
            re.I,
        )
        for c in participants
    )
    assert not any(
        re.search(r"20\d{2}-\d{2}-\d{2}|\b1[0-9]{9}\b", str(v))
        for v in participants.to_numpy().ravel()
    )
    for filename in [
        "safety_concern_categories.csv",
        "screening.csv",
    ]:
        assert "replication_id" not in pd.read_csv(DATA / filename).columns


def test_screener_item_totals_are_checked():
    raw = pd.read_csv(RAW_DATA, low_memory=False)
    screening = pd.read_csv(SCREENING_DATA, low_memory=False)
    screening.loc[0, "gad7_score_w1"] += 1
    with pytest.raises(ValueError, match="items disagree"):
        clean_replication_data(raw, screening)


def test_all_screeners_are_retained_without_identifiers_or_dates():
    screening = pd.read_csv(SCREENING_DATA, low_memory=False)
    dictionary = pd.read_csv(DATA / "data_dictionary.csv")
    expected = set(dictionary.loc[dictionary.file.eq("screening.csv"), "variable"])
    assert len(screening) == 10490
    assert set(screening.columns) == expected
    assert not any(
        "timestamp" in column or "created_at" in column or column.endswith("_id")
        for column in screening
    )
