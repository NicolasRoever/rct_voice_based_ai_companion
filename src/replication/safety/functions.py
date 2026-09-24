"""Self-reported perceived safety and symptom worsening."""

import pandas as pd
from statsmodels.stats.proportion import proportions_ztest


def calculate_safety(df, categories, threshold=4):
    treated = df.loc[df.sonia_treatment.eq(1)]
    ratings = treated.sonia_safe_w4.dropna()
    concerns = int(ratings.eq(0).sum())
    no_concerns = int(ratings.eq(1).sum())
    if categories.category.duplicated().any() or categories["count"].lt(0).any():
        raise ValueError("Safety categories must be unique with nonnegative counts.")
    if categories["count"].sum() != concerns:
        raise ValueError("Safety category counts must equal respondents with concerns.")
    values = {
        "number_no_concerns_w4": no_concerns,
        "number_concerns_w4": concerns,
        "fraction_no_concerns_w4": round(no_concerns / len(ratings) * 100),
        "fraction_concerns_w4": round(concerns / len(ratings) * 100),
    }
    values.update(
        {
            f"concerns_{category}": int(n)
            for category, n in categories.set_index("category")["count"].items()
        }
    )
    rows = []
    for scale, baseline in [("gad7", "gad7_score_w1"), ("phq8", "phq8_score_w2")]:
        counts, sizes = [], []
        for arm, name in [(1, "ai"), (0, "control")]:
            pair = df.loc[
                df.sonia_treatment.eq(arm), [baseline, f"{scale}_score_w4"]
            ].dropna()
            change = pair.iloc[:, 1] - pair.iloc[:, 0]
            n, worse, any_worse = (
                len(pair),
                int(change.ge(threshold).sum()),
                int(change.gt(0).sum()),
            )
            counts.append(worse)
            sizes.append(n)
            values[f"pct_worse_{scale}_{name}"] = round(100 * worse / n, 1)
            values[f"pct_any_worse_{scale}_{name}"] = round(100 * any_worse / n, 1)
            rows.append(
                {
                    "scale": scale,
                    "arm": name,
                    "n": n,
                    "any_worse": any_worse,
                    "deteriorated": worse,
                }
            )
        statistic, p = proportions_ztest(
            count=counts, nobs=sizes, alternative="two-sided"
        )
        values[f"pval_worse_{scale}"] = round(float(p), 2)
        for row in rows[-2:]:
            row.update(z_statistic=float(statistic), p_value=float(p))
    return values, pd.DataFrame(rows)
