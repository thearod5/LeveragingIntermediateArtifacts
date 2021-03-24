from api.tables.metric_table import MetricTable
from api.tables.table import Table
from experiments.constants import PATH_TO_BEST_AGGREGATE, PATH_TO_METRIC_TABLE_AGGREGATE
from experiments.experiment import Experiment


class CreateBestTechnique(Experiment):
    """
    Represents the experiment to update the best tables
    """

    def run(self) -> Table:
        rq1_aggregate = MetricTable(path_to_table=PATH_TO_METRIC_TABLE_AGGREGATE)
        best_table = rq1_aggregate.calculate_percent_best()
        best_table.sort_cols().save(PATH_TO_BEST_AGGREGATE)
        return best_table

    @property
    def description(self) -> str:
        return "Updates the best.csv table."

    @staticmethod
    def name() -> str:
        return "best_table"
