from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from api.tracer import Tracer
from experiments.create_metric_table import (
    create_direct_definition,
)
from experiments.create_sampled_table import get_best_no_trace_sampled_technique

if __name__ == "__main__":
    tracer = Tracer()
    dataset_name = "WARC"

    """
    Direct Techniques
    """
    direct_definition = create_direct_definition(AlgebraicModel.VSM)

    # print(
    #     "DIRECT:",
    #     tracer.get_metrics(dataset_name, direct_definition)[0].ap,
    # )
    #
    # """
    # Transitive Techniques
    # """
    # transitive_definition = create_transitive_definition(
    #     AlgebraicModel.VSM,
    #     ScalingMethod.INDEPENDENT,
    #     AggregationMethod.MAX,
    #     ExperimentTraceType.NONE,
    # )
    #
    # transitive_metrics = tracer.get_metrics(
    #     dataset_name, transitive_definition, summary_metrics=True
    # )
    # transitive_map = np.average(list(map(lambda m: m.ap, transitive_metrics)))
    # print("TRANSITIVE:", transitive_map)

    # """
    # Combined Techniques
    # """
    # combined_definition = create_combined_definition(
    #     (
    #         AlgebraicModel.VSM,
    #         ExperimentTraceType.NONE,
    #         AlgebraicModel.VSM,
    #         ScalingMethod.INDEPENDENT,
    #         AggregationMethod.MAX,
    #         AggregationMethod.SUM,
    #     )
    # )
    # combined_map = tracer.get_metrics(dataset_name, combined_definition)[0].ap
    # print("COMBINED", combined_map)

    """
    SAMPLED
    """
    sampled_combined_definition = get_best_no_trace_sampled_technique(dataset_name) % 1
    sampled_ap = sampled_technique_data = tracer.get_metrics(
        dataset_name, sampled_combined_definition
    )[0].ap
    print("SAMPLED AP:", sampled_ap)
