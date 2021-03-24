"""
This script calculates the precision at a given recall level for some dataset.
This is used to compare our technique against other studies who used different
metrics.
"""

import pandas as pd
from api.technique.variationpoints.scalers.ScalingMethod import ScalingMethod
from sklearn.metrics import precision_recall_curve

from api.extension.experiment_types import ExperimentTraceType
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from api.tracer import Tracer
from experiments.calculate_metric_table import create_combined_definition

if __name__ == "__main__":
    dataset_name = "EasyClinic"
    technique_name = create_combined_definition(
        AlgebraicModel.VSM,
        AlgebraicModel.VSM,
        ScalingMethod.INDEPENDENT,
        AggregationMethod.MAX,
        AggregationMethod.SUM,
        ExperimentTraceType.NONE,
    )

    # get technique similarity values
    tracer = Tracer()
    technique_data = tracer.get_technique_data(dataset_name, technique_name)
    scoring_table = technique_data.get_scoring_table()
    scores = scoring_table.values
    precision, recall, thresholds = precision_recall_curve(
        probas_pred=scores[:, 0], y_true=scores[:, 1], pos_label=1
    )

    # Create result technique_data frame
    metrics_df = pd.DataFrame()
    metrics_df["precision"] = precision
    metrics_df["recall"] = recall
    metrics_df["thresholds"] = list(thresholds) + [0]
    metrics_df.to_csv("metrics.csv", index=False)

    # get precision at some level or higher
    recall_value = 0.72
    recall_delta = 0.01
    above_base = metrics_df["recall"] <= recall_value + recall_delta
    below_base = metrics_df["recall"] >= recall_value

    print(metrics_df[above_base & below_base]["precision"].max())
