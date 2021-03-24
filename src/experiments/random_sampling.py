import os

import click

from api.constants.processing import (
    DATASET_COLUMN_ORDER,
)
from api.extension.experiment_types import SamplingExperiment
from api.tables.metric_table import MetricTable
from api.tables.table import Table
from api.tracer import Tracer
from experiments.constants import (
    PATH_TO_ARTIFACT_SAMPLING_AGG,
    PATH_TO_SAMPLED_METRIC_TABLES,
    PATH_TO_TRACES_SAMPLING_AGG,
)
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


def prompt_user():
    dataset_name = click.prompt(
        "Please select a dataset: ",
        type=click.Choice(DATASET_COLUMN_ORDER, case_sensitive=False),
    )
    sampling_method = click.prompt(
        "Please select a sampling method: ",
        type=click.Choice(SAMPLING_METHODS, case_sensitive=False),
    )
    return dataset_name, sampling_method


class SampledMetricTable(Experiment):
    """
    Contains the experiment interface for sampling techniques.
    """

    def run(self) -> Table:
        dataset_name, sampling_method = prompt_user()
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

        metric_table = create_sampled_metric_table(dataset_name, sampling_method)
        metric_table.sort_cols().save(run_export_path)
        Table.aggregate_intermediate_files(path_to_intermediate_files).sort_cols().save(
            aggregate_file_path
        )
        return metric_table

    @staticmethod
    def name() -> str:
        return EXPERIMENT_NAME


if __name__ == "__main__":
    SampledMetricTable().run()
