from api.constants.processing import (
    ALGEBRAIC_MODEL_COLNAME,
    DIRECT_ALGEBRAIC_MODEL_COLNAME,
    TECHNIQUE_AGGREGATION_COLNAME,
    TECHNIQUE_TYPE_COLNAME,
    TRANSITIVE_AGGREGATION_COLNAME,
    TRANSITIVE_SCALING_COLNAME,
    TRANSITIVE_TRACE_TYPE_COLNAME,
    TRANSITIVE_TRACE_TYPE_ORDER,
    VARIATION_POINT_COLNAME,
)
from api.constants.techniques import HYBRID_ID
from api.extension.experiment_types import ExperimentTraceType
from api.tables.metric_table import MetricTable
from api.tables.table import Table
from experiments.meta.experiment import Experiment
from utilities.constants import (
    DATASET_COLUMN_ORDER,
    PATH_TO_BEST_AGGREGATE,
    PATH_TO_METRIC_TABLE_AGGREGATE,
    PATH_TO_RQ1_BEST,
)


class CreateBestTechnique(Experiment):
    """
    Represents the experiment to update the best tables
    """

    variation_point_order = [
        TECHNIQUE_TYPE_COLNAME,
        DIRECT_ALGEBRAIC_MODEL_COLNAME,
        ALGEBRAIC_MODEL_COLNAME,
        TRANSITIVE_SCALING_COLNAME,
        TRANSITIVE_AGGREGATION_COLNAME,
        TECHNIQUE_AGGREGATION_COLNAME,
    ]

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

        best_table = (
            rq1_aggregate.calculate_percent_best()
            .sort(DATASET_COLUMN_ORDER)
            .to_categorical(
                VARIATION_POINT_COLNAME, col_value_order=self.variation_point_order
            )
            .to_categorical(
                TRANSITIVE_TRACE_TYPE_COLNAME,
                col_value_order=TRANSITIVE_TRACE_TYPE_ORDER,
            )
            .sort_values(
                group_names=[TRANSITIVE_TRACE_TYPE_COLNAME, VARIATION_POINT_COLNAME],
                axis=0,
            )
            .sort(DATASET_COLUMN_ORDER)
        )

        # export rq1 best
        hybrid_query = best_table.table[TECHNIQUE_TYPE_COLNAME] == HYBRID_ID
        none_traced_query = (
            best_table.table[TRANSITIVE_TRACE_TYPE_COLNAME]
            == ExperimentTraceType.NONE.value
        )
        Table(
            best_table.table[hybrid_query & none_traced_query].drop(
                [TECHNIQUE_TYPE_COLNAME, TRANSITIVE_TRACE_TYPE_COLNAME], axis=1
            )
        ).to_title_case(exclude=["technique"]).format_percents_for_latex(
            to_int=True
        ).save(
            PATH_TO_RQ1_BEST
        )
        self.export_paths.append(PATH_TO_RQ1_BEST)

        # export aggregate
        best_table.to_title_case(exclude=["technique"]).format_percents_for_latex(
            to_int=True
        ).save(PATH_TO_BEST_AGGREGATE)
        self.export_paths.append(PATH_TO_BEST_AGGREGATE)

        return best_table

    @staticmethod
    def name() -> str:
        return "best_table"
