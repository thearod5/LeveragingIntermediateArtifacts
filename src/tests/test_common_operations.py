import pandas as pd

from api.constants.processing import METRIC_COLNAME, AP_COLNAME, LAG_COLNAME, AUC_COLNAME, \
    DATASET_COLNAME
from src.analysis.common_operations import normalize_lag_scores, normalize_invert_lag_global, \
    create_melted_metrics
from tests.res.smart_test import SmartTest


class TestCommonOperations(SmartTest):
    df = pd.DataFrame()
    df["LagGlobal"] = [100, 200]

    def test_normalize_lag_normal(self):
        result = normalize_lag_scores(self.df["LagGlobal"])
        self.assertEqual(2, len(result), "result length")
        self.assertEqual(0, result[0])
        self.assertEqual(1, result[1])

        inverted_result = normalize_invert_lag_global(self.df["LagGlobal"])
        self.assertEqual(2, len(inverted_result), "inverted result length")
        self.assertEqual(1, inverted_result[0])
        self.assertEqual(0, inverted_result[1])

    def test_normalize_lag_normal_2(self):
        result = normalize_lag_scores(self.df["LagGlobal"], 0, 300)
        self.assertEqual(2, len(result), "result length")
        self.assertEqual(0.33, round(result[0], 2), "normalize min value")
        self.assertEqual(.67, round(result[1], 2), "normalize max value")

        inverted_result = normalize_invert_lag_global(self.df["LagGlobal"],
                                                      0, 300)
        self.assertEqual(2, len(inverted_result), "inverted result length")
        self.assertEqual(0.67, round(inverted_result[0], 2), "inverted max value")
        self.assertEqual(0.33, round(inverted_result[1], 2), "inverted min value")

    """
    create_melted_metrics
    """

    def test_create_melted_metrics(self):
        data = pd.DataFrame()
        data = data.append({DATASET_COLNAME: "MockDataset",
                            AP_COLNAME: 0.4,
                            LAG_COLNAME: 0.3,
                            AUC_COLNAME: 0.2},
                           ignore_index=True)

        result = create_melted_metrics(data)
        self.assertEqual(3, len(result))
        self.assertTrue(DATASET_COLNAME in result.columns)
        self.assertTrue(METRIC_COLNAME in result.columns)
        self.assertFalse(AP_COLNAME in result.columns)
        self.assertFalse(AUC_COLNAME in result.columns)
        self.assertFalse(LAG_COLNAME in result.columns)
