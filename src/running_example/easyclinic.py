import numpy as np

from api.tracer import Tracer
from utilities.technique_extractors import (
    get_best_direct_technique,
    get_best_hybrid_technique,
    get_best_transitive_technique,
)

if __name__ == "__main__":
    tracer = Tracer()
    d_name = "EasyClinic"
    direct_technique = get_best_direct_technique(d_name)
    transitive_technique = get_best_transitive_technique(d_name)
    hybrid_technique = get_best_hybrid_technique(d_name)

    """
    Direct
    """
    direct_score = tracer.get_metrics(d_name, direct_technique)[0].ap
    direct_individual_metrics = tracer.get_metrics(
        d_name, direct_technique, summary_metrics=False
    )
    direct_scores = [m.ap for m in direct_individual_metrics]
    print(f"Direct: {direct_score}:{np.mean(direct_scores)}")

    """
    Transitive
    """
    transitive_score = tracer.get_metrics(d_name, transitive_technique)[0].ap
    transitive_individual_metrics = tracer.get_metrics(
        "EasyClinic", transitive_technique, summary_metrics=False
    )
    transitive_scores = [m.ap for m in transitive_individual_metrics]
    print(f"Transitive: {transitive_score}:{np.mean(transitive_score)}")

    """
    Hybrid
    """
    hybrid_score = tracer.get_metrics(d_name, hybrid_technique)[0].ap
    hybrid_individual_metrics = tracer.get_metrics(
        "EasyClinic", hybrid_technique, summary_metrics=False
    )
    hybrid_scores = [m.ap for m in hybrid_individual_metrics]
    print(f"Hybrid: {hybrid_score}:{np.mean(hybrid_scores)}")

    print("Gain:", (hybrid_score - direct_score))
    print("Percent Gain:", (hybrid_score - direct_score) / direct_score)
