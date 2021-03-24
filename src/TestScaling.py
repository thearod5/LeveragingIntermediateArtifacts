"""
This script calculates the precision at a given recall level for some dataset.
This is used to compare our technique against other studies who used different
metrics.
"""

from api.technique.variationpoints.algebraicmodel.AlgebraicModel import AlgebraicModel
from api.technique.variationpoints.scalers.ScalingMethod import ScalingMethod

from api.extension.experiment_types import ExperimentTraceType
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.tracer import Tracer
from experiments.calculate_metric_table import create_transitive_definition

if __name__ == "__main__":
    dataset_name = "TrainController"
    t1 = create_transitive_definition(
        AlgebraicModel.VSM,
        ScalingMethod.INDEPENDENT,
        AggregationMethod.MAX,
        ExperimentTraceType.NONE,
    )
    t2 = create_transitive_definition(
        AlgebraicModel.VSM,
        ScalingMethod.GLOBAL,
        AggregationMethod.MAX,
        ExperimentTraceType.NONE,
    )

    technique_names = [t1, t2]

    # get technique similarity values
    tracer = Tracer()

    for t_name in technique_names:
        metrics = tracer.get_metrics(dataset_name, t_name)
        print("MAP:", metrics.ap)
        print("AUC:", metrics.auc)
