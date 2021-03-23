import os

import pandas as pd

from api.constants.paths import PATH_TO_DATASET_SIZES_DATA
from api.constants.processing import n_sig_figs
from api.datasets.dataset import Dataset

EXPORT_PATH = os.path.join(PATH_TO_DATASET_SIZES_DATA, "DatasetSizes.csv")

DATASET_NAME = "Dataset"
TOP_NAME = "Top"
MIDDLE_NAME = "Middle"
BOTTOM_NAME = "Bottom"
DIRECT_PATHS = "Direct Paths"
DIRECT_TRACES = "Direct Traces"
UPPER_PATHS = "Upper Paths"
UPPER_TRACES = "Upper Traces"
LOWER_PATHS = "Lower Paths"
LOWER_TRACES = "Lower Traces"

if __name__ == "__main__":
    datasets = ["EasyClinic", "EBT", "Drone", "TrainController", "WARC"]
    columns = [DATASET_NAME, TOP_NAME, MIDDLE_NAME, BOTTOM_NAME,
               DIRECT_PATHS, DIRECT_TRACES, UPPER_PATHS, UPPER_TRACES,
               LOWER_PATHS, LOWER_TRACES]
    data = pd.DataFrame(columns=columns)
    for dataset_name in datasets:
        dataset = Dataset(dataset_name)
        n_top = len(dataset.artifacts.levels[0])
        n_middle = len(dataset.artifacts.levels[1])
        n_bottom = len(dataset.artifacts.levels[2])


        def stat_matrix(matrix):
            n_traces = matrix.sum(axis=1).sum()
            n_paths = (matrix.shape[0] * matrix.shape[1])
            percent_traced = n_traces / n_paths
            return n_paths, percent_traced


        d_paths, d_percent = stat_matrix(dataset.traced_matrices["0-2"])
        u_paths, u_percent = stat_matrix(dataset.traced_matrices["0-1"])
        l_paths, l_percent = stat_matrix(dataset.traced_matrices["1-2"])

        entry = {
            DATASET_NAME: dataset_name,
            TOP_NAME: n_top,
            MIDDLE_NAME: n_middle,
            BOTTOM_NAME: n_bottom,
            DIRECT_PATHS: d_paths,
            DIRECT_TRACES: d_percent,
            UPPER_PATHS: u_paths,
            UPPER_TRACES: u_percent,
            LOWER_PATHS: l_paths,
            LOWER_TRACES: l_percent,
        }
        data = data.append(entry, ignore_index=True)

    post_df = data.sort_values(by=DIRECT_TRACES)
    for n_col in list(filter(lambda c: 'paths' in c.lower(), post_df.columns)):
        post_df[n_col] = post_df[n_col].apply(lambda n: f'{n:,}')
    for p_col in list(filter(lambda c: 'traces' in c.lower(), post_df.columns)):
        post_df[p_col] = post_df[p_col].apply(lambda p: repr(round(p * 100, 1)) + "\%")
    post_df = post_df.round(n_sig_figs)
    post_df.to_csv(EXPORT_PATH, index=False, sep=';')