"""
The module contains a set of functions for extracting the best techniques from the aggregated metric table calculated.
"""
from typing import List, Union

import numpy as np

from api.constants.processing import DATASET_COLNAME, NAME_COLNAME
from api.constants.techniques import DIRECT_ID, HYBRID_ID, TRANSITIVE_ID
from api.tables.metric_table import MetricTable
from api.technique.definitions.combined.technique import (
    CombinedTechnique,
    create_technique_by_name,
)
from api.technique.definitions.direct.technique import DirectTechnique
from api.technique.definitions.sampled.definition import SAMPLED_COMMAND_SYMBOL
from api.technique.definitions.transitive.definition import TRANSITIVE_COMMAND_SYMBOL
from api.technique.definitions.transitive.technique import TransitiveTechnique
from api.technique.parser.itechnique import ITechnique
from utilities.constants import PATH_TO_METRIC_TABLE_AGGREGATE

AGGREGATE_METRIC_TABLE = MetricTable(path_to_table=PATH_TO_METRIC_TABLE_AGGREGATE)


def get_best_direct_technique(dataset_name: str) -> str:
    """
    Find the best direct techniques and returns the one corresponding to given dataset.
    :param dataset_name: the dataset that whose best technique we are after
    :return: string - technique definition
    """
    best_direct_definition = (
        AGGREGATE_METRIC_TABLE.find_direct_best_techniques().table.set_index(
            DATASET_COLNAME
        )
    )
    best_technique_query = best_direct_definition.loc[dataset_name][NAME_COLNAME]
    return get_simplest_technique(best_technique_query)


def get_best_transitive_technique(dataset_name: str):
    """
    Find the best transitive techniques and returns the one corresponding to given dataset.
    Note, only techniques without transitive traces are considered.
    :param dataset_name: the dataset that whose best technique we are after
    :return: string - technique definition
    """
    best_df = AGGREGATE_METRIC_TABLE.find_best_transitive_techniques().table.set_index(
        DATASET_COLNAME
    )
    best_technique_query = best_df.loc[dataset_name][NAME_COLNAME]
    return get_simplest_technique(best_technique_query)


def get_best_hybrid_technique(dataset_name: str):
    """
    Find the best combined techniques and returns the one corresponding to given dataset.
    Note, only techniques without transitive traces are considered.
    :param dataset_name: the dataset that whose best technique we are after
    :return: string - technique definition
    """

    best_df = AGGREGATE_METRIC_TABLE.find_best_combined_techniques().table.set_index(
        DATASET_COLNAME
    )
    best_technique_query = best_df.loc[dataset_name][NAME_COLNAME]
    return get_simplest_technique(best_technique_query)


def get_best_combined_sampled_technique(dataset: str):
    """
    Find the best combined technique for given dataset and transforms it into a sampled technique.
    :param dataset: the dataset that whose best technique we are after
    :return: string - technique definition
    """
    temp = get_best_hybrid_technique(dataset)
    temp = temp.replace(TRANSITIVE_COMMAND_SYMBOL, SAMPLED_COMMAND_SYMBOL)

    if "INDEPENDENT" in temp:
        temp = temp.replace("INDEPENDENT", "INDEPENDENT %f")
    if "GLOBAL" in temp:
        temp = temp.replace("GLOBAL", "GLOBAL %f")

    return temp


def get_technique_type_id(technique_definition: str):
    """
    Returns ID of the type of technique given.
    :param technique_definition: string format of definition
    :return: string - the id of the technique type
    """
    technique: ITechnique = create_technique_by_name(technique_definition)
    if isinstance(technique, DirectTechnique):
        return DIRECT_ID
    if isinstance(technique, TransitiveTechnique):
        return TRANSITIVE_ID
    if isinstance(technique, CombinedTechnique):
        return HYBRID_ID
    else:
        raise Exception("Technique %s not implemented." % technique.get_name())


def get_simplest_technique(best_technique_query: Union[str, List[str]]):
    """
    Given a list of technique definitions, returns the technique with the simplest implemntation.
    :param best_technique_query: list of techniques, or a single technique if no competing techniques
    :return: string - the technique definiton of the simplest techniques
    """
    if isinstance(best_technique_query, str):
        return best_technique_query

    points = [0] * len(best_technique_query)
    for t_index, candidate_technique in enumerate(best_technique_query):
        if "PCA" not in candidate_technique:
            points[t_index] = points[t_index] + 1

        if "VSM" in candidate_technique:
            points[t_index] = points[t_index] + 1

        if "INDEPENDENT" in candidate_technique:
            points[t_index] = points[t_index] + 1

    best_technique_index = np.array(points).argmax()

    return best_technique_query[best_technique_index]
