import pandas as pd

from api.constants.processing import LAG_COLNAME, DATASET_COLNAME, AP_COLNAME, TRANSITIVE_TRACE_TYPE_COLNAME, \
    RANK_COLNAME, \
    ALGEBRAIC_MODEL_COLNAME, PERCENT_BEST_COLNAME, TRANSITIVE_SCALING_COLNAME
from api.constants.techniques import DIRECT_ID
from src.analysis.techniques.best_technique import create_percent_best, create_ranks
from tests.res.smart_test import SmartTest


def create_entry(dataset):
    return {
        DATASET_COLNAME: dataset,
        TRANSITIVE_TRACE_TYPE_COLNAME: DIRECT_ID,
        ALGEBRAIC_MODEL_COLNAME: "VSM",
        AP_COLNAME: 0.5,
        LAG_COLNAME: 0.5
    }


class TestBestTechnique(SmartTest):
    data = pd.DataFrame()
    data[DATASET_COLNAME] = ["ABC"] * 2 + ["DEF"] * 2
    data[TRANSITIVE_TRACE_TYPE_COLNAME] = ["NONE"] * 4
    data[TRANSITIVE_SCALING_COLNAME] = ["GLOBAL", "INDEPENDENT"] * 2
    data[AP_COLNAME] = [2, 3, 3, 5]
    data[LAG_COLNAME] = [2, 3, 4, 5]

    """
    create_ranks
    """

    def test_create_ranks(self):
        data = create_ranks(self.data)
        self.assertTrue(RANK_COLNAME in data.columns)

        self.assertEqual(2, data[RANK_COLNAME][0])
        self.assertEqual(1, data[RANK_COLNAME][1])
        self.assertEqual(2, data[RANK_COLNAME][2])
        self.assertEqual(1, data[RANK_COLNAME][3])

    """
    percent_best
    """

    def test_percent_best(self):
        with_ranks = create_ranks(self.data)
        data = create_percent_best(with_ranks)
        data = data.set_index("technique")

        def get_percent(tech_name: str):
            return data.loc[tech_name][PERCENT_BEST_COLNAME]

        self.assertEqual(3, len(data))
        self.assertEqual(1, get_percent("INDEPENDENT"))
        self.assertEqual(0, get_percent("GLOBAL"))
        self.assertEqual(1, get_percent("NONE"))
