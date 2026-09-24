"""Small I/O helpers shared by the tasks."""

import json
import re

import pandas as pd


def write_json(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(values, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def write_csv(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False)


def render_values(text, values):
    """Replace each table placeholder with its calculated value."""
    pattern = re.compile(r"\\roever\{(\w+)\}\{[^}]*\}")
    missing = {m[1] for m in pattern.finditer(text)} - values.keys()
    if missing:
        raise KeyError(f"Missing table values: {sorted(missing)}")
    return pattern.sub(lambda m: str(values[m[1]]), text)


def inject_values(tex_path, **values):
    """Fill a table file; outputs contain ordinary LaTeX without custom placeholders."""
    tex_path.write_text(
        render_values(tex_path.read_text(encoding="utf-8"), values), encoding="utf-8"
    )


def fix_pandas_append_error():
    """Compatibility for pystout 0.0.8 with pandas >= 2."""
    if not hasattr(pd.DataFrame, "append"):

        def append(self, other, ignore_index=False, sort=False):
            return pd.concat([self, other], ignore_index=ignore_index, sort=sort)

        pd.DataFrame.append = append
