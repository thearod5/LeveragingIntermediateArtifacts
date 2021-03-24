from api.tables.metric_table import MetricTable
from api.tables.table import Table
from experiments.constants import PATH_TO_GAIN_AGGREGATE, PATH_TO_METRIC_TABLE_AGGREGATE
from experiments.experiment import Experiment


class CalculateGain(Experiment):
    """
    Creates a table
    """

    def run(self) -> Table:
        rq1_aggregate = MetricTable(path_to_table=PATH_TO_METRIC_TABLE_AGGREGATE)
        best_table = rq1_aggregate.calculate_gain()
        best_table.sort_cols().save(PATH_TO_GAIN_AGGREGATE)
        return best_table

    @property
    def description(self) -> str:
        return "Calculates the maximum gain per trace type"

    @staticmethod
    def name() -> str:
        return "gain_table"
