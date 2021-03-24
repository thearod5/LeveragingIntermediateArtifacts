import os

from api.constants.paths import PATH_TO_ROOT

PATH_TO_DATA = os.path.join(PATH_TO_ROOT, "..", "data")
PATH_TO_METRIC_TABLES = os.path.join(PATH_TO_DATA, "metric_tables")
PATH_TO_SAMPLED_METRIC_TABLES = os.path.join(PATH_TO_DATA, "sampled_metric_tables")

PATH_TO_AGGREGATE_TABLES = os.path.join(PATH_TO_DATA, "aggregates")
PATH_TO_METRIC_TABLE_AGGREGATE = os.path.join(
    PATH_TO_AGGREGATE_TABLES, "metric_table.csv"
)
PATH_TO_RQ1_AGGREGATE = os.path.join(PATH_TO_AGGREGATE_TABLES, "rq1.csv")
PATH_TO_BEST_AGGREGATE = os.path.join(PATH_TO_AGGREGATE_TABLES, "best.csv")
PATH_TO_GAIN_AGGREGATE = os.path.join(PATH_TO_AGGREGATE_TABLES, "gain.csv")
PATH_TO_ARTIFACT_SAMPLING_AGG = os.path.join(
    PATH_TO_AGGREGATE_TABLES, "artifacts_sampling.csv"
)
PATH_TO_TRACES_SAMPLING_AGG = os.path.join(
    PATH_TO_AGGREGATE_TABLES, "traces_sampling.csv"
)
PATH_TO_ARTIFACT_CORRELATION_AGG = os.path.join(
    PATH_TO_AGGREGATE_TABLES, "artifacts_correlation.csv"
)
PATH_TO_TRACES_CORRELATION_AGG = os.path.join(
    PATH_TO_AGGREGATE_TABLES, "traces_correlation.csv"
)
