from api.extension.experiment_types import ExperimentTraceType
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from api.technique.variationpoints.scalers.scaling_method import ScalingMethod
from api.tracer import Tracer
from experiments.create_metric_table import (
    create_direct_definition,
    create_transitive_definition,
)

best_traced_technique = "(o (MAX) (\
(. (LSI NT) (0 2))\
 ($ (SUM INDEPENDENT %f) ((. (VSM NT) (0 1)) (. (VSM NT) (1 2))))))"
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
        "10",
        tracer.get_metrics("EasyClinic", best_traced_technique % 0.1)[0].ap,
    )

    print(
        "90",
        tracer.get_metrics("EasyClinic", best_traced_technique % 0.9)[0].ap,
    )
