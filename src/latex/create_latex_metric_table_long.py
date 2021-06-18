"""
The following script is responsible for creating Table 2 of our study's paper.
Namely, this involves displaying the latex code representing the metric scores for all direct techniques,
all transitive techniques, and the best (and worst) hybrid techniques.
"""

from experiments.create_metric_table import RetrievalTechniques
from latex.create_id_table import ROW_SUFFIX
from utilities.constants import DATASET_COLUMN_ORDER
from utilities.technique_extractors import AGGREGATE_METRIC_TABLE


def query_data(df, t_dict):
    for t_key, t_val in t_dict.items():
        if t_val == "NA":
            df = df[df[t_key].isnull()]
        else:
            df = df[df[t_key] == t_val]
    assert len(df) == 1, len(df)
    return df.iloc[0]


def create_table():
    row_index = 0
    last_type = None

    for dataset in DATASET_COLUMN_ORDER:
        table_rows = []

        for _, t_id in RetrievalTechniques():
            t_type = t_id["technique_type"]

            if last_type is None:
                last_type = t_type

            if last_type == t_type:
                row_index += 1
            else:
                row_index = 1
                last_type = t_type

            row_id = t_type[0] + repr(row_index)
            curr_row = [row_id]
            t_id.update({"dataset": dataset})
            t_entry = query_data(data, t_id)
            for metric in ["ap", "auc", "lag_normalized_inverted"]:
                m_value = t_entry[metric]
                curr_row.append(repr(round(m_value, 3)))
            table_rows.append("&".join(curr_row) + ROW_SUFFIX)
        print("\n".join(table_rows))
        print("-" * 50)


if __name__ == "__main__":
    data = AGGREGATE_METRIC_TABLE.create_lag_norm_inverted(drop_old=True).table
    t_content = create_table()
    print(t_content)
