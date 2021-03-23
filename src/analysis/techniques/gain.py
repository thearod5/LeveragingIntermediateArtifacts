import itertools
import os

import pandas as pd

from api.constants.paths import PATH_TO_GAIN_PROCESSED, PATH_TO_GAIN_INTERMEDIARY, PATH_TO_TECHNIQUE_SOURCE_DATA
from api.constants.processing import DATASET_COLNAME, METRIC_COLNAME, LAG_COLNAME, \
    LAG_NORMALIZED_COLNAME, Data, TRANSITIVE_TRACE_TYPE_COLNAME, Scores, RELATIVE_GAIN_COLNAME, VALUE_COLNAME, \
    N_SIG_FIGS
from src.analysis.common_operations import create_melted_metrics, update_aggregate
from src.runner.types import ExperimentTraceType

inverted_metrics = [LAG_COLNAME, LAG_NORMALIZED_COLNAME]


def calculate_gain(new_value, old_value, inverted=False):
    if inverted:
        return (old_value - new_value) / old_value
    return (new_value - old_value) / old_value


def calculate_gain_for_scores(scores: Scores, base_value: float, inverted: bool):
    return scores.apply(lambda score: calculate_gain(score, base_value, inverted))


def calculate_gain_for_source(data: Data):
    id_columns = [DATASET_COLNAME, TRANSITIVE_TRACE_TYPE_COLNAME]
    ids_unique_values = [list(data[col].unique()) for col in id_columns]

    melted_df = create_melted_metrics(data)
    metrics = melted_df[METRIC_COLNAME].unique()

    result = pd.DataFrame(
        columns=id_columns + [METRIC_COLNAME, RELATIVE_GAIN_COLNAME])
    for dataset, trace_type, metric_name in itertools.product(ids_unique_values[0], ids_unique_values[1], metrics):
        dataset_metric_query = melted_df[(melted_df[DATASET_COLNAME] == dataset) &
                                         (melted_df[METRIC_COLNAME] == metric_name)]
        baseline_values = \
            dataset_metric_query[
                dataset_metric_query[TRANSITIVE_TRACE_TYPE_COLNAME] == ExperimentTraceType.DIRECT.value][
                VALUE_COLNAME]
        query_df = dataset_metric_query[dataset_metric_query[TRANSITIVE_TRACE_TYPE_COLNAME] == trace_type]

        is_inverted = metric_name in inverted_metrics
        baseline_value = min(baseline_values) if is_inverted else max(baseline_values)
        experiment_value = query_df[VALUE_COLNAME]
        gain_values = calculate_gain_for_scores(experiment_value, baseline_value, is_inverted)

        assert len(gain_values) > 0
        max_gain = round(max(gain_values), N_SIG_FIGS)
        result = result.append({
            DATASET_COLNAME: dataset,
            TRANSITIVE_TRACE_TYPE_COLNAME: trace_type,
            METRIC_COLNAME: metric_name,
            RELATIVE_GAIN_COLNAME: max_gain
        }, ignore_index=True)
    return result


def export_gain(source_data: Data, dataset_name: str):
    gain_df = calculate_gain_for_source(source_data)
    export_path = os.path.join(PATH_TO_GAIN_INTERMEDIARY, dataset_name + ".csv")
    gain_df.to_csv(export_path, index=False)
    update_aggregate(PATH_TO_GAIN_INTERMEDIARY, os.path.join(PATH_TO_GAIN_PROCESSED, "Gain.csv"))
    print("Gain technique_data exported to: %s" % export_path)


if __name__ == "__main__":
    dataset_names = ["EasyClinic", "Drone", "TrainController", "WARC", "EBT"]
    for dataset_name in dataset_names:
        df = pd.read_csv(os.path.join(PATH_TO_TECHNIQUE_SOURCE_DATA, dataset_name + '.csv'))
        export_gain(df, dataset_name)
