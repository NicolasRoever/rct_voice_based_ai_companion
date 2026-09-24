"""Paths are relative to this package; tasks pass them into functions."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "replication"
DATA = ROOT / "data"
BLD = ROOT / "bld"
RAW_DATA = DATA / "participants.csv"
CLEAN_DATA = BLD / "clean_data" / "participants.csv"
SCREENING_DATA = DATA / "screening.csv"
RESULTS = BLD / "results"
FIGURES = BLD / "figures"
TABLES = BLD / "tables"
TEMPLATES = SRC / "reporting" / "templates"
VALIDATION = ROOT / "validation"
FIGURE_NAMES = (
    "consort_diagram_w124",
    "gad7_baseline_vs_w4_scatter_treatment",
    "gad7_baseline_vs_w4_scatter_control",
    "phq8_baseline_vs_w4_scatter_treatment",
    "phq8_baseline_vs_w4_scatter_control",
    "metaanalysis_digital_anxiety",
    "metaanalysis_digital_depression",
)

TABLE_TEMPLATES = {
    "Table 1": "main_results_psych.tex",
    "Table 2": "clinical_outcomes_main.tex",
    "Table A1": "balance_table_rct.tex",
}
SUPPLIED_FIGURES = (
    "ad.png",
    "personalize_noblack.png",
    "privacy_noblack.PNG",
    "sonia_architecture_corrected.png",
)
