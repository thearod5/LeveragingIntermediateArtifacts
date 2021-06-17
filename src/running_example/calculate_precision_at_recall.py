"""
This script calculates the precision at a given recall level for some dataset.
This is used to compare our technique against other studies who used different
metrics.
"""

import pandas as pd
from sklearn.metrics import precision_recall_curve

from api.extension.experiment_types import ExperimentTraceType
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from api.technique.variationpoints.scalers.scaling_method import ScalingMethod
from api.tracer import Tracer
from experiments.create_metric_table import create_transitive_definition

if __name__ == "__main__":
    dataset_name = "EasyClinic"
    # technique_id: TechniqueID = (
    #     # AlgebraicModel.VSM,
    #     #  ExperimentTraceType.NONE,
    #     AlgebraicModel.VSM,
    #     ScalingMethod.INDEPENDENT,
    #     AggregationMethod.MAX,
    #     ExperimentTraceType.NONE,
    #     # AggregationMethod.SUM,
    # )
    technique_name = create_transitive_definition(
        AlgebraicModel.VSM,
        ScalingMethod.INDEPENDENT,
        AggregationMethod.MAX,
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
    recall_value = 0.165
    recall_delta = 0.01
    above_base = metrics_df["recall"] <= recall_value + recall_delta
    below_base = metrics_df["recall"] >= recall_value - recall_delta

    print("Recall: ", metrics_df[above_base & below_base]["recall"].mean())
    print("Precision: ", metrics_df[above_base & below_base]["precision"].mean())
