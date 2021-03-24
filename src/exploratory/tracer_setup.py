import numpy as np

from api.extension.experiment_types import ExperimentTraceType
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from api.technique.variationpoints.scalers.scaling_method import ScalingMethod
from api.tracer import Tracer
from experiments.calculate_metric_table import (
    create_direct_definition,
    create_transitive_definition,
)

if __name__ == "__main__":
    tracer = Tracer()

    direct_definition = create_direct_definition(AlgebraicModel.VSM)
    transitive_definition = create_transitive_definition(
        AlgebraicModel.VSM,
        ScalingMethod.INDEPENDENT,
        AggregationMethod.MAX,
        ExperimentTraceType.NONE,
    )

    print(
        "DIRECT:",
        tracer.get_metrics("EasyClinic", direct_definition)[0].ap,
    )

    transitive_metrics = tracer.get_metrics(
        "EasyClinic", transitive_definition, summary_metrics=True
    )
    transitive_map = np.average(list(map(lambda m: m.ap, transitive_metrics)))
    print(len(transitive_metrics), "TRANSITIVE (MULTI):", transitive_map)

    transitive_metrics = tracer.get_metrics(
        "EasyClinic", transitive_definition, summary_metrics=False
    )
    print(len(transitive_metrics), "TRANSITIVE (SINGLE):", transitive_metrics[0].ap)
