"""
The following src collects metrics on the individual queries for both a transitive and
direct technique.
"""
import os
import re
from typing import Dict

import pandas as pd

from api.constants.processing import DATASET_COLNAME, NAME_COLNAME
from api.constants.techniques import DIRECT_ID, HYBRID_ID, TRANSITIVE_ID
from api.tables.metric_table import MetricTable
from api.tables.table import Table
from api.tracer import Tracer
from experiments.meta.experiment import Experiment
from utilities.constants import DATASET_COLUMN_ORDER, PATH_TO_AGGREGATE_TABLES
from utilities.technique_extractors import (
    get_best_direct_technique,
    get_best_hybrid_technique,
    get_best_transitive_technique,
)

EXPERIMENT_NAME = "evaluate_paths"
METRIC_TABLE_EXPORT_PATH = os.path.join(
    PATH_TO_AGGREGATE_TABLES, "hierarchy_experiment_results.csv"
)
GAIN_TABLE_EXPORT_PATH = os.path.join(PATH_TO_AGGREGATE_TABLES, "hierarchy_gain.csv")

QUERY_INDEX_COLNAME = "query_index"

POSSIBLE_PATHS = [(0, 1, 2), (1, 0, 2), (0, 2, 1)]


def path_to_str(path_tuple):
    return "%s->%s->%s" % (path_tuple[0], path_tuple[1], path_tuple[2])


def path_iterator():
    for dataset_name in DATASET_COLUMN_ORDER:
        for path in POSSIBLE_PATHS:
            yield path, dataset_name


def create_template(text: str, rep: Dict[str, str]):
    # use these three lines to do the replacement
    rep = dict((re.escape(k), v) for k, v in rep.items())
    # Python 3 renamed dict.iteritems to dict.items so use rep.items() for latest versions
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], text)


class EvaluatePaths(Experiment):
    """
    Calculates metrics on all possible paths between three artifact types.
    """

    def run(self) -> Table:
        tracer = Tracer()

        def get_metrics(d_name, t_def: str):
            return tracer.get_metrics(d_name, t_def)

        def add_metrics(d_name, t_def: str, t_type: str, p_name: str):
            t_metrics = get_metrics(d_name, t_def)
            metric_table.add(
                t_metrics,
                {
                    DATASET_COLNAME: d_name,
                    "path": p_name,
                    "type": t_type,
                    NAME_COLNAME: t_def,
                },
            )

        aggregate_gain = None
        aggregate_metric = None
        for path in POSSIBLE_PATHS:
            metric_table = MetricTable()
            comparison_dict = {}
            for dataset_name in DATASET_COLUMN_ORDER:
                source_index = str(path[0])
                intermediate_index = str(path[1])
                target_index = str(path[2])

                replacement_dict = {
                    "0": source_index,
                    "1": intermediate_index,
                    "2": target_index,
                }

                path_name = path_to_str(path)

                # direct
                direct_technique_def = create_template(
                    get_best_direct_technique(dataset_name), replacement_dict
                )
                add_metrics(
                    dataset_name,
                    direct_technique_def,
                    DIRECT_ID,
                    path_name,
                )

                # transitive
                transitive_technique_def = create_template(
                    get_best_transitive_technique(dataset_name), replacement_dict
                )
                add_metrics(
                    dataset_name,
                    transitive_technique_def,
                    TRANSITIVE_ID,
                    path_name,
                )

                # HYBRID
                hybrid_technique_definition = create_template(
                    get_best_hybrid_technique(dataset_name), replacement_dict
                )
                add_metrics(
                    dataset_name,
                    hybrid_technique_definition,
                    HYBRID_ID,
                    path_name,
                )
                comparison_dict.update(
                    {dataset_name: (direct_technique_def, hybrid_technique_definition)}
                )
            gain_table = metric_table.calculate_gain_between_techniques(comparison_dict)
            gain_table.table["path"] = path_name

            aggregate_gain = (
                gain_table.table
                if aggregate_gain is None
                else pd.concat([gain_table.table, aggregate_gain])
            )

            aggregate_metric = (
                metric_table.table
                if aggregate_metric is None
                else pd.concat([metric_table.table, aggregate_metric])
            )

            MetricTable(aggregate_metric).create_lag_norm_inverted(
                drop_old=True
            ).melt_metrics().save(METRIC_TABLE_EXPORT_PATH)
            self.export_paths.append(METRIC_TABLE_EXPORT_PATH)

            MetricTable(aggregate_gain).melt_metrics().save(GAIN_TABLE_EXPORT_PATH)
            self.export_paths.append(GAIN_TABLE_EXPORT_PATH)
        return aggregate_gain

    @staticmethod
    def name() -> str:
        return EXPERIMENT_NAME


if __name__ == "__main__":
    EvaluatePaths().run()
    print("Done")
