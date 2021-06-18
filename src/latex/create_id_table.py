"""
Responsible for creating the latex for the table
giving each technique an id
"""
from api.constants.techniques import DIRECT_ID, HYBRID_ID, TRANSITIVE_ID
from api.extension.experiment_types import ExperimentTraceType
from experiments.create_metric_table import TechniqueID, technique_iterator

COLUMNS = ["Approach", "ID", "Model"]
ROW_SUFFIX = "\\\\ \\hline"
NA_VAL = "\cellcolor{gray!50}"
SHORT_NAMES = {"INDEPENDENT": "IND", "GLOBAL": "GLB"}


def create_table():
    """
    Returns string consisting all a row per technique where ids are given
    first come first serve.
    :return:
    """
    table_rows = []
    row_index = 0
    last_type = None
    for _, t_id in technique_iterator():
        t_type = get_technique_type(t_id)
        if last_type is None:
            last_type = t_type

        if last_type == t_type:
            row_index += 1
        else:
            row_index = 1
            last_type = t_type

        row_id = t_type[0] + repr(row_index)
        table_rows.append(create_row(row_id, t_id))
    return "\n".join(table_rows)


def create_row(row_id: str, t_id: TechniqueID):
    """
    Returns the formatted latex row of given technqiue
    :return:
    """
    t_type = get_technique_type(t_id)
    t_id = t_id[:1] + t_id[2:]
    t_labels = [t.value if t is not None else NA_VAL for t in t_id]
    t_labels = [t if t not in SHORT_NAMES else SHORT_NAMES[t] for t in t_labels]
    return "&".join([row_id, t_type] + t_labels) + ROW_SUFFIX


def get_technique_type(t_id: TechniqueID):
    if t_id[1] == ExperimentTraceType.DIRECT:
        return DIRECT_ID.title()

    if t_id[-1] is not None:
        return HYBRID_ID.title()

    return TRANSITIVE_ID.title()


if __name__ == "__main__":
    id_table = create_table()
    print(id_table)
