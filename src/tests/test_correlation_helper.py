import random

import pandas as pd

from api.constants.processing import (
    AP_COLNAME,
    AUC_COLNAME,
    CORRELATION_COLNAME,
    DF_METRICS,
    LAG_COLNAME,
    METRIC_COLNAME,
    PERCENT_COLNAME,
    P_VALUE_COLNAME,
    VALUE_COLNAME,
)
from api.extension.experiment_types import SamplingExperiment
from src.analysis.sampling.gain_correlation_joiner import (
    create_correlation_matrix,
    create_gain_correlation_table,
)
from tests.res.test_technique_helper import TestTechniqueHelper


def create_sample_data():
    n_metrics = 3
    n_values_per_percent = 10
    n_percents = 10

    data = pd.DataFrame()
    for metric in DF_METRICS[:n_metrics]:
        for percent in [p_i / n_percents for p_i in range(n_percents)]:
            for _ in range(n_values_per_percent):
                entry = {
                    METRIC_COLNAME: metric,
                    VALUE_COLNAME: random.uniform(percent - 1, percent + 1),
                    PERCENT_COLNAME: percent,
                }
                data = data.append(entry, ignore_index=True)
    return data


class TestCorrelationHelper(TestTechniqueHelper):
    """
    create_correlation_matrix
    """

    data = create_sample_data()

    def test_create_correlation_matrix(self):
        corr_df = create_correlation_matrix(self.data)
        self.assertTrue(
            all([col in corr_df for col in [CORRELATION_COLNAME, P_VALUE_COLNAME]])
        )
        corr_df = corr_df.set_index(METRIC_COLNAME)

        self.assertGreater(corr_df.loc[AP_COLNAME][CORRELATION_COLNAME], 0)
        self.assertGreater(corr_df.loc[LAG_COLNAME][CORRELATION_COLNAME], 0)
        self.assertGreater(corr_df.loc[AUC_COLNAME][CORRELATION_COLNAME], 0)

    def test_create_correlation_matrix_with_empty_data(self):
        self.assertRaises(Exception, lambda: create_correlation_matrix(pd.DataFrame()))

    """
    create_gain_correlation_table
    """

    def test_create_gain_correlation_table_with_artifacts(self):
        correlation_df = create_correlation_matrix(self.data)
        gain_correlation_df = create_gain_correlation_table(
            "EasyClinic", SamplingExperiment.ARTIFACTS, correlation_df
        )
        self.assertFalse(any(gain_correlation_df.isna().any()))

    def test_create_gain_correlation_table_with_traces(self):
        correlation_df = create_correlation_matrix(self.data)
        gain_correlation_df = create_gain_correlation_table(
            "EasyClinic", SamplingExperiment.TRACES, correlation_df
        )
        self.assertFalse(any(gain_correlation_df.isna().any()))
