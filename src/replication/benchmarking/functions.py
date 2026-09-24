"""Published benchmarks are fixed inputs; the present trial is re-estimated."""

import pandas as pd

from replication.benchmarking.plots import make_row


def prepare_benchmarks(published, coefficients, sample_size):
    rows = []
    for row in published.to_dict("records"):
        cohort = row.pop("cohort")
        row = {key: None if pd.isna(value) else value for key, value in row.items()}
        row["year"], row["sample_n"] = int(row["year"]), int(row["sample_n"])
        rows.append({"cohort": cohort, **make_row(**row)})
    for cohort, outcome, name in [
        ("anxiety", "GAD-7", "gad7_std"),
        ("depression", "PHQ-8", "phq8_std"),
    ]:
        effect = coefficients.loc[
            (coefficients.model == name) & (coefficients.term == "sonia_treatment")
        ].iloc[0]
        rows.append(
            {
                "cohort": cohort,
                **make_row(
                    "This Study",
                    2026,
                    sample_size,
                    outcome,
                    "RCT",
                    # Display magnitudes favouring treatment, at manuscript precision.
                    g=round(-effect.estimate, 2),
                    ci_low=round(-effect.ci_upper, 2),
                    ci_high=round(-effect.ci_lower, 2),
                    note="Sonia voice-based AI CBT",
                ),
            }
        )
    return pd.DataFrame(rows)
