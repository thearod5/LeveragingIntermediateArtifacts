import pandas as pd

from api.constants.processing import METRIC_COLNAME, AP_COLNAME, LAG_COLNAME, AUC_COLNAME, \
    DATASET_COLNAME
from api.tables.metric_table import MetricTable
from tests.res.smart_test import SmartTest


class TestCommonOperations(SmartTest):
    df = pd.DataFrame()
    df["LagGlobal"] = [100, 200]

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
        result = MetricTable(data).create_melted_metrics().table
        self.assertEqual(3, len(result))
        self.assertTrue(DATASET_COLNAME in result.columns)
        self.assertTrue(METRIC_COLNAME in result.columns)
        self.assertFalse(AP_COLNAME in result.columns)
        self.assertFalse(AUC_COLNAME in result.columns)
        self.assertFalse(LAG_COLNAME in result.columns)
