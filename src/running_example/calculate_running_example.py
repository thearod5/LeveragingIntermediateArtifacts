"""
This script finds the source, target, and transitive artifacts
in which a direct technique most benefits from the transitive relation score.

The following questions are answered:

-> What n transitive artifacts helped the most?
-> Why did they help?
-> How much did they help?
"""
import pandas as pd
from api.technique.variationpoints.scalers.ScalingMethod import ScalingMethod

from api.constants.processing import n_sig_figs
from api.datasets.dataset import Dataset
from api.technique.definitions.combined.technique import CombinedTechniqueData
from api.technique.definitions.transitive.calculator import TransitiveTechniqueData
from api.technique.variationpoints.aggregation.aggregation_method import AggregationMethod
from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from api.tracer import Tracer
from src.runner.types import ExperimentTraceType
from src.techniques import retrieval_techniques

if __name__ == "__main__":
    dataset_name = "Drone"

    # techniques
    direct_am = AlgebraicModel.VSM
    transitive_am = AlgebraicModel.VSM
    transitive_scaling = ScalingMethod.INDEPENDENT
    transitive_aggregation = AggregationMethod.MAX
    technique_aggregation = AggregationMethod.MAX
    trace_type = ExperimentTraceType.NONE
    n_top_intermediate_artifacts = 3

    # get technique similarity values
    tracer = Tracer()

    # direct technique
    direct_technique_name = retrieval_techniques.format_direct_technique(direct_am)
    direct_technique_data = tracer.get_technique_data(dataset_name, direct_technique_name)
    direct_scoring_table = direct_technique_data.get_scoring_table()
    direct_scores = direct_scoring_table.values

    # transitive technique
    transitive_technique_name = retrieval_techniques.format_transitive_technique(transitive_am,
                                                                                 transitive_scaling,
                                                                                 transitive_aggregation,
                                                                                 trace_type)
    transitive_technique_data: TransitiveTechniqueData = tracer.get_technique_data(dataset_name,
                                                                                   transitive_technique_name)
    transitive_scoring_table = transitive_technique_data.get_scoring_table()
    transitive_scores = transitive_scoring_table.values

    # combined technique
    combined_technique_name = retrieval_techniques.format_combined_technique(direct_am,
                                                                             transitive_am,
                                                                             transitive_scaling,
                                                                             transitive_aggregation,
                                                                             technique_aggregation,
                                                                             trace_type)
    combined_technique_data: CombinedTechniqueData = tracer.get_technique_data(dataset_name, combined_technique_name)
    combined_scoring_table = combined_technique_data.get_scoring_table()
    combined_scores = combined_scoring_table.values

    # create dataframe
    df = pd.DataFrame()
    df['direct'] = direct_scores[:, 0]
    df['transitive'] = transitive_scores[:, 0]
    df['combined'] = combined_scores[:, 0]
    df['delta'] = combined_scores[:, 0] - direct_scores[:, 0]
    df['traced?'] = direct_scores[:, 1]
    df = df.reset_index()

    """
    How much was the maximum help the transitive technique provided?
    """
    traced_df = df[df['traced?'] == 1]
    example_item = traced_df.iloc[traced_df['delta'].argmax()]
    example_item_idx = example_item['index']
    example_score_delta = example_item['delta']
    example_technique_scores = (("direct", example_item['direct']),
                                ("transitive", example_item['transitive']),
                                ("combined", example_item['combined']))

    """
    What artifact pair benefited the most from the transitive technique?
    """
    dataset = Dataset(dataset_name)
    top_artifacts = dataset.artifacts.levels[0]
    intermediate_artifacts = dataset.artifacts.levels[1]
    bottom_artifacts = dataset.artifacts.levels[2]

    top_artifact_idx = int(example_item_idx // len(bottom_artifacts))
    bottom_artifact_idx = int(example_item_idx % len(bottom_artifacts))

    top_artifact = top_artifacts.iloc[top_artifact_idx]
    bottom_artifact = bottom_artifacts.iloc[bottom_artifact_idx]

    """
    What where the top n most beneficial intermediate artifacts?
    """
    upper = transitive_technique_data.transitive_matrices[0]
    lower = transitive_technique_data.transitive_matrices[1]

    intermediate_scores = pd.Series(upper[top_artifact_idx, :] * lower[:, bottom_artifact_idx])
    sorted_intermediate_scores = intermediate_scores.sort_values().iloc[::-1].reset_index(drop=True)
    sorted_intermediate_idx = intermediate_scores.argsort().iloc[::-1].reset_index(drop=True)

    top_n_intermediate_idx = sorted_intermediate_idx[:n_top_intermediate_artifacts]
    top_intermediate_artifacts = intermediate_artifacts.iloc[top_n_intermediate_idx]
    best_intermediate_ids = list(top_intermediate_artifacts['id'])
    best_intermediate_scores = sorted_intermediate_scores[:n_top_intermediate_artifacts]

    best_intermediate_artifacts = zip(best_intermediate_ids, best_intermediate_scores)

    """
    Print Results
    """
    techniques = [("direct", direct_technique_name),
                  ("transitive", transitive_technique_name),
                  ("combined", combined_technique_name)]
    for t in techniques:
        print("%s: %s" % (t[0], t[1]))
    print("\nThe query that benefited the most was %s -> %s" % (top_artifact['id'], bottom_artifact['id']))
    print("\nTechnique similarity scores:")
    for technique_score in example_technique_scores:
        print("%s: %f" % (technique_score[0], technique_score[1]))
    print("\nMost helpful intermediate artifacts (artifact, score): ")
    for best_i in best_intermediate_artifacts:
        print("%s -> %f" % (best_i[0], round(best_i[1], n_sig_figs)))
