"""Assemble key numbers and compare exhibits with reported references."""

import re

import pandas as pd

from replication.helper import render_values


def combine_values(dictionaries):
    combined = {}
    for values in dictionaries:
        for key, value in values.items():
            if key in combined and str(combined[key]) != str(value):
                raise ValueError(f"Conflicting values for {key}")
            combined[key] = value
    return combined


def compare_reported_values(values, expected):
    rows = []
    for item in expected:
        actual = str(values.get(item["key"], "MISSING"))
        original = str(item["value"])
        try:
            matches = float(actual.replace(",", "")) == float(original.replace(",", ""))
        except ValueError:
            matches = actual == original
        rows.append({**item, "replicated": actual, "matches": matches})
    return pd.DataFrame(rows)


def table_numbers(text):
    """Extract statistical table cells, excluding row labels and TeX layout."""
    cells = []
    for line in text.splitlines():
        if "&" not in line or any(
            token in line for token in ["multicolumn", "shortstack", "cline"]
        ):
            # shortstack rows also contain coefficients; keep their cells below.
            if "shortstack" not in line:
                continue
        parts = line.split("&")[1:]
        for part in parts:
            found = re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", part)
            cells.extend(float(value) for value in found)
    return cells


def rendered_tables_match(tables, templates, expected):
    """Check complete rendered tables against their reported numerical references."""
    if tables.keys() != templates.keys():
        return False
    for label, template in templates.items():
        values = {
            row["key"]: row["value"] for row in expected if row["source"] == label
        }
        if tables[label] != render_values(template, values):
            return False
    return True


def significance_markers(text):
    """Keep significance stars in row order, excluding TeX commands and labels."""
    return re.findall(r"\\sym\{(\*+)\}", text)
