from api.constants.processing import LAG_NORMALIZED_INVERTED_COLNAME, METRIC_COLNAME
from api.tables.table import Table
from experiments.meta.experiment import Experiment
from utilities.constants import (
    DATASET_COLUMN_ORDER,
    PATH_TO_RQ1_CORRELATION,
    PATH_TO_RQ1_GAIN,
    PATH_TO_RQ1_GAIN_CORRELATION,
    PATH_TO_RQ2_CORRELATION,
    PATH_TO_RQ2_GAIN,
    PATH_TO_RQ2_GAIN_CORRELATION,
)


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

        rq1_gain.table[METRIC_COLNAME] = rq1_gain.table[METRIC_COLNAME].apply(
            lambda c: "lag" if c == LAG_NORMALIZED_INVERTED_COLNAME else c
        )
        rq1_correlation.table[METRIC_COLNAME] = rq1_correlation.table[
            METRIC_COLNAME
        ].apply(lambda c: "lag" if c == LAG_NORMALIZED_INVERTED_COLNAME else c)

        rq1_gain_correlation = rq1_correlation + rq1_gain

        (
            rq1_gain_correlation.drop_duplicate_columns()
            .sort(DATASET_COLUMN_ORDER)
            .col_values_to_upper(METRIC_COLNAME)
            .to_title_case(exclude=[METRIC_COLNAME])
            .round()
            .save(PATH_TO_RQ1_GAIN_CORRELATION)
        )
        self.export_paths.append(PATH_TO_RQ1_GAIN_CORRELATION)

        rq2_gain_correlation = rq2_correlation + rq2_gain
        (
            rq2_gain_correlation.drop_duplicate_columns()
            .sort(DATASET_COLUMN_ORDER)
            .col_values_to_upper(METRIC_COLNAME)
            .to_title_case(exclude=[METRIC_COLNAME])
            .round()
            .save(PATH_TO_RQ2_GAIN_CORRELATION)
        )
        self.export_paths.append(PATH_TO_RQ2_GAIN_CORRELATION)


if __name__ == "__main__":
    e = GainCorrelationTable()
    e.run()
    print(e.export_paths)
    print("Done")
