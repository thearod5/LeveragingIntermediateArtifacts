from api.constants.processing import (
    RANK_COLNAME,
    TRANSITIVE_TRACE_TYPE_COLNAME,
)
from api.extension.experiment_types import ExperimentTraceType
from api.tables.metric_table import MetricTable
from api.tables.table import Table
from experiments.constants import (
    PATH_TO_BEST_RANKS,
    PATH_TO_METRIC_TABLE_AGGREGATE,
)
from experiments.experiment import Experiment


class CalculateBestRanks(Experiment):
    """
    Exports the techniques that performed the best for each dataset in each trace type
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

        best_table = rq1_aggregate.create_ranks()

        direct_mask = (
            best_table.table[TRANSITIVE_TRACE_TYPE_COLNAME]
            == ExperimentTraceType.DIRECT.value
        )

        none_mask = (
            best_table.table[TRANSITIVE_TRACE_TYPE_COLNAME]
            == ExperimentTraceType.NONE.value
        )

        best_ranks = best_table.table[
            (best_table.table[RANK_COLNAME] == 1) & (none_mask)
        ]
        best_ranks.to_csv(PATH_TO_BEST_RANKS, index=False)
        self.export_paths.append(PATH_TO_BEST_RANKS)

        return best_table

    @staticmethod
    def name() -> str:
        return "best_ranks"
