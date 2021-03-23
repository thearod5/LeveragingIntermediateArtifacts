import os
from collections import Iterable

import pandas as pd

from api.constants.paths import PATH_TO_BEST_INTERMEDIARY, PATH_TO_BEST_PROCESSED
from api.constants.processing import DATASET_COLNAME, AP_COLNAME, RANK_COLNAME, TRANSITIVE_TRACE_TYPE_COLNAME, \
    META_COLS, PERCENT_BEST_COLNAME, \
    TECHNIQUE_COLNAME, VARIATION_POINT_COLNAME, Data, ALL_METRIC_NAMES
from api.metrics.models import format_data
from src.analysis.common_operations import update_aggregate


def create_ranks(data: Data) -> Data:
    """
    For each dataset and trace type, create ranks with 1 corresponding to highest map score
    :param data: dataframe containing cols: dataset, transitive_trace_type
    :return:
    """
    data = data.copy()
    aggregated_rank_df = None

    for name, values in data.groupby([DATASET_COLNAME, TRANSITIVE_TRACE_TYPE_COLNAME]):
        values[RANK_COLNAME] = values[AP_COLNAME].rank(method="dense", ascending=False)
        if aggregated_rank_df is None:
            aggregated_rank_df = values
        else:
            aggregated_rank_df = pd.concat([aggregated_rank_df, values], ignore_index=True)
    return format_data(aggregated_rank_df)


def is_array(thing):
    return isinstance(thing, Iterable)


def create_percent_best(data: Data) -> Data:
    ignore_columns = ALL_METRIC_NAMES + META_COLS + [RANK_COLNAME]
    variation_points = [col for col in data.columns if col not in ignore_columns]
    data = data.copy()
    percent_best_df = pd.DataFrame()
    n_datasets = len(data[DATASET_COLNAME].unique())

    for variation_point in variation_points:  # ex: NLPType
        for (trace_type, vp_technique), group_data in data.groupby([TRANSITIVE_TRACE_TYPE_COLNAME, variation_point]):
            best_rank_query = group_data[group_data[RANK_COLNAME] == 1]
            vp_freq = len(best_rank_query[DATASET_COLNAME].unique()) / n_datasets
            new_record = {
                TRANSITIVE_TRACE_TYPE_COLNAME: trace_type,
                VARIATION_POINT_COLNAME: variation_point,
                TECHNIQUE_COLNAME: vp_technique,
                PERCENT_BEST_COLNAME: vp_freq
            }
            percent_best_df = percent_best_df.append(new_record, ignore_index=True)

    return format_data(percent_best_df)


def export_best_techniques(source_data: Data, export_name: str):
    with_ranks = create_ranks(source_data)
    best_df = create_percent_best(with_ranks)
    export_path = os.path.join(PATH_TO_BEST_INTERMEDIARY, export_name + ".csv")
    best_df.to_csv(export_path, index=False)
    update_aggregate(PATH_TO_BEST_INTERMEDIARY, os.path.join(PATH_TO_BEST_PROCESSED, "Best.csv"))
    print("Exported best technique to: %s" % export_path)
