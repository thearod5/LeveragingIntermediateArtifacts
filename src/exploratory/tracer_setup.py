import numpy as np

from api.extension.experiment_types import ExperimentTraceType
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from api.technique.variationpoints.scalers.scaling_method import ScalingMethod
from api.tracer import Tracer
from experiments.create_metric_table import (
    create_combined_definition,
    create_direct_definition,
    create_transitive_definition,
)

if __name__ == "__main__":
    tracer = Tracer()
    dataset_name = "EasyClinic"

    """
    Direct Techniques
    """
    direct_definition = create_direct_definition(AlgebraicModel.VSM)

    print(
        "DIRECT:",
        tracer.get_metrics(dataset_name, direct_definition)[0].ap,
    )

    """
    Transitive Techniques
    """
    transitive_definition = create_transitive_definition(
        AlgebraicModel.VSM,
        ScalingMethod.INDEPENDENT,
        AggregationMethod.MAX,
        ExperimentTraceType.NONE,
    )

    transitive_metrics = tracer.get_metrics(
        dataset_name, transitive_definition, summary_metrics=True
    )
    transitive_map = np.average(list(map(lambda m: m.ap, transitive_metrics)))
    print("TRANSITIVE:", transitive_map)

    """
    Combined Techniques
    """
    combined_definition = create_combined_definition(
        (
            AlgebraicModel.VSM,
            ExperimentTraceType.NONE,
            AlgebraicModel.VSM,
            ScalingMethod.INDEPENDENT,
            AggregationMethod.MAX,
            AggregationMethod.SUM,
        )
    )
    combined_map = tracer.get_metrics(dataset_name, combined_definition)[0].ap
    print("COMBINED", combined_map)
