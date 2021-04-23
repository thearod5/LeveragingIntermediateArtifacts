"""
The following script will investigate why certain queries in some datasets have a AP score of 0

Requirements:

- the system shall be able to examine all similarity scores for a particular query
- the system shall be able to list the pair of traced artifacts with the lowest similarity score
"""
from typing import List

import numpy as np

from api.constants.dataset import SimilarityMatrix
from api.datasets.dataset import Dataset
from api.extension.cache import Cache
from api.technique.definitions.transitive.calculator import TransitiveTechniqueData
from api.tracer import Tracer
from utilities.technique_extractors import (
    get_best_direct_technique,
    get_best_hybrid_technique,
    get_best_transitive_technique,
)

AP_THRESHOLD = 0.1
BAR = "-" * 50


def get_worst_query(metrics):
    ap_scores = list(map(lambda m: m.ap, metrics))
    min_ap = min(ap_scores)
    query_indices = [m.query_id for m in metrics if m.ap == min_ap]
    return query_indices[0], min_ap


def get_metrics_by_query(metrics, query_id: int):
    query = [m for m in metrics if m.query_id == query_id]
    assert len(query) == 1
    return query[0]


def get_trace_link_indices(oracle_matrix: SimilarityMatrix, query_index: int):
    return [i[1] for i in np.argwhere(oracle_matrix == 1) if i[0] == query_index]


def get_ranks_of_trace_links(
    oracle_matrix: SimilarityMatrix,
    similarity_matrix: SimilarityMatrix,
    query_index: int,
):
    """
    Returns the ranks of the traced artifacts in query with given index within given similarity matrix.
    :param oracle_matrix: the matrix defining where the trace links are
    :param similarity_matrix: the matrix ranking artifact pairs
    :param query_index: the index of the query whose traced artifacts ranks we are concerned with
    :return: list of integers representing ranks
    """
    traced_link_indices = get_trace_link_indices(oracle_matrix, query_index)
    query_similarities = similarity_matrix[query_index, :]
    sorted_indices = np.argsort(query_similarities)[::-1]
    trace_link_ranks = [
        i[0] for i in enumerate(sorted_indices) if i[1] in traced_link_indices
    ]
    return trace_link_ranks


def print_trace_link_ranks_per_technique(
    dataset_name: str,
    similarity_matrices: List[SimilarityMatrix],
    labels: List[str],
    query_index: int,
):
    dataset = Dataset(dataset_name)

    oracle_matrix = dataset.traced_matrices["0-2"]
    n_trace_links = sum(oracle_matrix[query_index, :] == 1)
    print(f"Rankings of trace links in worst performing query")
    print(f"Trace links in query: {n_trace_links}")

    for similarity_matrix, label in zip(similarity_matrices, labels):
        trace_link_ranks = get_ranks_of_trace_links(
            oracle_matrix,
            similarity_matrix,
            query_index,
        )
        print(f"{label}: {trace_link_ranks}")


def get_highest_ranking_artifact_pair_indices(
    oracle_matrix: SimilarityMatrix,
    similarity_matrix: SimilarityMatrix,
    query_index: int,
    label_value: int,
):
    """
    Returns indices of artifacts consisting of highest ranking non trace link in similarity matrix for dataset
    :param oracle_matrix: ground truth labels for trace links
    :param similarity_matrix: the ranking of all source to target artifacts
    :param query_index: the query of whose highest non trace we are interested in
    :param label_value: either 1 for trace links or 0 for non links
    :return:
    """

    ranked_indices = np.argsort(similarity_matrix[query_index, :])[::-1]
    ranked_labels = oracle_matrix[query_index, ranked_indices]

    for rank, r_label in enumerate(ranked_labels):
        if r_label == label_value:
            link_index = ranked_indices[rank]
            score = similarity_matrix[query_index, link_index]
            return [query_index, link_index, rank, score]


def print_highest_ranking_link_in_query(
    dataset_name: str,
    technique_data: TransitiveTechniqueData,
    query_index: int,
    label_value: int,
    n_artifact: int,
):
    dataset = Dataset(dataset_name)
    oracle_matrix = dataset.traced_matrices["0-2"]

    (
        link_source_index,
        link_target_index,
        link_rank,
        link_score,
    ) = get_highest_ranking_artifact_pair_indices(
        oracle_matrix,
        technique_data.similarity_matrix,
        query_index,
        label_value,
    )

    source_id = dataset.artifacts[0].iloc[link_source_index]["id"]
    target_id = dataset.artifacts[2].iloc[link_target_index]["id"]

    print(f"Link: {(source_id, target_id)}")
    print(f"Type:", label_value)
    print(f"Technique: ", transitive_technique_data.technique.get_name())
    print(f"Rank: {link_rank}")
    print(f"Score: {link_score}")

    upper_intermediate_values = technique_data.transitive_matrices[0][
        link_source_index, :
    ].flatten()
    lower_intermediate_values = technique_data.transitive_matrices[1][
        :, link_target_index
    ].flatten()
    intermediate_values = upper_intermediate_values * lower_intermediate_values
    sorted_values = np.sort(intermediate_values)[::-1]
    best_intermediate_artifact_indices = np.argsort(intermediate_values)[::-1][
        :n_artifact
    ]
    best_intermediate_artifact_ids = list(
        dataset.artifacts[1].iloc[best_intermediate_artifact_indices]["id"]
    )
    print("Most influential intermediate artifacts:", best_intermediate_artifact_ids)
    print("Intermediate scores:", sorted_values[:n_artifact])
    print("Intermediate Sum", sum(intermediate_values))
    print("Intermediate Max:", max(intermediate_values))


if __name__ == "__main__":
    Cache.CACHE_ON = False
    d_name = "EBT"
    direct_t_name = get_best_direct_technique(d_name)
    transitive_t_name = get_best_transitive_technique(d_name)
    hybrid_t_name = get_best_hybrid_technique(d_name)

    tracer = Tracer()
    direct_technique_data = tracer.get_technique_data(d_name, direct_t_name)
    transitive_technique_data = tracer.get_technique_data(d_name, transitive_t_name)
    hybrid_technique_data = tracer.get_technique_data(d_name, hybrid_t_name)
    hybrid_metrics = tracer.get_metrics(d_name, hybrid_t_name, summary_metrics=False)
    data_labels = ["direct", "transitive", "hybrid"]
    data = [direct_technique_data, transitive_technique_data, hybrid_technique_data]
    matrices = list(map(lambda d: d.similarity_matrix, data))

    worst_query_index, ap_score = get_worst_query(hybrid_metrics)
    print("Hybrid Technique:", hybrid_t_name)
    print("Hybrid AP on worst query:", ap_score)

    """
    Experiments
    """
    print()
    print_trace_link_ranks_per_technique(
        d_name, matrices, data_labels, worst_query_index
    )
    print(BAR)
    print_highest_ranking_link_in_query(
        d_name, transitive_technique_data, worst_query_index, 0, 5
    )
    print(BAR)
    print_highest_ranking_link_in_query(
        d_name, transitive_technique_data, worst_query_index, 1, 5
    )
    print(BAR)
    print("Done!")
