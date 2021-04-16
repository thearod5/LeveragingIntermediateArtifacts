from experiments.meta.experiment import Experiment
from utilities.constants import DATASET_COLUMN_ORDER

combined_direct = ""


class CompareTechniques(Experiment):
    """
    The following experiment compares the accuracy of the best combined technique and the combined
    direct technique
    """

    def run(self):
        for dataset_name in DATASET_COLUMN_ORDER:
            print("delete me")

    @staticmethod
    def name() -> str:
        return "compare_techniques"
