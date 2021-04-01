"""
The following src collects metrics on the individual queries for both a transitive and
direct technique.
"""
import os
import re
from typing import Dict

from api.constants.processing import DATASET_COLNAME, NAME_COLNAME
from api.constants.techniques import DIRECT_ID, HYBRID_ID, TRANSITIVE_ID
from api.tables.metric_table import MetricTable
from api.tables.table import Table
from api.tracer import Tracer
from experiments.meta.experiment import Experiment
from utilities.constants import DATASET_COLUMN_ORDER, PATH_TO_AGGREGATE_TABLES
from utilities.progress_bar_factory import create_loading_bar
from utilities.technique_extractors import (
    get_best_direct_technique,
    get_best_hybrid_technique,
    get_best_transitive_technique,
)

EXPERIMENT_NAME = "evaluate_paths"
EXPORT_PATH = os.path.join(PATH_TO_AGGREGATE_TABLES, "hierarchy_experiment_results.csv")
QUERY_INDEX_COLNAME = "query_index"

POSSIBLE_PATHS = [(0, 1, 2), (1, 0, 2), (2, 1, 0)]

DIRECT_TECHNIQUE_TEMPLATE = "(. (VSM NT) (%s %s))"
TRANSITIVE_TECHNIQUE_TEMPLATE = (
    "(x (MAX INDEPENDENT) ((. (VSM NT) (%s %s)) (. (VSM NT) (%s %s))))"
)
HYBRID_TECHNIQUE_TEMPLATE = (
    "(o (MAX) ((. (LSI NT) (%s %s))"
    " (x (SUM INDEPENDENT) ((. (VSM NT) (%s %s)) (. (VSM NT) (%s %s))))))"
)


def path_to_str(path_tuple):
    return "%s->%s->%s" % (path_tuple[0], path_tuple[1], path_tuple[2])


def path_iterator():
    for dataset_name in DATASET_COLUMN_ORDER:
        for path in POSSIBLE_PATHS:
            yield path, dataset_name


def create_template(text: str, rep: Dict[str, str]):
    # use these three lines to do the replacement
    rep = dict((re.escape(k), v) for k, v in rep.items())
    # Python 3 renamed dict.iteritems to dict.items so use rep.items() for latest versions
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], text)


class EvaluatePaths(Experiment):
    """
    Calculates metrics on all possible paths between three artifact types.
    """

    def run(self) -> Table:
        tracer = Tracer()
        metric_table = MetricTable()

        def get_metrics(d_name, t_def: str):
            return tracer.get_metrics(d_name, t_def, summary_metrics=False)

        def add_metrics(d_name, t_def: str, t_type: str, p_name: str):
            t_metrics = get_metrics(d_name, t_def)
            metric_table.add(
                t_metrics,
                {
                    DATASET_COLNAME: d_name,
                    "path": p_name,
                    "type": t_type,
                    NAME_COLNAME: t_def,
                },
                create_index=True,
                index_name=QUERY_INDEX_COLNAME,
            )

        with create_loading_bar(
            EXPERIMENT_NAME, path_iterator(), len(POSSIBLE_PATHS)
        ) as experiment_iterable:
            for path, dataset_name in experiment_iterable:
                source_index = str(path[0])
                intermediate_index = str(path[1])
                target_index = str(path[2])

                replacement_dict = {
                    "0": source_index,
                    "1": intermediate_index,
                    "2": target_index,
                }

                path_name = path_to_str(path)

                # direct
                direct_technique_def = create_template(
                    get_best_direct_technique(dataset_name), replacement_dict
                )
                add_metrics(
                    dataset_name,
                    direct_technique_def,
                    DIRECT_ID,
                    path_name,
                )

                # transitive
                transitive_technique_def = create_template(
                    get_best_transitive_technique(dataset_name), replacement_dict
                )
                add_metrics(
                    dataset_name,
                    transitive_technique_def,
                    TRANSITIVE_ID,
                    path_name,
                )

                # HYBRID
                hybrid_technique_definition = create_template(
                    get_best_hybrid_technique(dataset_name), replacement_dict
                )
                add_metrics(
                    dataset_name,
                    hybrid_technique_definition,
                    HYBRID_ID,
                    path_name,
                )

        metric_table.save(EXPORT_PATH)
        self.export_paths.append(EXPORT_PATH)
        return metric_table

    @staticmethod
    def name() -> str:
        return EXPERIMENT_NAME


if __name__ == "__main__":
    EvaluatePaths().run()
    print("Done")
