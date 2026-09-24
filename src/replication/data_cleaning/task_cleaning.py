import pandas as pd

from replication.config import CLEAN_DATA, RAW_DATA, SCREENING_DATA, SRC
from replication.data_cleaning.functions import clean_replication_data
from replication.helper import write_csv


def task_clean_data(
    depends_on={
        "data": RAW_DATA,
        "screening": SCREENING_DATA,
        "code": SRC / "data_cleaning/functions.py",
        "helper": SRC / "helper.py",
    },
    produces=CLEAN_DATA,
):
    sample = clean_replication_data(
        pd.read_csv(depends_on["data"], low_memory=False),
        pd.read_csv(depends_on["screening"], low_memory=False),
    )
    write_csv(produces, sample)
