from api.tables.metric_table import MetricTable
from api.tables.table import Table
from experiments.meta.experiment import Experiment
from utilities.constants import (
    PATH_TO_METRIC_TABLE_AGGREGATE,
    PATH_TO_RQ1_GAIN,
    PATH_TO_RQ2_GAIN,
)
from utilities.technique_extractors import create_comparison_dict


class CalculateGain(Experiment):
    """
    Creates two tables representing:
    * Gain on direct best when leveraging intermediate artifacts
    * Gain on direct best when leveraging intermediate traces
    """

    def run(self) -> Table:
        agg_metric_table = MetricTable(path_to_table=PATH_TO_METRIC_TABLE_AGGREGATE)

        gain_table = agg_metric_table.calculate_gain_between_techniques(
            create_comparison_dict()
        )

        gain_table.melt_metrics(metric_value_col_name="relative_gain").save(
            PATH_TO_RQ1_GAIN
        )
        self.export_paths.append(PATH_TO_RQ1_GAIN)

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
