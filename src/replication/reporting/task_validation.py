import hashlib
import json

import numpy as np
import pandas as pd

from replication.config import (
    CLEAN_DATA,
    DATA,
    FIGURE_NAMES,
    FIGURES,
    RAW_DATA,
    RESULTS,
    ROOT,
    SRC,
    SUPPLIED_FIGURES,
    TABLE_TEMPLATES,
    TABLES,
    TEMPLATES,
    VALIDATION,
)
from replication.helper import write_csv, write_json
from replication.reporting.functions import (
    compare_reported_values,
    rendered_tables_match,
    significance_markers,
    table_numbers,
)


def task_validate_replication(
    depends_on={
        "values": RESULTS / "key_numbers.json",
        "expected": VALIDATION / "expected_values.json",
        "expected_screening": VALIDATION / "expected_screening.json",
        "screening": RESULTS / "screening.json",
        "input": RAW_DATA,
        "checksums": VALIDATION / "input_checksums.json",
        "templates": {
            label: TEMPLATES / name for label, name in TABLE_TEMPLATES.items()
        },
        "data_inputs": [
            DATA / name
            for name in (
                "data_dictionary.csv",
                "screening.csv",
                "published_benchmarks.csv",
                "safety_concern_categories.csv",
            )
        ],
        "supplied_inputs": {
            **{name: DATA / "illustrations" / name for name in SUPPLIED_FIGURES},
            "study_comparison.tex": DATA / "study_comparison.tex",
        },
        "supplied_outputs": {
            **{name: FIGURES / name for name in SUPPLIED_FIGURES},
            "study_comparison.tex": TABLES / "study_comparison.tex",
        },
        "source_verification": VALIDATION / "source_verification.json",
        "provenance": VALIDATION / "input_provenance.json",
        "data": CLEAN_DATA,
        "expected_coefficients": VALIDATION / "expected_coefficients.csv",
        "coefficients": RESULTS / "coefficients.csv",
        "figures": [FIGURES / f"{name}.pdf" for name in FIGURE_NAMES],
        "original_robustness": VALIDATION / "effect_robustness_wave_4.tex",
        "robustness": TABLES / "effect_robustness_wave_4.tex",
        "tables": {label: TABLES / name for label, name in TABLE_TEMPLATES.items()},
        "code": SRC / "reporting/functions.py",
        "helper": SRC / "helper.py",
    },
    produces={
        "comparison": RESULTS / "key_numbers_comparison.csv",
        "summary": RESULTS / "validation.json",
    },
):
    values = json.loads(depends_on["values"].read_text(encoding="utf-8"))
    expected = json.loads(depends_on["expected"].read_text(encoding="utf-8"))
    comparison = compare_reported_values(values, expected)
    write_csv(produces["comparison"], comparison)
    provenance = json.loads(depends_on["provenance"].read_text(encoding="utf-8"))
    data = pd.read_csv(depends_on["data"], low_memory=False)
    expected_models = pd.read_csv(depends_on["expected_coefficients"]).set_index(
        ["model", "term"]
    )
    models = pd.read_csv(depends_on["coefficients"]).set_index(["model", "term"])
    checksums = json.loads(depends_on["checksums"].read_text(encoding="utf-8"))
    original_robustness = depends_on["original_robustness"].read_text(encoding="utf-8")
    robustness = depends_on["robustness"].read_text(encoding="utf-8")
    checks = {
        "public_data_match_original_anonymization_task": all(
            hashlib.sha256((DATA / name).read_bytes()).hexdigest() == digest
            for name, digest in provenance["files"].items()
        ),
        "screening_distribution_and_flow_match": json.loads(
            depends_on["screening"].read_text(encoding="utf-8")
        )
        == json.loads(depends_on["expected_screening"].read_text(encoding="utf-8")),
        "all_input_checksums_match": all(
            hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
            for name, digest in checksums.items()
        ),
        "rendered_tables_match_reported_values": rendered_tables_match(
            {
                name: path.read_text(encoding="utf-8")
                for name, path in depends_on["tables"].items()
            },
            {
                name: path.read_text(encoding="utf-8")
                for name, path in depends_on["templates"].items()
            },
            expected,
        ),
        "supplied_exhibits_copied_unchanged": all(
            path.read_bytes() == depends_on["supplied_inputs"][name].read_bytes()
            for name, path in depends_on["supplied_outputs"].items()
        ),
        "robustness_significance_stars_match": significance_markers(original_robustness)
        == significance_markers(robustness),
        "input_checksum": hashlib.sha256(depends_on["input"].read_bytes()).hexdigest()
        == provenance["participant_file_sha256"],
        "randomized_400": len(data) == 400,
        "allocated_200_each": data.sonia_treatment.value_counts().to_dict()
        == {1: 200, 0: 200},
        "followup_193_treatment_197_control": data.groupby("sonia_treatment")
        .gad7_score_w4.count()
        .to_dict()
        == {0: 197, 1: 193},
        "all_reported_values_match": bool(comparison.matches.all()),
        "main_models_match_original_coefficients": bool(
            np.allclose(
                models.loc[expected_models.index].to_numpy(),
                expected_models.to_numpy(),
                atol=1e-10,
                rtol=1e-8,
            )
        ),
        "all_seven_figures_created": all(
            path.read_bytes().startswith(b"%PDF-") for path in depends_on["figures"]
        ),
        "robustness_table_numbers_match": table_numbers(original_robustness)
        == table_numbers(robustness),
        "safety_categories_match": all(
            values.get(f"concerns_{key}") == n
            for key, n in {
                "privacy": 2,
                "uncertainty": 2,
                "insufficient_knowledge": 1,
            }.items()
        ),
    }
    write_json(
        produces["summary"],
        {
            "checks": checks,
            "reported_values_checked": len(comparison),
            "passed": all(checks.values()),
        },
    )
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(
            f"Replication checks failed: {failed}. See {produces['comparison']}."
        )
