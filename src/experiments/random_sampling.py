import os

import click

from api.constants.processing import (
    DATASET_COLUMN_ORDER,
)
from api.extension.experiment_types import SamplingExperiment
from api.tables.metric_table import MetricTable
from api.tables.table import Table
from api.tracer import Tracer
from experiments.constants import PATH_TO_SAMPLED_METRIC_TABLES
from src.experiments.experiment import Experiment
from src.experiments.progress_bar_factory import create_bar

SamplingInitData = (str, str)

n_iterations = 100
n_intervals = 10

""" MUST MANUALLY UPDATE
because we are technically defining a new technique, SampledIntermediateTechnique
"""

best_none_techniques = "(o (MAX) ((. (VSM NT) (0 2)) (~ (SUM GLOBAL %f) \
((. (VSM NT) (0 1)) (. (VSM NT) (1 2))))))"

best_traced_technique = "(o (MAX) ((. (VSM NT) (0 2)) ($ (SUM GLOBAL %f) \
((. (VSM T) (0 1)) (. (VSM T) (1 2))))))"

SAMPLING_FOLDER_NAME = "sampling"

EXPERIMENT_NAME = "random_sampling"

EXPERIMENT_DESCRIPTION = (
    "Samples artifacts or traces iterating between 0 and 100 in increments of 10."
)

SAMPLING_METHODS = [et.value for et in SamplingExperiment]


def create_sampling_sections():
    for interval_index in range(0, n_intervals + 1):
        percentage = interval_index / n_intervals
        for iteration_index in range(n_iterations):
            yield interval_index, iteration_index, percentage


def create_sampled_metric_table(dataset_name: str, sampling_method: str) -> MetricTable:
    experiment_type = SamplingExperiment(sampling_method)

    tracer = Tracer()
    metric_table = MetricTable()
    loading_message = "sampling %s" % sampling_method
    sampling_intervals = create_sampling_sections()
    with create_bar(
        loading_message, sampling_intervals, length=n_intervals * n_iterations
    ) as iter_id:
        for interval_index, iteration_index, percentage in iter_id:
            if experiment_type == SamplingExperiment.ARTIFACTS:
                if interval_index == 0:
                    continue
                metrics = tracer.get_metrics(
                    dataset_name, best_none_techniques % percentage
                )
            elif experiment_type == SamplingExperiment.TRACES:
                metrics = tracer.get_metrics(
                    dataset_name, best_traced_technique % percentage
                )
            else:
                raise ValueError(
                    "Sampling src not implemented %s" % experiment_type.value
                )
            metric_table.add(
                metrics, {"percent": percentage, "iteration": iteration_index}
            )

    return metric_table


class SampledMetricTable(Experiment):
    """
    Contains the experiment interface for sampling techniques.
    """

    def run(self) -> Table:
        dataset_name = click.prompt(
            "Please select a dataset: ",
            type=click.Choice(DATASET_COLUMN_ORDER, case_sensitive=False),
        )
        sampling_method = click.prompt(
            "Please select a sampling method: ",
            type=click.Choice(SAMPLING_METHODS, case_sensitive=False),
        )
        metric_table = create_sampled_metric_table(dataset_name, sampling_method)
        export_path = os.path.join(
            PATH_TO_SAMPLED_METRIC_TABLES, sampling_method, dataset_name + ".csv"
        )
        metric_table.sort_cols().save(export_path)
        return metric_table

    @property
    def description(self) -> str:
        return EXPERIMENT_DESCRIPTION

    @staticmethod
    def name() -> str:
        return EXPERIMENT_NAME


#
# def post_processing(init_data: (str, str), metric_table: Table):
#     dataset, experiment_type = init_data
#
#     aggregate_file_path = os.path.join(
#         PATH_TO_SAMPLING_PROCESSED, "%s_sampling.csv" % experiment_type
#     )
#     component_folder = os.path.join(PATH_TO_SAMPLING_INTERMEDIARY, experiment_type)
#
#     processed_df = metric_table.setup_for_graph()
#
#     intermediary_path = os.path.join(component_folder, dataset + ".csv")
#     processed_df.to_csv(intermediary_path, index=False)
#     Table.aggregate_intermediate_files(component_folder).format_table().save(
#         aggregate_file_path
#     )
#
#     # calculate Spearman's correlation
#     data_processed_without_lag = processed_df[
#         processed_df[METRIC_COLNAME] != LAG_COLNAME
#     ]
#     correlation_df = create_correlation_matrix(data_processed_without_lag).round(
#         n_sig_figs
#     )
#
#     # combine with gain table and export
#     gain_correlation_df = create_gain_correlation_table(
#         dataset, experiment_type, correlation_df
#     ).round(n_sig_figs)
#     correlation_base_folder = os.path.join(
#         PATH_TO_CORRELATION_INTERMEDIARY, experiment_type
#     )
#     correlation_export_path = os.path.join(correlation_base_folder, dataset + ".csv")
#     gain_correlation_df.to_csv(correlation_export_path, index=False)
#
#     # update aggregate gain-correlation table
#     correlation_agg_path = os.path.join(
#         PATH_TO_CORRELATION_PROCESSED,
#         experiment_type,
#         "%s_gain_correlation.csv" % experiment_type,
#     )
#     Table.aggregate_intermediate_files(correlation_base_folder).format_table().save(
#         correlation_agg_path
#     )


# def run_post_processing():
#     datasets = ["EBT", "WARC", "Drone", "TrainController", "EasyClinic"]
#     for dataset_name in datasets:
#         experiment_type = "traces"
#         data = pd.read_csv(create_run_export_path((dataset_name, experiment_type)))
#         metric_table = Table()
#         metric_table.table = data
#         post_processing((dataset_name, experiment_type), metric_table)


if __name__ == "__main__":
    SampledMetricTable().run()
