"""
Calculates what words two artifacts have in common.
"""

import pandas as pd

from api.datasets.dataset import Dataset

if __name__ == "__main__":
    dataset_name = "Drone"
    ids = ["RE-100", "IMonitoringDataHandler.java"]

    # get technique similarity values
    dataset = Dataset(dataset_name)

    artifacts_df = pd.concat(dataset.artifacts.artifact_levels, axis=0)
    artifacts_df = artifacts_df.set_index("id")

    word_intersection = set([])
    for a_id in ids:
        a = artifacts_df.loc[a_id]
        a_text = a["text"]
        print("%s:%s" % (a_id, a_text))
        a_words = a_text.split(" ")

        if len(word_intersection) == 0:
            word_intersection = set(a_words)
        else:
            word_intersection = word_intersection.intersection(set(a_words))

    print("shared words: ", list(word_intersection))
