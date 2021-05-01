"""
The following script is responsible for calculating the metrics on the individual queries for the best overall technique.
"""
import os
from typing import List

from api.constants.processing import (
    DATASET_COLNAME,
    METRIC_COLNAME,
    METRIC_SCORE_COLNAME,
    TECHNIQUE_TYPE_COLNAME,
)
from api.constants.techniques import DIRECT_ID, HYBRID_ID
from api.tables.metric_table import MetricTable, Metrics
from api.tables.table import Table
from api.tracer import Tracer
from experiments.meta.experiment import Experiment
from utilities.constants import (
    DATASET_COLUMN_ORDER,
    PATH_TO_AGGREGATE_TABLES,
    PATH_TO_INDIVIDUAL_QUERIES_AGG,
)
from utilities.technique_extractors import get_best_direct_technique

BEST_OVERALL_TECHNIQUE = "(o (SUM) ((. (VSM NT) (0 2)) (x (SUM GLOBAL) ((. (VSM NT) (0 1)) (. (VSM NT) (1 2))))))"

EXPORT_PATH = os.path.join(PATH_TO_AGGREGATE_TABLES, "best_overall.csv")


class CalculateOverallBest(Experiment):
    """
    Given a dataset, extracts its best no trace technique and calculates metric on the individual queries
    of the technique.
    """

    def run(self) -> Table:
        """
        Returns a metric table containing all of the metrics calculated for each technique in df
        :return: metric table with single query metrics for each technique applied to specified dataset in row
        """
        tracer = Tracer()
        metric_table = MetricTable()

        for dataset_name in DATASET_COLUMN_ORDER:
            hybrid_query_metrics: List[Metrics] = tracer.get_metrics(
                dataset_name, BEST_OVERALL_TECHNIQUE, summary_metrics=False
            )
            metric_table.add(
                hybrid_query_metrics,
                other={
                    DATASET_COLNAME: dataset_name,
                    TECHNIQUE_TYPE_COLNAME: HYBRID_ID,
                },
                create_index=True,
            )

            direct_query_metrics: List[Metrics] = tracer.get_metrics(
                dataset_name,
                get_best_direct_technique(dataset_name),
                summary_metrics=False,
            )
            metric_table.add(
                direct_query_metrics,
                other={
                    DATASET_COLNAME: dataset_name,
                    TECHNIQUE_TYPE_COLNAME: DIRECT_ID,
                },
                create_index=True,
            )

        individual_queries_aggregate = (
            metric_table.create_lag_norm_inverted(drop_old=True)
            .melt_metrics(metric_value_col_name=METRIC_SCORE_COLNAME)
            .sort(DATASET_COLUMN_ORDER)
            .col_values_to_upper(METRIC_COLNAME)
            .save(EXPORT_PATH)
        )

        self.export_paths.append(PATH_TO_INDIVIDUAL_QUERIES_AGG)

        return individual_queries_aggregate

    @staticmethod
    def name() -> str:
        return "best_overall"


if __name__ == "__main__":
    CalculateOverallBest().run()
    print("goodbye")
