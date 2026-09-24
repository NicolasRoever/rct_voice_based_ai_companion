"""Calendar-day usage windows; nonusers contribute zero to arm summaries."""

import pandas as pd


def usage_in_window(df, prefix, lower, upper):
    columns = [f"{prefix}day_{day}" for day in range(lower, upper + 1)]
    missing = set(columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing relative-day usage columns: {sorted(missing)}")
    return df[columns].sum(axis=1)


def calculate_engagement(df):
    values, rows = {}, []
    for week, bounds in [(1, (-1, 6)), (2, (7, 13))]:
        for arm, prefix, name, divisor in [
            (1, "number_sessions_", "sessions", 1),
            (1, "duration_", "minutes_sonia", 60),
            (0, "webapp_sessions_", "visits_webapp", 1),
            (0, "webapp_seconds_", "minutes_webapp", 60),
        ]:
            group = df.loc[df.sonia_treatment.eq(arm)]
            observations = usage_in_window(group, prefix, *bounds) / divisor
            values[f"median_{name}_w{week}"] = round(float(observations.median()), 1)
            values[f"sd_{name}_w{week}"] = round(float(observations.std(ddof=1)), 1)
            rows.append(
                {
                    "week": week,
                    "metric": name,
                    "n": len(observations),
                    "lower_day": bounds[0],
                    "upper_day": bounds[1],
                    "median": observations.median(),
                    "sd": observations.std(ddof=1),
                }
            )
    return values, pd.DataFrame(rows)
