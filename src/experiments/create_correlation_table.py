from api.tables.metric_table import MetricTable
from api.tables.table import Table
from experiments.constants import (
    PATH_TO_ARTIFACT_SAMPLING_AGG,
    PATH_TO_RQ1_CORRELATION,
    PATH_TO_RQ2_CORRELATION,
)
from experiments.experiment import Experiment

EXPERIMENT_NAME = "correlation_table"


class CalculateCorrelation(Experiment):
    """
    Creates the correlation table using the intermediate sampling tables.
    """

    def run(self) -> Table:
        """
        Reads aggregate sampling table and calculates spearman's correlation per dataset
        :return:
        """
        artifact_correlation_df: Table = (
            MetricTable(path_to_table=PATH_TO_ARTIFACT_SAMPLING_AGG)
            .create_correlation_table()
            .round()
            .save(PATH_TO_RQ1_CORRELATION)
        )
        self.export_paths.append(PATH_TO_RQ1_CORRELATION)

        trace_correlation_df: Table = (
            MetricTable(path_to_table=PATH_TO_ARTIFACT_SAMPLING_AGG)
            .create_correlation_table()
            .round()
            .save(PATH_TO_RQ2_CORRELATION)
        )
        self.export_paths.append(PATH_TO_RQ2_CORRELATION)

        return artifact_correlation_df + trace_correlation_df

    @staticmethod
    def name() -> str:
        return "correlation_table"
