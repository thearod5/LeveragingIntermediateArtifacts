import os

import pandas as pd
from pandas import Series
from sklearn.preprocessing import minmax_scale

from api.constants.processing import METRIC_COLNAME, Data, \
    MeltedData, CORE_METRIC_NAMES, DATASET_COLNAME, LAG_NORMALIZED_INVERTED_COLNAME, LAG_COLNAME
from api.metrics.models import format_data


def normalize_lag_scores(scores: Series, min_value=None, max_value=None):
    """

    :param scores: lag metric scores
    :param min_value: the minimum value of the application of min max scaling
    :param max_value: the maximum value of the min max scaling
    :return:
    """
    if min_value is not None and max_value is not None:
        result = minmax_scale(list(scores) + [min_value, max_value])
        return result[:-2]
    return minmax_scale(list(scores))


def normalize_invert_lag_global(scores: [float], min_value=None, max_value=None):
    return 1 - normalize_lag_scores(scores, min_value, max_value)


def create_melted_metrics(data: Data) -> MeltedData:
    metric_found = [metric for metric in CORE_METRIC_NAMES if metric in data.columns]
    other_columns = [col for col in data.columns if col not in CORE_METRIC_NAMES]
    melted_df = pd.melt(
        data,
        id_vars=other_columns,
        value_vars=metric_found,
        var_name=METRIC_COLNAME)
    return melted_df


def update_aggregate(path_to_components: str, aggregate_export_path: str):
    aggregate_df = None
    for f in os.listdir(path_to_components):
        if f[0] == ".":
            continue
        df = pd.read_csv(os.path.join(path_to_components, f))
        df[DATASET_COLNAME] = f[:-4]
        aggregate_df = df if aggregate_df is None else pd.concat([aggregate_df, df])
    aggregate_df = format_data(aggregate_df, True)
    aggregate_df.to_csv(aggregate_export_path, index=False)


def create_graph_metrics(data: Data, drop_original_lag=True):
    data = data.copy()
    data[LAG_NORMALIZED_INVERTED_COLNAME] = normalize_invert_lag_global(data[LAG_COLNAME],
                                                                        min_value=0,
                                                                        max_value=1)
    if drop_original_lag:
        data = data.drop(LAG_COLNAME, axis=1)
    return data


def setup_for_graph(data: Data, drop_original_lag=True):
    data_with_graph_metrics = create_graph_metrics(data, drop_original_lag)
    melted_df = create_melted_metrics(data_with_graph_metrics)
    return format_data(melted_df)
