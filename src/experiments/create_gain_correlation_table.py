from api.tables.table import Table
from experiments.constants import PATH_TO_GAIN_AGGREGATE
from experiments.experiment import Experiment

EXPERIMENT_NAME = "gain_correlation_table"

import pandas as pd


class GainCorrelationTable(Experiment):
    """
    Combines aggregate gain and correlation tables.
    """

    def run(self) -> Table:
        gain_df = pd.read_csv(PATH_TO_GAIN_AGGREGATE)
        aggregate_file_path = (
            PATH_TO_ARTIFACT_SAMPLING_AGG
            if sampling_method in PATH_TO_ARTIFACT_SAMPLING_AGG
            else PATH_TO_TRACES_SAMPLING_AGG
        )
        gain_correlation_df = create_gain_correlation_table(
            dataset, experiment_type, correlation_df
        ).round(n_sig_figs)

        correlation_base_folder = os.path.join(
            PATH_TO_CORRELATION_INTERMEDIARY, experiment_type
        )
        correlation_export_path = os.path.join(
            correlation_base_folder, dataset + ".csv"
        )
        gain_correlation_df.to_csv(correlation_export_path, index=False)

        # update aggregate gain-correlation table
        correlation_agg_path = os.path.join(
            PATH_TO_CORRELATION_PROCESSED,
            experiment_type,
            "%s_gain_correlation.csv" % experiment_type,
        )
        Table.aggregate_intermediate_files(correlation_base_folder).format_table().save(
            correlation_agg_path
        )

    @staticmethod
    def name() -> str:
        return EXPERIMENT_NAME
