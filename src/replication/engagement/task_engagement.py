import pandas as pd

from replication.config import CLEAN_DATA, RESULTS, SRC
from replication.engagement.functions import calculate_engagement
from replication.helper import write_csv, write_json


def task_engagement(
    depends_on={
        "data": CLEAN_DATA,
        "code": SRC / "engagement/functions.py",
        "helper": SRC / "helper.py",
    },
    produces={
        "values": RESULTS / "engagement.json",
        "detail": RESULTS / "engagement.csv",
    },
):
    values, detail = calculate_engagement(
        pd.read_csv(depends_on["data"], low_memory=False)
    )
    write_json(produces["values"], values)
    write_csv(produces["detail"], detail)
