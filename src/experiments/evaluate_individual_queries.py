"""
The following script is intended to calculate a csv file containing the
map, lag, and auc of individual queries in some dataset for some technique.
"""

import os

import pandas as pd

from api.constants.processing import LAG_COLNAME, LAG_NORMALIZED_COLNAME
from api.constants.techniques import COMBINED_ID, DIRECT_ID, TRANSITIVE_ID
from api.tables.metric_table import MetricTable, Metrics
from api.tables.table import Table
from api.technique.definitions.combined.technique import (
    CombinedTechnique,
    create_technique_by_name,
)
from api.technique.definitions.direct.technique import DirectTechnique
from api.technique.definitions.transitive.technique import TransitiveTechnique
from api.tracer import Tracer


def get_technique_type(technique_name: str):
    technique = create_technique_by_name(technique_name)
    if isinstance(technique, DirectTechnique):
        return DIRECT_ID
    elif isinstance(technique, TransitiveTechnique):
        return TRANSITIVE_ID
    elif isinstance(technique, CombinedTechnique):
        return COMBINED_ID
    else:
        raise Exception("Technique %s not implemented." % technique.name)


def calculate_metric_table_for_single_queries(df: pd.DataFrame) -> Table:
    """
    Returns a metric table containing all of the metrics calculated for each technique in df
    :param df: df containing columns 'dataset' and 'name'
    :return: metric table with single query metrics for each technique applied to specified dataset in row
    """
    tracer = Tracer()
    table = MetricTable()
    for i in range(len(df)):

        df_entry = df.iloc[i]
        dataset_name = df_entry["dataset"]
        best_technique_name = df_entry["name"]
        technique_type = get_technique_type(best_technique_name)
        if technique_type != DIRECT_ID or dataset_name != "EasyClinic":
            continue

        query_metrics: [Metrics] = tracer.get_metrics(
            dataset_name, best_technique_name, summary_metrics=False
        )
        entry_id = {"dataset": dataset_name, "type": technique_type}
        table.add(query_metrics, other=entry_id, create_index=True)

    return table


if __name__ == "__main__":
    PATH_TO_BEST_TECHNIQUES_GENERALIZED = os.path.join(
        PATH_TO_DATA, "processed", "best", "best_techniques_generalized.csv"
    )

    EXPORT_PATH = os.path.join("~/downloads/individual_queries_generalized.csv")
    MELTED_EXPORT_PATH = os.path.join(
        "~/downloads/individual_queries_generalized_melted.csv"
    )

    best_generalized_df = pd.read_csv(PATH_TO_BEST_TECHNIQUES_GENERALIZED)
    metric_table = calculate_metric_table_for_single_queries(best_generalized_df)

    print(metric_table.table)
    metric_table.scale_col(
        LAG_COLNAME,
        ["dataset"],
        new_col_name=LAG_NORMALIZED_COLNAME,
        drop_old=True,
        inverted=True,
    )
    metric_table.save(EXPORT_PATH, melt_data=False)
    metric_table.save(MELTED_EXPORT_PATH, melt_data=True)
    print("done")
