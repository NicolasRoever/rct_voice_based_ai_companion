import pandas as pd

from replication.config import CLEAN_DATA, RESULTS, SCREENING_DATA, SRC
from replication.descriptives.functions import (
    calculate_balance,
    calculate_flow,
    calculate_screening_summary,
)
from replication.helper import write_csv, write_json


def task_descriptives(
    depends_on={
        "sample": CLEAN_DATA,
        "screening": SCREENING_DATA,
        "code": SRC / "descriptives/functions.py",
        "helper": SRC / "helper.py",
    },
    produces={
        "balance": RESULTS / "balance.json",
        "balance_full": RESULTS / "balance.csv",
        "flow": RESULTS / "flow.json",
        "counts": RESULTS / "flow_counts.json",
        "screening": RESULTS / "screening.json",
    },
):
    df = pd.read_csv(depends_on["sample"], low_memory=False)
    screening = pd.read_csv(depends_on["screening"], low_memory=False)
    balance, detail = calculate_balance(df)
    flow, counts = calculate_flow(screening, df)
    write_json(produces["balance"], balance)
    write_csv(produces["balance_full"], detail)
    write_json(produces["flow"], flow)
    write_json(produces["counts"], counts)
    write_json(produces["screening"], calculate_screening_summary(screening))
