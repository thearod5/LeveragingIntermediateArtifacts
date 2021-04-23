import pandas as pd

from api.tables.metric_table import MetricTable
from api.tables.table import Table
from experiments.meta.experiment import Experiment
from utilities.constants import (
    PATH_TO_BEST_RANKS,
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
                rq1_aggregate.find_direct_best_techniques().table,
                rq1_aggregate.find_best_transitive_techniques().table,
                rq1_aggregate.find_best_hybrid_techniques().table,
            ]
        )
        best_df.to_csv(PATH_TO_BEST_RANKS, index=False)
        # best_table = rq1_aggregate.create_ranks()
        #
        # best_ranks = best_table.table[(best_table.table[RANK_COLNAME] == 1)]
        # best_ranks.to_csv(PATH_TO_BEST_RANKS, index=False)
        self.export_paths.append(PATH_TO_BEST_RANKS)

        return best_df

    @staticmethod
    def name() -> str:
        return "best_ranks"


if __name__ == "__main__":
    e = FindBestRankedTechniques()
    e.run()
    print(e.export_paths)
