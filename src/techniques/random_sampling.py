import os

import click
import pandas as pd

from api.constants.paths import (
    PATH_TO_CORRELATION_INTERMEDIARY,
    PATH_TO_CORRELATION_PROCESSED,
    PATH_TO_DATA_SOURCE,
    PATH_TO_SAMPLING_INTERMEDIARY,
    PATH_TO_SAMPLING_PROCESSED,
    PATH_TO_TECHNIQUE_SOURCE_DATA,
)
from api.constants.processing import (
    AP_COLNAME,
    LAG_COLNAME,
    METRIC_COLNAME,
    NAME_COLNAME,
    TRANSITIVE_TRACE_TYPE_COLNAME,
    n_sig_figs,
)
from api.extension.experiment_types import ExperimentTraceType, SamplingExperiment
from api.tables.table import Table
from api.tracer import Tracer
from src.analysis.sampling.correlation_helper import (
    create_correlation_matrix,
    create_gain_correlation_table,
)
from src.runner.experiment import CommandSequence, Experiment, Runnable
from src.runner.progress_bar_factory import create_bar

SamplingInitData = (str, str)

n_iterations = 100
n_intervals = 10

""" MUST MANUALLY UPDATE
because we are technically defining a new technique, SampledIntermediateTechnique
"""
best_none_techniques = {
    "DRONE": "(o (MAX) ((. (VSM GLOBAL NT) (0 2)) (~ (SUM %f) ((. (LSI GLOBAL NT) (0 1)) (. (LSI GLOBAL NT) (1 2))))))",
    "EBT": "(o (MAX) ((. (VSM GLOBAL NT) (0 2)) (~ (MAX %f) ((. (VSM GLOBAL NT) (0 1)) (. (VSM GLOBAL NT) (1 2))))))",
    "EASYCLINIC": "(o (MEDIAN) ((. (VSM GLOBAL NT) (0 2)) (~ (MAX %f) ((. (VSM SINGLE NT) (0 1)) (. (VSM SINGLE NT) (1 2))))))",
    "TRAINCONTROLLER": "(o (MAX) ((. (VSM GLOBAL NT) (0 2)) (~ (MAX %f) ((. (LSI GLOBAL NT) (0 1)) (. (LSI GLOBAL NT) (1 2))))))",
    "WARC": "(o (PCA) ((. (VSM GLOBAL NT) (0 2)) (~ (MAX %f) ((. (VSM SINGLE NT) (0 1)) (. (VSM SINGLE NT) (1 2))))))",
}

best_traced_technique = "(o (MAX) ((. (VSM GLOBAL NT) (0 2)) ($ (MAX %f) ((. (VSM GLOBAL NT) (0 1)) (. (VSM GLOBAL NT) (1 2))))))"

SAMPLING_FOLDER_NAME = "sampling"


# TODO: What is GenericData here?
# TODO: Setup functions to work with new Command/Experiment interface
def create_random_sampling_experiment():
    """
    Returns the random sampling
    :return:
    """

    steps = CommandSequence()

    steps.add(Runnable(prompt_experiment_configuration))
    steps.add(Runnable(run_sampling))
    steps.add(Runnable(post_processing))

    experiment = Experiment(
        steps,
    )

    experiment.prompt_init_data_func = None
    experiment.experiment_func = run_sampling
    experiment.post_process_pipeline = [post_processing]
    experiment.export_path_func = create_run_export_path
    return experiment


def experiment_iterable(e_type: str):
    with create_bar(
        "sampling %s" % e_type, range(0, n_intervals + 1), length=n_intervals + 1
    ) as intervals:
        for interval_index in intervals:
            percentage = interval_index / n_intervals
            for iteration_index in range(n_iterations):
                yield interval_index, iteration_index, percentage


def prompt_experiment_configuration():
    options = "(%s)" % "|".join([et.value for et in SamplingExperiment])
    d = click.prompt("Dataset name").strip()
    e = click.prompt("Sampling method %s" % options).strip()
    return d, SamplingExperiment(e).value


def create_run_export_path(init_data: SamplingInitData):
    dataset, experiment_type = init_data
    return os.path.join(
        PATH_TO_DATA_SOURCE, SAMPLING_FOLDER_NAME, experiment_type, dataset + ".csv"
    )


def load_best_none_techniques():
    best_dict = {}
    for f in os.listdir(PATH_TO_TECHNIQUE_SOURCE_DATA):
        if f[0] == ".":
            continue
        dataset_name = f[:-4]
        techniques_df = pd.read_csv(os.path.join(PATH_TO_TECHNIQUE_SOURCE_DATA, f))
        techniques_df = techniques_df[
            techniques_df[TRANSITIVE_TRACE_TYPE_COLNAME]
            == ExperimentTraceType.NONE.value
        ]
        best_dict[dataset_name] = techniques_df.set_index(NAME_COLNAME)[
            AP_COLNAME
        ].idxmax()
    return best_dict


def run_sampling(init_data):
    dataset, experiment_type_str = init_data
    experiment_type = SamplingExperiment(experiment_type_str)

    tracer = Tracer()
    metric_table = Table()

    for interval_index, iteration_index, percentage in experiment_iterable(
        experiment_type.value
    ):
        if experiment_type == SamplingExperiment.ARTIFACTS:
            if interval_index == 0:
                continue
            metrics = tracer.get_metrics(
                dataset, best_none_techniques[dataset.upper()] % percentage
            )
        elif experiment_type == SamplingExperiment.TRACES:
            metrics = tracer.get_metrics(dataset, best_traced_technique % percentage)
        else:
            raise ValueError("Sampling src not implemented %s" % experiment_type.value)
        metric_table.add(metrics, {"percent": percentage, "iteration": iteration_index})

    return metric_table


def post_processing(init_data: (str, str), metric_table: Table):
    dataset, experiment_type = init_data

    aggregate_file_path = os.path.join(
        PATH_TO_SAMPLING_PROCESSED, "%s_sampling.csv" % experiment_type
    )
    component_folder = os.path.join(PATH_TO_SAMPLING_INTERMEDIARY, experiment_type)

    processed_df = metric_table.setup_for_graph()

    intermediary_path = os.path.join(component_folder, dataset + ".csv")
    processed_df.to_csv(intermediary_path, index=False)
    Table.aggregate_intermediate_files(component_folder).format_table().save(
        aggregate_file_path
    )

    # calculate Spearman's correlation
    data_processed_without_lag = processed_df[
        processed_df[METRIC_COLNAME] != LAG_COLNAME
    ]
    correlation_df = create_correlation_matrix(data_processed_without_lag).round(
        n_sig_figs
    )

    # combine with gain table and export
    gain_correlation_df = create_gain_correlation_table(
        dataset, experiment_type, correlation_df
    ).round(n_sig_figs)
    correlation_base_folder = os.path.join(
        PATH_TO_CORRELATION_INTERMEDIARY, experiment_type
    )
    correlation_export_path = os.path.join(correlation_base_folder, dataset + ".csv")
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


def run_post_processing():
    datasets = ["EBT", "WARC", "Drone", "TrainController", "EasyClinic"]
    for dataset_name in datasets:
        experiment_type = "traces"
        data = pd.read_csv(create_run_export_path((dataset_name, experiment_type)))
        metric_table = Table()
        metric_table.table = data
        post_processing((dataset_name, experiment_type), metric_table)


if __name__ == "__main__":
    # # Setup
    # Cache.CACHE_ON = True
    # src = create_experiment()
    #
    # # Work
    # src.run()
    #
    # # Cleanup
    # Cache.cleanup(src.init_data[0])
    run_post_processing()
