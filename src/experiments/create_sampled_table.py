import os

from api.constants.processing import METRIC_COLNAME
from api.extension.experiment_types import SamplingExperiment
from api.tables.metric_table import MetricTable
from api.tables.table import Table
from api.tracer import Tracer
from experiments.meta.experiment import Experiment
from utilities.constants import (
    DATASET_COLUMN_ORDER,
    PATH_TO_ARTIFACT_SAMPLING_AGG,
    PATH_TO_SAMPLED_METRIC_TABLES,
    PATH_TO_TRACES_SAMPLING_AGG,
)
from utilities.progress_bar_factory import create_loading_bar
from utilities.prompts import prompt_for_dataset, prompt_for_sampling_method
from utilities.technique_extractors import get_best_combined_sampled_technique

SamplingInitData = (str, str)

N_INCREMENTS = 10  # increments to take between 0 and 100% of samples
N_ITERATIONS = 100  # iterations per increment

""" MUST MANUALLY UPDATE
because we are technically defining a new technique, SampledIntermediateTechnique
"""

best_traced_technique = "(o (SUM) (\
(. (LSI NT) (0 2))\
 ($ (SUM INDEPENDENT %f) ((. (VSM NT) (0 1)) (. (VSM NT) (1 2))))))"

SAMPLING_FOLDER_NAME = "sampling"

EXPERIMENT_NAME = "random_sampling"

EXPERIMENT_DESCRIPTION = (
    "Samples artifacts or traces iterating between 0 and 100 in increments of 10."
)


class CreateSampledTable(Experiment):
    """
    Contains the experiment interface for sampling techniques.
    """

    def run(self) -> Table:
        dataset_name, sampling_method = prompt_user()

        """
        Create export paths using user responses:
        1. one for intermediate folder
        2. current run export path
        3. aggregate export path
        """
        path_to_intermediate_files = os.path.join(
            PATH_TO_SAMPLED_METRIC_TABLES, sampling_method
        )
        run_export_path = os.path.join(
            path_to_intermediate_files, dataset_name + ".csv"
        )
        aggregate_file_path = (
            PATH_TO_ARTIFACT_SAMPLING_AGG
            if sampling_method in PATH_TO_ARTIFACT_SAMPLING_AGG
            else PATH_TO_TRACES_SAMPLING_AGG
        )

        """
        Current run
        """

        metric_table = create_sampled_metric_table(dataset_name, sampling_method)
        metric_table.sort(DATASET_COLUMN_ORDER).save(run_export_path)

        """
        Update aggregate
        """
        self.export_paths.append(run_export_path)
        MetricTable(
            Table.aggregate_intermediate_files(path_to_intermediate_files)
            .sort(DATASET_COLUMN_ORDER)
            .table
        ).create_lag_norm_inverted(drop_old=True).melt_metrics().col_values_to_upper(
            METRIC_COLNAME
        ).save(
            aggregate_file_path
        )
        self.export_paths.append(aggregate_file_path)
        return metric_table

    @staticmethod
    def name() -> str:
        return EXPERIMENT_NAME


def create_sampled_metric_table(dataset_name: str, sampling_method: str) -> MetricTable:
    """
    Creates a MetricTable for each percentage (between 0 and 100 in increments of 10) with each percentage
    containing 100 iterations.
    :param dataset_name:
    :param sampling_method:
    :return: MetricTable containing metrics, percent, and iteration columns as identifying information
    """
    experiment_type = SamplingExperiment(sampling_method)

    tracer = Tracer()
    metric_table = MetricTable()
    loading_message = "sampling %s" % sampling_method
    sampling_intervals = create_sampling_sections()
    best_no_trace_technique = get_best_combined_sampled_technique(dataset_name)
    with create_loading_bar(
        loading_message, sampling_intervals, length=N_INCREMENTS * N_ITERATIONS
    ) as iter_id:
        for interval_index, iteration_index, percentage in iter_id:
            if experiment_type == SamplingExperiment.ARTIFACTS:
                if (
                    interval_index == 0
                ):  # using 0% of intermediate artifacts is not a valid Hybrid technique
                    continue
                technique_name = best_no_trace_technique % percentage
            elif experiment_type == SamplingExperiment.TRACES:
                technique_name = best_traced_technique % percentage
            else:
                raise ValueError(
                    "Sampling src not implemented %s" % experiment_type.value
                )
            metrics = tracer.get_metrics(dataset_name, technique_name)
            metric_table.add(
                metrics, {"percent": percentage, "iteration": iteration_index}
            )

    return metric_table


def create_sampling_sections():
    """
    Creates generator for iterating through n_intervals from 0 to 100% which n_iterations per each increment.
    :return: (int, int, float) representing interval index, iteration index, and percentage
    """
    for interval_index in range(0, N_INCREMENTS + 1):
        percentage = interval_index / N_INCREMENTS
        for iteration_index in range(N_ITERATIONS):
            yield interval_index, iteration_index, percentage


def prompt_user():
    """
    :return: (str, str) representing dataset to sample and what to sample (e.g. artifacts or traces)
    """
    dataset_name = prompt_for_dataset()
    sampling_method = prompt_for_sampling_method()
    return dataset_name, sampling_method
