from api.extension.experiment_types import ExperimentTraceType
from api.tables.metric_table import MetricTable
from api.tables.table import Table
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from api.technique.variationpoints.scalers.scaling_method import ScalingMethod
from experiments.constants import (
    PATH_TO_METRIC_TABLE_AGGREGATE,
    PATH_TO_RQ1_GAIN,
    PATH_TO_RQ2_GAIN,
)
from experiments.create_metric_table import create_combined_definition
from experiments.experiment import Experiment


class CalculateGain(Experiment):
    """
    Creates two tables representing:
    * Gain on direct best when leveraging intermediate artifacts
    * Gain on direct best when leveraging intermediate traces
    """

    best_traced_technique = (
        AlgebraicModel.LSI,
        ExperimentTraceType.ALL,
        AlgebraicModel.VSM,
        ScalingMethod.INDEPENDENT,
        AggregationMethod.SUM,
        AggregationMethod.MAX,
    )

    @staticmethod
    def calculate_rq1_gain(agg_df, direct_indices) -> Table:
        no_traces_target_indices = agg_df.get_best_combined_no_traces_indices()
        no_traces_gain_df = agg_df.calculate_gain(
            base_indices=direct_indices, target_indices=no_traces_target_indices
        )

        return no_traces_gain_df

    def calculate_rq2_gain(self, agg_df: MetricTable, direct_indices) -> Table:
        traces_target_indices = agg_df.get_technique_indices(
            create_combined_definition(self.best_traced_technique)
        )
        traces_gain_df = agg_df.calculate_gain(
            base_indices=direct_indices, target_indices=traces_target_indices
        )

        return traces_gain_df

    def run(self) -> Table:
        agg_metric_table = MetricTable(path_to_table=PATH_TO_METRIC_TABLE_AGGREGATE)
        direct_indices = agg_metric_table.get_direct_best_indices()
        rq1_gain_df = self.calculate_rq1_gain(agg_metric_table, direct_indices)
        rq2_gain_df = self.calculate_rq2_gain(agg_metric_table, direct_indices)

        rq1_gain_df.save(PATH_TO_RQ1_GAIN)
        self.export_paths.append(PATH_TO_RQ1_GAIN)

        rq2_gain_df.save(PATH_TO_RQ2_GAIN)
        self.export_paths.append(PATH_TO_RQ2_GAIN)
        return rq1_gain_df

    @staticmethod
    def name() -> str:
        return "gain_table"


if __name__ == "__main__":
    CalculateGain().run()
