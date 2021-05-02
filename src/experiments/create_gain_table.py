import os

from api.tables.metric_table import MetricTable
from api.tables.table import Table
from experiments.meta.experiment import Experiment
from utilities.constants import (
    DATASET_COLUMN_ORDER,
    PATH_TO_GAIN,
    PATH_TO_METRIC_TABLE_AGGREGATE,
    PATH_TO_RQ2_GAIN,
)
from utilities.technique_extractors import (
    get_best_direct_technique,
    get_best_hybrid_technique,
    get_best_transitive_technique,
)


def create_comparison_dict() -> dict:
    """
    Creates a dictionary containing dataset names as keys and tuples as values of the technique definition
    of the best direct and hybrid techniques. This dictionary can be used to calculate the gain between
    techniques within metric tables.
    :return:
    """
    comparison_dict = {}
    for dataset in DATASET_COLUMN_ORDER:
        comparison_dict.update(
            {
                dataset: (
                    get_best_direct_technique(dataset),
                    get_best_hybrid_technique(dataset),
                )
            }
        )
    return comparison_dict


def create_comparison_dict_transitive() -> dict:
    """
    Creates a dictionary containing dataset names as keys and tuples as values of the technique definition
    of the best direct and hybrid techniques. This dictionary can be used to calculate the gain between
    techniques within metric tables.
    :return:
    """
    comparison_dict = {}
    for dataset in DATASET_COLUMN_ORDER:
        comparison_dict.update(
            {
                dataset: (
                    get_best_direct_technique(dataset),
                    get_best_transitive_technique(dataset),
                )
            }
        )
    return comparison_dict


def create_comparison_dict_hybrid_over_transitive() -> dict:
    """
    Creates a dictionary containing dataset names as keys and tuples as values of the technique definition
    of the best direct and hybrid techniques. This dictionary can be used to calculate the gain between
    techniques within metric tables.
    :return:
    """
    comparison_dict = {}
    for dataset in DATASET_COLUMN_ORDER:
        comparison_dict.update(
            {
                dataset: (
                    get_best_transitive_technique(dataset),
                    get_best_hybrid_technique(dataset),
                )
            }
        )
    return comparison_dict


class CalculateGain(Experiment):
    """
    Creates two tables representing:
    * Gain on direct best when leveraging intermediate artifacts
    * Gain on direct best when leveraging intermediate traces
    """

    def run(self) -> Table:
        agg_metric_table = MetricTable(path_to_table=PATH_TO_METRIC_TABLE_AGGREGATE)
        H_PATH = os.path.join(PATH_TO_GAIN, "hybrid_over_direct.csv")
        hybrid_gain_table = (
            agg_metric_table.calculate_gain_between_techniques(create_comparison_dict())
            .sort(DATASET_COLUMN_ORDER)
            .save(H_PATH)
        )

        T_PATH = os.path.join(PATH_TO_GAIN, "transitive_over_direct.csv")
        transitive_gain_table = (
            agg_metric_table.calculate_gain_between_techniques(
                create_comparison_dict_transitive()
            )
            .sort(DATASET_COLUMN_ORDER)
            .save(T_PATH)
        )

        H_OVER_T_PATH = os.path.join(PATH_TO_GAIN, "hybrid_over_transitive.csv")
        hybrid_over_transitive_gain = (
            agg_metric_table.calculate_gain_between_techniques(
                create_comparison_dict_hybrid_over_transitive()
            )
            .sort(DATASET_COLUMN_ORDER)
            .save(H_OVER_T_PATH)
        )

        self.export_paths.append(H_PATH)
        self.export_paths.append(T_PATH)
        self.export_paths.append(H_OVER_T_PATH)

        # rq2_gain_df.save(PATH_TO_RQ2_GAIN)
        self.export_paths.append(PATH_TO_RQ2_GAIN)
        return agg_metric_table

    @staticmethod
    def name() -> str:
        return "gain_table"


if __name__ == "__main__":
    e = CalculateGain()
    e.run()
    print(e.export_paths)
    print("Done")
