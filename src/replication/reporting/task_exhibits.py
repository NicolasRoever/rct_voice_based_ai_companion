import json
import shutil

import pandas as pd

from replication.config import (
    DATA,
    FIGURES,
    RESULTS,
    SRC,
    SUPPLIED_FIGURES,
    TABLE_TEMPLATES,
    TABLES,
    TEMPLATES,
)
from replication.helper import inject_values, write_csv, write_json
from replication.reporting.functions import combine_values


def task_collect_key_numbers(
    depends_on={
        "results": [
            RESULTS / f"{name}.json"
            for name in (
                "main_results",
                "clinical_outcomes",
                "balance",
                "flow",
                "engagement",
                "safety",
                "power",
            )
        ],
        "code": SRC / "reporting/functions.py",
        "helper": SRC / "helper.py",
    },
    produces={
        "json": RESULTS / "key_numbers.json",
        "csv": RESULTS / "key_numbers.csv",
    },
):
    values = combine_values(
        [json.loads(path.read_text(encoding="utf-8")) for path in depends_on["results"]]
    )
    write_json(produces["json"], values)
    write_csv(
        produces["csv"], pd.DataFrame(sorted(values.items()), columns=["key", "value"])
    )


def task_tables(
    depends_on={
        "values": RESULTS / "key_numbers.json",
        "helper": SRC / "helper.py",
        "templates": {
            label: TEMPLATES / name for label, name in TABLE_TEMPLATES.items()
        },
    },
    produces={label: TABLES / name for label, name in TABLE_TEMPLATES.items()},
):
    values = json.loads(depends_on["values"].read_text(encoding="utf-8"))
    for label, source in depends_on["templates"].items():
        produces[label].parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, produces[label])
        inject_values(produces[label], **values)


def task_supplied_exhibits(
    depends_on={
        **{name: DATA / "illustrations" / name for name in SUPPLIED_FIGURES},
        "study_comparison.tex": DATA / "study_comparison.tex",
    },
    produces={
        **{name: FIGURES / name for name in SUPPLIED_FIGURES},
        "study_comparison.tex": TABLES / "study_comparison.tex",
    },
):
    for name, source in depends_on.items():
        produces[name].parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, produces[name])
