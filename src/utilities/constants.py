import os

from api.constants.paths import PATH_TO_ROOT

PATH_TO_DATA = os.path.join(PATH_TO_ROOT, "..", "data")
PATH_TO_METRIC_TABLES = os.path.join(PATH_TO_DATA, "metric_tables")
PATH_TO_SAMPLED_METRIC_TABLES = os.path.join(PATH_TO_DATA, "sampled_metric_tables")
PATH_TO_INDIVIDUAL_QUERIES = os.path.join(PATH_TO_DATA, "individual_queries")

"""
AGGREGATES
"""
PATH_TO_AGGREGATE_TABLES = os.path.join(PATH_TO_DATA, "aggregates")
PATH_TO_METRIC_TABLE_AGGREGATE = os.path.join(
    PATH_TO_AGGREGATE_TABLES, "metric_table.csv"
)
PATH_TO_GRAPH_METRIC_TABLE_AGGREGATE = os.path.join(
    PATH_TO_AGGREGATE_TABLES, "graph_metric_table.csv"
)
PATH_TO_RQ1_AGGREGATE = os.path.join(PATH_TO_AGGREGATE_TABLES, "rq1.csv")
PATH_TO_BEST_AGGREGATE = os.path.join(PATH_TO_AGGREGATE_TABLES, "best.csv")
PATH_TO_ARTIFACT_SAMPLING_AGG = os.path.join(
    PATH_TO_AGGREGATE_TABLES, "artifacts_sampling.csv"
)
PATH_TO_TRACES_SAMPLING_AGG = os.path.join(
    PATH_TO_AGGREGATE_TABLES, "traces_sampling.csv"
)

PATH_TO_BEST_RANKS = os.path.join(PATH_TO_AGGREGATE_TABLES, "best_ranks.csv")
PATH_TO_INDIVIDUAL_QUERIES_AGG = os.path.join(
    PATH_TO_AGGREGATE_TABLES, "individual_queries.csv"
)

"""
PRESENTATION

contains the path to tables that are used directly in the paper
"""
PATH_TO_PRESENTATION = os.path.join(PATH_TO_DATA, "presentation")
PATH_TO_RQ1_BEST = os.path.join(PATH_TO_PRESENTATION, "rq1_best.csv")
PATH_TO_RQ1_GAIN = os.path.join(PATH_TO_PRESENTATION, "rq1_gain.csv")
PATH_TO_RQ2_GAIN = os.path.join(PATH_TO_PRESENTATION, "rq2_gain.csv")
PATH_TO_RQ1_CORRELATION = os.path.join(PATH_TO_PRESENTATION, "rq1_correlation.csv")
PATH_TO_RQ2_CORRELATION = os.path.join(PATH_TO_PRESENTATION, "rq2_correlation.csv")
PATH_TO_RQ1_GAIN_CORRELATION = os.path.join(
    PATH_TO_PRESENTATION, "rq1_gain_correlation.csv"
)
PATH_TO_RQ2_GAIN_CORRELATION = os.path.join(
    PATH_TO_PRESENTATION, "rq2_gain_correlation.csv"
)
DATASET_COLUMN_ORDER = ["Drone", "TrainController", "EasyClinic", "EBT", "WARC"]
