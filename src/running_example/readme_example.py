from api.tables.metric_table import MetricTable
from api.tracer import Tracer

if __name__ == "__main__":
    dataset_name = "EasyClinic"
    direct_technique = "(. (LSI NT) (0 2))"
    transitive_technique = "(x (PCA GLOBAL) ((. (LSI NT) (0 1)) (. (LSI NT) (1 2))))"
    hybrid_technique = f"(o (MAX) ({direct_technique} {transitive_technique}))"

    technique_definitions = [
        ("direct", direct_technique),
        ("transitive", transitive_technique),
        ("hybrid", hybrid_technique),
    ]

    metric_table = MetricTable()
    tracer = Tracer()

    for t_name, t_def in technique_definitions:
        t_metrics = tracer.get_metrics(dataset_name, t_def)
        metric_table.add(t_metrics, {"name": t_name})

    print(metric_table.table)
