import pandas as pd

from replication.config import CLEAN_DATA, DATA, RESULTS, SRC
from replication.helper import write_csv, write_json
from replication.safety.functions import calculate_safety


def task_safety(
    depends_on={
        "data": CLEAN_DATA,
        "categories": DATA / "safety_concern_categories.csv",
        "code": SRC / "safety/functions.py",
        "helper": SRC / "helper.py",
    },
    produces={
        "values": RESULTS / "safety.json",
        "detail": RESULTS / "deterioration.csv",
    },
):
    values, detail = calculate_safety(
        pd.read_csv(depends_on["data"], low_memory=False),
        pd.read_csv(depends_on["categories"]),
    )
    write_json(produces["values"], values)
    write_csv(produces["detail"], detail)
