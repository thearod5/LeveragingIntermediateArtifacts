"""
This script is used to clean a dataset's artifacts, create their trace technique_matrices,
and setup the structure needed to run our src on it.
"""
from api.datasets.builder.dataset_builder import DatasetBuilder
from api.datasets.builder.dataset_exporter import export_dataset

datasets = ["EasyClinic", "Drone", "TrainController", "EBT", "WARC"]  # the name of the datasets to build

if __name__ == "__main__":
    for dataset_name in datasets:
        builder = DatasetBuilder(dataset_name, create=True)
        export_dataset(builder)
    print("Done!")
