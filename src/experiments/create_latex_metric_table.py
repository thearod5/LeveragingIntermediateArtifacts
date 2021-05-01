"""
The following script is responsible for creating Table 2 of our study's paper.
Namely, this involves displaying the latex code representing the metric scores for all direct techniques,
all transitive techniques, and the best (and worst) hybrid techniques.
"""
import os

import pandas as pd

from api.constants.processing import (
    AP_COLNAME,
    AUC_COLNAME,
    DATASET_COLNAME,
    DIRECT_ALGEBRAIC_MODEL_COLNAME,
    LAG_NORMALIZED_INVERTED_COLNAME,
    TRANSITIVE_AGGREGATION_COLNAME,
    TRANSITIVE_ALGEBRAIC_MODEL_COLNAME,
    TRANSITIVE_SCALING_COLNAME,
    TRANSITIVE_TRACE_TYPE_COLNAME,
)
from api.constants.techniques import DIRECT_ID, TRANSITIVE_ID
from api.tables.metric_table import MetricTable
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from api.technique.variationpoints.scalers.scaling_method import ScalingMethod
from utilities.constants import DATASET_COLUMN_ORDER, PATH_TO_PRESENTATION
from utilities.technique_extractors import AGGREGATE_METRIC_TABLE

if __name__ == "__main__":
    data = AGGREGATE_METRIC_TABLE.table
    mask = (
        AGGREGATE_METRIC_TABLE.get_technique_type_mask(DIRECT_ID)
        | AGGREGATE_METRIC_TABLE.get_technique_type_mask(TRANSITIVE_ID)
    ) & (data[TRANSITIVE_TRACE_TYPE_COLNAME].isin(["direct", "none"]))

    masked_data = AGGREGATE_METRIC_TABLE.table[mask].reset_index(drop=True)
    table_metrics = (
        MetricTable(masked_data).create_lag_norm_inverted(drop_old=True).table
    )

    column_orders = {
        DIRECT_ALGEBRAIC_MODEL_COLNAME: [
            AlgebraicModel.VSM.value,
            AlgebraicModel.LSI.value,
        ],
        TRANSITIVE_ALGEBRAIC_MODEL_COLNAME: [
            AlgebraicModel.VSM.value,
            AlgebraicModel.LSI.value,
        ],
        TRANSITIVE_SCALING_COLNAME: [
            ScalingMethod.INDEPENDENT.value,
            ScalingMethod.GLOBAL.value,
        ],
        TRANSITIVE_AGGREGATION_COLNAME: [
            AggregationMethod.SUM.value,
            AggregationMethod.PCA.value,
            AggregationMethod.MAX.value,
        ],
        DATASET_COLNAME: DATASET_COLUMN_ORDER,
    }

    for col_name, value_order in column_orders.items():
        table_metrics[col_name] = pd.Categorical(
            table_metrics[col_name], categories=value_order
        )

    sorted_column_names = list(column_orders.keys())
    metric_columns = [AP_COLNAME, AUC_COLNAME, LAG_NORMALIZED_INVERTED_COLNAME]
    table_metrics = table_metrics[sorted_column_names + metric_columns]
    sorted_metrics = table_metrics.sort_values(by=sorted_column_names)

    EXPORT_PATH = os.path.join(PATH_TO_PRESENTATION, "latex_table_values.csv")
    sorted_metrics.to_csv(EXPORT_PATH, index=False)

    row_values = []
    for i in range(len(sorted_metrics)):

        entry = sorted_metrics.iloc[i]
        for metric_name in metric_columns:
            value = str(round(entry[metric_name], 3))
            row_values.append(value)

        if (i + 1) % 5 == 0 and i > 0:
            print("&".join(row_values))
            row_values = []
