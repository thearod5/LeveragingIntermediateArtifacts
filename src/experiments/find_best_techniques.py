"""
The following module will calculate the best and worst hybrid techniques and print out the latex
row values.
"""
import pandas as pd

from api.constants.processing import (
    BEST_TECHNIQUE_AGGREGATE_METRICS,
    DATASET_COLNAME,
    TECHNIQUE_TYPE_COLNAME,
)
from api.constants.techniques import HYBRID_ID
from api.tables.metric_table import MetricTable
from api.tables.table import Table
from experiments.meta.experiment import Experiment
from utilities.constants import (
    DATASET_COLUMN_ORDER,
    PATH_TO_METRIC_TABLE_AGGREGATE,
)


class FindBestRankedTechniques(Experiment):
    """
    Exports the techniques that performed the best for each dataset and trace type
    """

    def run(self) -> Table:
        """
        Calculates percent best on the aggregate metric table.

        :exports:
            1. rq1 best
            2. aggregate best (includes RQ1 and RQ2)
        :return: Table - aggregate best table
        """

        # Read aggregate metric table
        rq1_aggregate = MetricTable(path_to_table=PATH_TO_METRIC_TABLE_AGGREGATE)
        best_df = pd.concat(
            [
                rq1_aggregate.find_best_direct_techniques().table,
                rq1_aggregate.find_best_transitive_techniques().table,
                rq1_aggregate.find_best_hybrid_techniques().table,
            ]
        )
        worst_df = pd.concat(
            [
                rq1_aggregate.find_worst_direct_techniques().table,
                rq1_aggregate.find_worst_transitive_techniques().table,
                rq1_aggregate.find_worst_hybrid_techniques().table,
            ]
        )

        for title, df in [("name", best_df), ("worst", worst_df)]:
            print(f"{title}-----------")
            for i in range(len(df)):
                entry = df.iloc[i]
                print(
                    "%20s %10s %10s"
                    % (entry["dataset"], entry["technique_type"], entry["name"])
                )

        def get_latex_row(data_df):
            metric_values = []
            for dataset_name in DATASET_COLUMN_ORDER:
                dataset_entries = data_df[
                    (data_df[DATASET_COLNAME] == dataset_name)
                    & (data_df[TECHNIQUE_TYPE_COLNAME] == HYBRID_ID)
                ]
                entry = dataset_entries.iloc[0]
                for metric_name in BEST_TECHNIQUE_AGGREGATE_METRICS:
                    metric_value = entry[metric_name]
                    metric_values.append(str(round(metric_value, 3)))
            return "&".join(metric_values)

        best_row = get_latex_row(best_df)
        print("-" * 50)
        worst_row = get_latex_row(worst_df)

        print("BEST:", best_row)
        print("WORST:", worst_row)

    @staticmethod
    def name() -> str:
        return "best_techniques"


if __name__ == "__main__":
    e = FindBestRankedTechniques()
    e.run()
