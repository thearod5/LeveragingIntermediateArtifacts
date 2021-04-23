"""
Calculates what words two artifacts have in common.
"""
from typing import Tuple

import pandas as pd

from api.datasets.dataset import Dataset


def find_words_in_common(dataset: Dataset, artifact_ids: Tuple[str, str]):
    artifacts_df = pd.concat(dataset.artifacts, axis=0)
    artifacts_df = artifacts_df.set_index("id")

    word_intersection = set([])
    for a_id in artifact_ids:
        a = artifacts_df.loc[a_id]
        a_text = a["text"]
        print("%s:%s" % (a_id, a_text))
        a_words = a_text.split(" ")

        if len(word_intersection) == 0:
            word_intersection = set(a_words)
        else:
            word_intersection = word_intersection.intersection(set(a_words))

    return word_intersection


def get_words_in_common(doc_a: str, doc_b: str):
    """
    Returns set of words in common between given documents
    :param doc_a: source document
    :param doc_b: target document
    :return:
    """
    a_words = set(doc_a.split(" "))
    b_words = set(doc_b.split(" "))
    return a_words.intersection(b_words)


if __name__ == "__main__":
    global_ids = [("NFR11.txt", "FR41.txt")]
    dataset_name = "WARC"
    dataset = Dataset(dataset_name)

    for ids in global_ids:
        shared_words = find_words_in_common(dataset, ids)
        print(ids, "shared words: ", list(shared_words), "\n")
