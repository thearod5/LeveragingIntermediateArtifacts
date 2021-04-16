"""
Calculates what words two artifacts have in common.
"""
from typing import Tuple

import pandas as pd

from api.datasets.dataset import Dataset


def words_in_common(dataset_name: str, artifact_ids: Tuple[str, str]):
    dataset = Dataset(dataset_name)

    artifacts_df = pd.concat(dataset.artifacts, axis=0)
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

    return word_intersection


if __name__ == "__main__":
    global_ids = [("NFR11.txt", "FR41.txt")]
    dataset_name = "WARC"

    for ids in global_ids:
        shared_words = words_in_common(dataset_name, ids)
        print(ids, "shared words: ", list(shared_words), "\n")
