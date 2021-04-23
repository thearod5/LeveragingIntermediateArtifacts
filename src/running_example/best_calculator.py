from api.constants.processing import DATASET_COLNAME, TRANSITIVE_TRACE_TYPE_COLNAME
from api.tables.metric_table import get_best_rows
from utilities.technique_extractors import AGGREGATE_METRIC_TABLE

if __name__ == "__main__":
    data = AGGREGATE_METRIC_TABLE.create_lag_norm_inverted().table
    data["agg_metric"] = data["lag_normalized_inverted"] + data["ap"] + data["auc"]
    data = data[data[TRANSITIVE_TRACE_TYPE_COLNAME].isin(["direct", "none"])]
    print(data.columns)
    print(data.transitive_trace_type.unique())
    best_rows_query = get_best_rows(
        data, ["ap", "auc", "lag_normalized_inverted"]
    ).set_index(DATASET_COLNAME)

    print(best_rows_query.loc["EBT"]["name"])
