"""
The following script investigates whether transitive technique are fulfilling their expected purpose:
to capture transitive relationships where direct comparisons would not be able to.

Steps:
1. Find the trace queries whose target artifacts share the smallest number of words with the source artifact
2. Examine the performance of the best transitive technique on this query.
"""
import os
from typing import List, Tuple

import numpy as np
import pandas as pd

from api.constants.dataset import SimilarityMatrix
from api.datasets.builder.trace_id_map import TraceIdMap
from api.datasets.dataset import Dataset
from api.tracer import Tracer
from running_example.calculate_words_in_common import get_words_in_common
from utilities.constants import PATH_TO_PRESENTATION
from utilities.technique_extractors import (
    get_best_direct_technique,
    get_best_transitive_technique,
)


def get_artifact_indices_with_word_intersection(
    dataset: Dataset, n_word_intersection: int, trace_matrix_id: str = "0-2"
):
    """
    For each query (row) finds the trace link where the source and target artifact share the smallest number of words
    :param dataset: containing trace matrix and artifacts
    :param trace_matrix_id: the id of query path whose trace matrix we are analyzing
    :return:
    """

    a_index, b_index = TraceIdMap.parse_trace_id(trace_matrix_id)
    trace_matrix = dataset.traced_matrices[trace_matrix_id]
    trace_links_locations = np.where(trace_matrix == 1)
    trace_links = list(zip(trace_links_locations[0], trace_links_locations[1]))
    non_intersection_traced_artifacts = []
    for query_index in range(trace_matrix.shape[0]):
        query_trace_links = [link for link in trace_links if link[0] == query_index]
        for q_trace_link in query_trace_links:
            source_index = q_trace_link[0]
            target_index = q_trace_link[1]
            source_artifact = dataset.artifacts[a_index].iloc[source_index]["text"]
            target_artifact = dataset.artifacts[b_index].iloc[target_index]["text"]
            words_in_common = get_words_in_common(source_artifact, target_artifact)
            if len(words_in_common) == n_word_intersection:
                non_intersection_traced_artifacts.append((source_index, target_index))
    return non_intersection_traced_artifacts


def compare_metrics_on_queries(
    artifact_indices: List[Tuple[int, int]],
    base_matrix: SimilarityMatrix,
    target_matrix: SimilarityMatrix,
):
    rank_gains = []
    base_ranks = []
    target_ranks = []
    n_possible_ranks = base_matrix.shape[1]
    for source_index, target_index in artifact_indices:
        base_rankings = np.argsort(base_matrix[source_index, :])[::-1]
        target_rankings = np.argsort(target_matrix[source_index, :])[::-1]

        base_rank = np.where(base_rankings == target_index)[0][0]
        target_rank = np.where(target_rankings == target_index)[0][0]
        rank_gains.append((base_rank - target_rank) / n_possible_ranks)
        base_ranks.append(base_rank / n_possible_ranks)
        target_ranks.append(target_rank / n_possible_ranks)

    return rank_gains, base_ranks, target_ranks


if __name__ == "__main__":
    datasets = ["WARC", "EBT", "EasyClinic", "Drone", "TrainController"]
    EXPORT_PATH = os.path.join(PATH_TO_PRESENTATION, "word_intersection.csv")
    MAX_N_WORDS = 10
    df = pd.DataFrame()
    for d_name in datasets:
        d = Dataset(d_name)
        direct_technique = get_best_direct_technique(d_name)
        transitive_technique = get_best_transitive_technique(d_name)

        tracer = Tracer()
        direct_similarity_matrix = tracer.get_technique_data(
            d_name, direct_technique
        ).similarity_matrix
        transitive_similarity_matrix = tracer.get_technique_data(
            d_name, transitive_technique
        ).similarity_matrix
        for n_intersection_words in range(MAX_N_WORDS):
            non_intersection_artifact_indices = (
                get_artifact_indices_with_word_intersection(d, n_intersection_words)
            )
            if len(non_intersection_artifact_indices) == 0:
                continue

            ranks = compare_metrics_on_queries(
                non_intersection_artifact_indices,
                direct_similarity_matrix,
                transitive_similarity_matrix,
            )
            for r_gain, b_rank, t_rank in zip(ranks[0], ranks[1], ranks[2]):
                entry = {
                    "dataset": d_name,
                    "n_words": n_intersection_words,
                    "rank_gain": r_gain,
                    "direct_rank": b_rank,
                    "transitive_rank": t_rank,
                }
                df = df.append(entry, ignore_index=True)
    df.to_csv(EXPORT_PATH, index=False)
    print("Done!")
