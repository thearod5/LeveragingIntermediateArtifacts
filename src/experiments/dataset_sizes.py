"""
The following experiment calculates the size of each dataset along various dimensions including:
1. number of artifacts
2. number of relations between artifacts
3. percentage of relations which are trace links
"""
import os

import pandas as pd

from api.constants.processing import N_SIG_FIGS
from api.datasets.dataset import Dataset
from api.tables.table import Table
from experiments.meta.experiment import Experiment
from utilities.constants import DATASET_COLUMN_ORDER, PATH_TO_AGGREGATE_TABLES

EXPORT_PATH = os.path.join(PATH_TO_AGGREGATE_TABLES, "dataset_sizes.csv")

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

EXPERIMENT_NAME = "dataset_sizes"


class DatasetSizes(Experiment):
    """
    The following module calculates the number of artifacts, relations between artifacts, and percentage of relations
    which are trace links.
    """

    def run(self) -> Table:
        """
        Iterates through
        :return:
        """
        columns = [
            DATASET_NAME,
            DIRECT_PATHS,
            DIRECT_TRACES,
            UPPER_PATHS,
            UPPER_TRACES,
            LOWER_PATHS,
            LOWER_TRACES,
        ]
        data = pd.DataFrame(columns=columns)
        for dataset_name in DATASET_COLUMN_ORDER:
            dataset = Dataset(dataset_name)
            n_top = len(dataset.artifacts[0])
            n_middle = len(dataset.artifacts[1])
            n_bottom = len(dataset.artifacts[2])

            def stat_matrix(matrix):
                n_traces = matrix.sum(axis=1).sum()
                n_paths = matrix.shape[0] * matrix.shape[1]
                return n_paths, n_traces

            d_paths, n_direct_traces = stat_matrix(dataset.traced_matrices["0-2"])
            u_paths, n_upper_traces = stat_matrix(dataset.traced_matrices["0-1"])
            l_paths, n_lower_traces = stat_matrix(dataset.traced_matrices["1-2"])

            entry = {
                DATASET_NAME: dataset_name,
                DIRECT_PATHS: d_paths,
                DIRECT_TRACES: n_direct_traces,
                UPPER_PATHS: u_paths,
                UPPER_TRACES: n_upper_traces,
                LOWER_PATHS: l_paths,
                LOWER_TRACES: n_lower_traces,
            }
            data = data.append(entry, ignore_index=True)
        post_df = data.sort_values(by=DIRECT_TRACES)

        post_df = post_df.round(N_SIG_FIGS)
        post_df.to_csv(EXPORT_PATH, index=False)
        self.export_paths.append(EXPORT_PATH)
        return Table()

    @staticmethod
    def name() -> str:
        return EXPERIMENT_NAME


if __name__ == "__main__":
    DatasetSizes().run()
