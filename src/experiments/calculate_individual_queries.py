"""
The following script is intended to calculate a csv file containing the
map, lag, and auc of individual queries in some dataset for some technique.
"""
import os

from api.constants.processing import (
    DATASET_COLNAME,
    METRIC_COLNAME,
    METRIC_SCORE_COLNAME,
    NAME_COLNAME,
    TECHNIQUE_TYPE_COLNAME,
)
from api.constants.techniques import COMBINED_ID, DIRECT_ID, TRANSITIVE_ID
from api.tables.metric_table import MetricTable, Metrics
from api.tables.table import Table
from api.technique.definitions.combined.technique import (
    CombinedTechnique,
    create_technique_by_name,
)
from api.technique.definitions.direct.technique import DirectTechnique
from api.technique.definitions.transitive.technique import TransitiveTechnique
from api.tracer import Tracer
from experiments.constants import (
    PATH_TO_INDIVIDUAL_QUERIES,
    PATH_TO_INDIVIDUAL_QUERIES_AGG,
    PATH_TO_METRIC_TABLE_AGGREGATE,
)
from experiments.create_sampled_table import get_best_no_trace_technique
from experiments.experiment import Experiment
from utilities.prompts import prompt_for_dataset


def get_direct_best_technique(dataset_name: str) -> str:
    agg_metric_table = MetricTable(path_to_table=PATH_TO_METRIC_TABLE_AGGREGATE)
    best_direct_definition = agg_metric_table.get_direct_best_techniques().set_index(
        DATASET_COLNAME
    )
    return best_direct_definition.loc[dataset_name][NAME_COLNAME]


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
        best_combined_definition = get_best_no_trace_technique(dataset_name)
        direct_best_definition = get_direct_best_technique(dataset_name)

        tracer = Tracer()
        metric_table = MetricTable()

        combined_metrics: [Metrics] = tracer.get_metrics(
            dataset_name, best_combined_definition, summary_metrics=False
        )
        metric_table.add(
            combined_metrics,
            other={TECHNIQUE_TYPE_COLNAME: COMBINED_ID},
            create_index=True,
        )
        direct_metrics: [Metrics] = tracer.get_metrics(
            dataset_name, direct_best_definition, summary_metrics=False
        )
        metric_table.add(
            direct_metrics, other={TECHNIQUE_TYPE_COLNAME: DIRECT_ID}, create_index=True
        )

        """
        Export
        """
        export_path = os.path.join(PATH_TO_INDIVIDUAL_QUERIES, dataset_name + ".csv")
        metric_table.save(export_path)
        self.export_paths.append(export_path)

        (
            MetricTable(
                Table.aggregate_intermediate_files(PATH_TO_INDIVIDUAL_QUERIES).table
            )
            .melt_metrics(metric_value_col_name=METRIC_SCORE_COLNAME)
            .sort_cols()
            .col_values_to_upper(METRIC_COLNAME)
            # .to_title_case(exclude=[METRIC_COLNAME])
            .save(PATH_TO_INDIVIDUAL_QUERIES_AGG)
        )
        self.export_paths.append(PATH_TO_INDIVIDUAL_QUERIES_AGG)

    @staticmethod
    def name() -> str:
        return "individual_queries"


def get_technique_type(technique_name: str):
    technique = create_technique_by_name(technique_name)
    if isinstance(technique, DirectTechnique):
        return DIRECT_ID
    elif isinstance(technique, TransitiveTechnique):
        return TRANSITIVE_ID
    elif isinstance(technique, CombinedTechnique):
        return COMBINED_ID
    else:
        raise Exception("Technique %s not implemented." % technique.name)


if __name__ == "__main__":
    CalculateIndividualQueries().run()
    print("goodbye")
