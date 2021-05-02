"""
The following script is meant to explore why EBT observes near zero gain on MAP but a lot of gain
in AUC and LAG.
"""

import os

import pandas as pd
from sklearn.preprocessing import minmax_scale

from api.datasets.dataset import Dataset
from api.tracer import Tracer
from experiments.evaluate_paths import change_paths_in_technique
from utilities.constants import PATH_TO_EXPLORATORY
from utilities.technique_extractors import (
    get_best_direct_technique,
    get_best_hybrid_technique,
    get_best_transitive_technique,
)

if __name__ == "__main__":
    dataset_name = "Drone"
    tracer = Tracer()

    direct_technique = get_best_direct_technique(dataset_name)
    transitive_technique = get_best_transitive_technique(dataset_name)
    hybrid_technique = get_best_hybrid_technique(dataset_name)
    new_path = ["0", "2", "1"]
    techniques = [direct_technique, transitive_technique, hybrid_technique]
    techniques = [change_paths_in_technique(t, new_path) for t in techniques]
    matrices = [
        tracer.get_technique_data(dataset_name, t).similarity_matrix for t in techniques
    ]
    matrices = list(map(minmax_scale, matrices))

    def get_group(percentile):
        if percentile < 1 / 3:
            return "low"
        elif percentile < 2 / 3:
            return "medium"
        else:
            return "high"

    trace_matrix = Dataset(dataset_name).traced_matrices[
        "%s-%s" % (new_path[0], new_path[2])
    ]
    entries = []
    for row_index in range(matrices[0].shape[0]):
        original_groups = []
        for family, matrix in zip(["direct", "transitive", "hybrid"], matrices):
            query_ranks = pd.Series(matrix[row_index, :]).rank()
            query_percentiles = 1 - (query_ranks / max(query_ranks))

            if len(original_groups) == 0:
                original_groups = list(map(get_group, query_percentiles))

            for col_index in range(matrices[0].shape[1]):
                trace_value = trace_matrix[row_index, col_index]
                entries.append(
                    {
                        "family": family,
                        "type": "links" if trace_value == 1 else "non-links",
                        "percentile": query_percentiles[col_index],
                        "original_group": original_groups[col_index],
                    }
                )
        original_groups = []
    data = pd.DataFrame(entries)
    data.to_csv(
        os.path.join(PATH_TO_EXPLORATORY, f"{dataset_name}_{'-'.join(new_path)}.csv"),
        index=False,
    )
    print("Done!")
