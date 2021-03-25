from api.constants.processing import METRIC_COLNAME
from api.tables.table import Table
from experiments.constants import (
    PATH_TO_RQ1_CORRELATION,
    PATH_TO_RQ1_GAIN,
    PATH_TO_RQ1_GAIN_CORRELATION,
    PATH_TO_RQ2_CORRELATION,
    PATH_TO_RQ2_GAIN,
    PATH_TO_RQ2_GAIN_CORRELATION,
)
from experiments.experiment import Experiment


class GainCorrelationTable(Experiment):
    """
    Joins the Gain and Correlation table for RQ1 and RQ2.
    """

    @staticmethod
    def name() -> str:
        return "gain_correlation"

    def run(self):
        rq1_correlation = Table(path_to_table=PATH_TO_RQ1_CORRELATION)
        rq2_correlation = Table(path_to_table=PATH_TO_RQ2_CORRELATION)
        rq1_gain = Table(path_to_table=PATH_TO_RQ1_GAIN)
        rq2_gain = Table(path_to_table=PATH_TO_RQ2_GAIN)

        rq1_gain_correlation = rq1_correlation + rq1_gain
        (
            rq1_gain_correlation.drop_duplicate_columns()
            .sort_cols()
            .col_values_to_upper(METRIC_COLNAME)
            .to_title_case(exclude=[METRIC_COLNAME])
            .save(PATH_TO_RQ1_GAIN_CORRELATION)
        )
        self.export_paths.append(PATH_TO_RQ1_GAIN_CORRELATION)

        rq2_gain_correlation = rq2_correlation + rq2_gain
        (
            rq2_gain_correlation.drop_duplicate_columns()
            .sort_cols()
            .col_values_to_upper(METRIC_COLNAME)
            .to_title_case(exclude=[METRIC_COLNAME])
            .save(PATH_TO_RQ2_GAIN_CORRELATION)
        )
        self.export_paths.append(PATH_TO_RQ2_GAIN_CORRELATION)
