from analysis.sampling.correlation_helper import (
    create_correlation_matrix,
)
from api.constants.processing import N_SIG_FIGS
from api.tables.metric_table import MetricTable
from api.tables.table import Table
from experiments.constants import (
    PATH_TO_ARTIFACT_CORRELATION_AGG,
    PATH_TO_ARTIFACT_SAMPLING_AGG,
    PATH_TO_TRACES_CORRELATION_AGG,
    PATH_TO_TRACES_SAMPLING_AGG,
)
from experiments.experiment import Experiment
from utilities.prompts import prompt_for_sampling_method

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
        sampling_method = prompt_for_sampling_method()
        sampling_agg_path = (
            PATH_TO_ARTIFACT_SAMPLING_AGG
            if sampling_method in PATH_TO_ARTIFACT_SAMPLING_AGG
            else PATH_TO_TRACES_SAMPLING_AGG
        )

        processed_df = MetricTable(path_to_table=sampling_agg_path).setup_for_graph()
        correlation_df = create_correlation_matrix(processed_df.table).round(N_SIG_FIGS)

        agg_file_path = (
            PATH_TO_ARTIFACT_CORRELATION_AGG
            if sampling_method in PATH_TO_ARTIFACT_CORRELATION_AGG
            else PATH_TO_TRACES_CORRELATION_AGG
        )

        correlation_df.to_csv(agg_file_path, index=False)
        self.export_paths.append(agg_file_path)
        return Table(correlation_df)

    @staticmethod
    def name() -> str:
        return "correlation_table"
