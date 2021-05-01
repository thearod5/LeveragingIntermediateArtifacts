"""
This script is used to clean a dataset's artifacts and create the trace matrices between them.
Both artifacts and trace matrices are formatted in standardized order following:
"""
from api.datasets.builder.dataset_builder import DatasetBuilder
from api.tables.table import Table
from experiments.meta.experiment import Experiment
from utilities.constants import DATASET_COLUMN_ORDER
from utilities.progress_bar_factory import create_loading_bar

EXPERIMENT_NAME = "create_datasets"


class CreateDatasets(Experiment):
    def run(self) -> Table:
        with create_loading_bar(
            EXPERIMENT_NAME, DATASET_COLUMN_ORDER, len(DATASET_COLUMN_ORDER)
        ) as d_iterable:
            for dataset_name in d_iterable:
                builder = DatasetBuilder(dataset_name)
                builder.build()
                builder.export()
                print(f"{dataset_name} exported.")
        return Table()

    @staticmethod
    def name() -> str:
        return EXPERIMENT_NAME


if __name__ == "__main__":
    CreateDatasets().run()
    print("Done!")
