"""
The following src collects metrics on the individual queries for both a transitive and
direct technique.
"""
import os

from api.constants.processing import (
    DATASET_COLUMN_ORDER,
    LAG_COLNAME,
    METRIC_COLNAME,
    QUERY_INDEX_COLNAME,
)
from api.tables.metric_table import MetricTable, Metrics
from api.tracer import Tracer
from experiments.constants import PATH_TO_DATA


def path_to_str(path_tuple):
    return "%s->%s->%s" % (path_tuple[0], path_tuple[1], path_tuple[2])


class HierarchyEntry:
    def __init__(
        self, dataset: str, p: str, metric: str, direct: float, transitive: float
    ):
        self.dataset = dataset
        self.path = p
        self.metric = metric
        self.direct = direct
        self.transitive = transitive
        self.delta = transitive - direct


def create_entries(dataset: str, p: str, d_metrics: [Metrics], t_metrics: [Metrics]):
    entries = []
    for d, t in zip(d_metrics, t_metrics):
        entries = entries + create_entries_for_metrics(dataset, p, d, t)
    return entries


def create_entries_for_metrics(
    dataset: str, p: str, d_metrics: Metrics, t_metrics: Metrics
):
    entries = []
    for metric in vars(d_metrics).keys():
        entry = HierarchyEntry(
            dataset=dataset,
            p=p,
            metric=metric,
            direct=getattr(d_metrics, metric),
            transitive=getattr(t_metrics, metric),
        )
        entries.append(entry)
    return entries


if __name__ == "__main__":
    transitive_technique_template = (
        "(x (MAX INDEPENDENT) ((. (VSM NT) (%s %s)) (. (VSM NT) (%s %s))))"
    )
    direct_technique_template = "(. (VSM NT) (%s %s))"

    EXPORT_PATH = os.path.join(
        PATH_TO_DATA, "processed", "hierarchy", "hierarchy_experiment_results.csv"
    )
    possible_paths = [(0, 1, 2), (1, 0, 2), (2, 1, 0)]
    tracer = Tracer()

    metric_table = MetricTable()
    index_col_name = "query_index"
    for dataset_name in DATASET_COLUMN_ORDER:
        for path in possible_paths:
            p_name = path_to_str(path)
            # transitive
            transitive_technique_def = transitive_technique_template % (
                path[0],
                path[1],
                path[1],
                path[2],
            )
            transitive_metrics = tracer.get_metrics(
                dataset_name, transitive_technique_def, summary_metrics=False
            )
            metric_table.add(
                transitive_metrics,
                {"dataset": dataset_name, "path": p_name, "type": "transitive"},
                create_index=True,
                index_name=index_col_name,
            )

            # direct
            direct_technique_def = direct_technique_template % (path[0], path[2])
            direct_metrics = tracer.get_metrics(
                dataset_name, direct_technique_def, summary_metrics=False
            )
            metric_table.add(
                direct_metrics,
                {"dataset": dataset_name, "path": p_name, "type": "direct"},
                create_index=True,
                index_name=index_col_name,
            )

            # delta
            delta_metrics = list(
                map(lambda m: m[1] - m[0], zip(direct_metrics, transitive_metrics))
            )

    scaled_df = metric_table.scale_col(
        LAG_COLNAME, group_by_cols=["dataset"], inverted=True, drop_old=True
    )
    melted_df = metric_table.melt_metrics()

    cols = ["dataset", "path", "direct", "transitive", "metric", "score"]
    pivot_df = melted_df.table.pivot(
        index=["dataset", "path", "metric", index_col_name],
        columns=["type"],
        values=["score"],
    ).reset_index()

    pivot_df.columns = [
        "dataset",
        "path",
        METRIC_COLNAME,
        QUERY_INDEX_COLNAME,
        "direct",
        "transitive",
    ]
    pivot_df = pivot_df[
        ["dataset", "path", "metric", "query_index", "transitive", "direct"]
    ]
    pivot_df["delta"] = pivot_df["transitive"] - pivot_df["direct"]
    print(pivot_df.head())
    pivot_df.to_csv(EXPORT_PATH, index=False)
