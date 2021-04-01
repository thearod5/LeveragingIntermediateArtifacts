"""
The following script is intended to calculate a csv file containing the
map, lag, and auc of individual queries in some dataset for some technique.
"""
import os

from api.constants.processing import (
    METRIC_COLNAME,
    METRIC_SCORE_COLNAME,
    TECHNIQUE_TYPE_COLNAME,
)
from api.constants.techniques import DIRECT_ID, HYBRID_ID, TRANSITIVE_ID
from api.tables.metric_table import MetricTable, Metrics
from api.tables.table import Table
from api.tracer import Tracer
from experiments.meta.experiment import Experiment
from utilities.constants import (
    PATH_TO_INDIVIDUAL_QUERIES,
    PATH_TO_INDIVIDUAL_QUERIES_AGG,
)
from utilities.prompts import prompt_for_dataset
from utilities.technique_extractors import (
    get_best_direct_technique,
    get_best_hybrid_technique,
    get_best_transitive_technique,
)


class CalculateIndividualQueries(Experiment):
    """
    Given a dataset, extracts its best no trace technique and calculates metric on the individual queries
    of the technique.
    """

    def run(self) -> Table:
        """
        Returns a metric table containing all of the metrics calculated for each technique in df
        :return: metric table with single query metrics for each technique applied to specified dataset in row
        """
        dataset_name = prompt_for_dataset()

        """
        Find best techniques
        """
        direct_best_definition = get_best_direct_technique(dataset_name)
        transitive_best_definition = get_best_transitive_technique(dataset_name)
        combined_best_definition = get_best_hybrid_technique(dataset_name)

        """
        Calculate metrics for individual queries on dataset
        """
        tracer = Tracer()
        metric_table = MetricTable()

        direct_metrics: [Metrics] = tracer.get_metrics(
            dataset_name, direct_best_definition, summary_metrics=False
        )
        metric_table.add(
            direct_metrics, other={TECHNIQUE_TYPE_COLNAME: DIRECT_ID}, create_index=True
        )

        transitive_metrics: [Metrics] = tracer.get_metrics(
            dataset_name, transitive_best_definition, summary_metrics=False
        )
        metric_table.add(
            transitive_metrics,
            other={TECHNIQUE_TYPE_COLNAME: TRANSITIVE_ID},
            create_index=True,
        )

        combined_metrics: [Metrics] = tracer.get_metrics(
            dataset_name, combined_best_definition, summary_metrics=False
        )
        metric_table.add(
            combined_metrics,
            other={TECHNIQUE_TYPE_COLNAME: HYBRID_ID},
            create_index=True,
        )

        """
        Export individual run
        """
        export_path = os.path.join(PATH_TO_INDIVIDUAL_QUERIES, dataset_name + ".csv")
        (metric_table.sort(DATASET_COLUMN_ORDER).save(export_path))
        self.export_paths.append(export_path)

        """
        Update aggregate
        """

        individual_queries_aggregate = (
            MetricTable(
                Table.aggregate_intermediate_files(PATH_TO_INDIVIDUAL_QUERIES).table
            )
            .create_lag_norm_inverted(remove_old_lag=True)
            .melt_metrics(metric_value_col_name=METRIC_SCORE_COLNAME)
            .sort()
            .col_values_to_upper(METRIC_COLNAME)
            .to_title_case(exclude=METRIC_COLNAME)
            .save(PATH_TO_INDIVIDUAL_QUERIES_AGG)
        )

        # aggregate_table
        self.export_paths.append(PATH_TO_INDIVIDUAL_QUERIES_AGG)

        return individual_queries_aggregate

    @staticmethod
    def name() -> str:
        return "individual_queries"


if __name__ == "__main__":
    CalculateIndividualQueries().run()
    print("goodbye")
