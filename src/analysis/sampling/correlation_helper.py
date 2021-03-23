import os

import pandas as pd
from scipy.stats import spearmanr

from api.constants.paths import PATH_TO_GAIN_INTERMEDIARY
from api.constants.processing import (
    CORRELATION_COLNAME,
    DATASET_COLNAME,
    Data,
    METRIC_COLNAME,
    N_SIG_FIGS,
    PERCENT_COLNAME,
    P_VALUE_COLNAME,
    TRANSITIVE_TRACE_TYPE_COLNAME,
    VALUE_COLNAME,
)
from api.extension.experiment_types import ExperimentTraceType, SamplingExperiment


def create_correlation_matrix(data: Data):
    """
    Creates a matrix capturing the correlation and pvalue of association between metrics and percent
    :param data: contains metrics and percent as columns
    :return: Data containing row for each metric with correlation (and pvalue) of metric value and percent
    """
    assert all(
        [col in data for col in [METRIC_COLNAME, VALUE_COLNAME, PERCENT_COLNAME]]
    ), data.columns
    result = pd.DataFrame()
    metrics = data[METRIC_COLNAME].unique()
    for metric_name in metrics:
        metric_mask = data[METRIC_COLNAME] == metric_name
        metric_df = data[metric_mask]

        metric_values = list(metric_df["value"])
        percent_values = list(metric_df["percent"])

        correlation, p_value = spearmanr(metric_values, percent_values)
        result = result.append(
            {
                METRIC_COLNAME: metric_name,
                CORRELATION_COLNAME: correlation,
                P_VALUE_COLNAME: "<0.001" if p_value < 0.001 else p_value,
            },
            ignore_index=True,
        )
    return result.reset_index(drop=True).round(N_SIG_FIGS)


def create_gain_correlation_table(
    dataset_name: str, sampling_type: str, correlation_df: Data
):
    experiment_label = (
        ExperimentTraceType.ALL.value
        if sampling_type == SamplingExperiment.TRACES.value
        else ExperimentTraceType.NONE.value
    )

    path_to_gain_df = os.path.join(PATH_TO_GAIN_INTERMEDIARY, dataset_name + ".csv")
    gain_df = pd.read_csv(path_to_gain_df)
    trace_mask = gain_df[TRANSITIVE_TRACE_TYPE_COLNAME] == experiment_label
    gain_for_trace_df = (
        gain_df[trace_mask]
        .reset_index(drop=True)
        .drop(TRANSITIVE_TRACE_TYPE_COLNAME, axis=1)
    )
    correlation_df[DATASET_COLNAME] = dataset_name
    gain_correlation_df = pd.merge(left=gain_for_trace_df, right=correlation_df)
    return gain_correlation_df
