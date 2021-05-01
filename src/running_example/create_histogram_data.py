"""
The following script generates a dataset for a given technique containing all of its similarity scores
"""
import os

import pandas as pd
from sklearn.preprocessing import minmax_scale

from api.datasets.dataset import Dataset
from api.tracer import Tracer
from utilities.constants import PATH_TO_DATA
from utilities.technique_extractors import get_best_transitive_technique

if __name__ == "__main__":
    good_dataset_name = "TrainController"

    EXPORT_PATH = os.path.join(
        PATH_TO_DATA, "presentation", "similarity_distribution.csv"
    )

    good_transitive_technique = get_best_transitive_technique(good_dataset_name)

    tracer = Tracer()
    technique_data = tracer.get_technique_data(
        good_dataset_name, good_transitive_technique
    )
    metrics = tracer.get_metrics(
        good_dataset_name, good_transitive_technique, summary_metrics=False
    )
    sorted_metrics = sorted(metrics, key=lambda m: m.ap)
    N_QUERIES = 5
    bad_queries = [m.query_id for m in sorted_metrics[:N_QUERIES]]
    good_queries = [m.query_id for m in sorted_metrics[-N_QUERIES:]]
    similarity_matrix = minmax_scale(technique_data.similarity_matrix)
    oracle_matrix = Dataset(good_dataset_name).traced_matrices["0-2"]

    data = pd.DataFrame()

    for g_query in good_queries:
        for col_index in range(similarity_matrix.shape[1]):
            score_value = similarity_matrix[g_query][col_index]
            oracle_value = oracle_matrix[g_query][col_index]
            delta_value = score_value - oracle_value
            entry = {
                "query_performance": "top_5",
                "value": delta_value,
                "type": "traced" if oracle_value == 1 else "not traced",
            }
            data = data.append(entry, ignore_index=True)

    for b_query in bad_queries:
        for col_index in range(similarity_matrix.shape[1]):
            score_value = similarity_matrix[b_query][col_index]
            oracle_value = oracle_matrix[b_query][col_index]
            delta_value = score_value - oracle_value
            entry = {
                "query_performance": "worst_5",
                "value": delta_value,
                "type": "traced" if oracle_value == 1 else "not traced",
            }
            data = data.append(entry, ignore_index=True)

    data.to_csv(EXPORT_PATH, index=False)
    print("Done!")
