import pandas as pd

from replication.benchmarking.functions import prepare_benchmarks
from replication.config import CLEAN_DATA, DATA, RESULTS, SRC
from replication.helper import write_csv


def task_benchmarks(
    depends_on={
        "published": DATA / "published_benchmarks.csv",
        "coefficients": RESULTS / "coefficients.csv",
        "data": CLEAN_DATA,
        "code": [SRC / "benchmarking/functions.py", SRC / "benchmarking/plots.py"],
        "helper": SRC / "helper.py",
    },
    produces=RESULTS / "benchmarks.csv",
):
    output = prepare_benchmarks(
        pd.read_csv(depends_on["published"]),
        pd.read_csv(depends_on["coefficients"]),
        len(pd.read_csv(depends_on["data"], low_memory=False)),
    )
    write_csv(produces, output)
