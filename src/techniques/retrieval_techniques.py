"""
The following experiment calculates all possible direct, transitive, and combined techniques.
"""
import os
from typing import Tuple, Optional

import click

from api.constants.paths import PATH_TO_TECHNIQUE_SOURCE_DATA, PATH_TO_NOTRACES_INTERMEDIARY, \
    PATH_TO_WITHTRACES_INTERMEDIARY, PATH_TO_DATA_PROCESSED, NOTRACES_ID, WITHTRACES_ID, TECHNIQUES_ID
from api.constants.processing import TRANSITIVE_TRACE_TYPE_COLNAME, DIRECT_ALGEBRAIC_MODEL_COLNAME, \
    ALGEBRAIC_MODEL_COLNAME, TECHNIQUE_AGGREGATION_COLNAME, TRANSITIVE_AGGREGATION_COLNAME, \
    TRANSITIVE_SCALING_COLNAME, TECHNIQUE_TYPE_COLNAME
from api.constants.techniques import UNDEFINED_TECHNIQUE, DIRECT_ID, COMBINED_ID, TRANSITIVE_ID
from api.experiment.cache import Cache
from api.metrics.models import Table
from api.technique.definitions.combined.technique import COMBINED_COMMAND_SYMBOL
from api.technique.definitions.direct.definition import DIRECT_COMMAND_SYMBOL
from api.technique.definitions.transitive.definition import TRANSITIVE_COMMAND_SYMBOL
from api.technique.variationpoints.aggregation.aggregation_method import AggregationMethod
from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from api.technique.variationpoints.scalers.scaling_method import ScalingMethod
from api.technique.variationpoints.tracetype.trace_type import TraceType
from api.tracer import Tracer
from src.analysis.common_operations import update_aggregate, setup_for_graph, create_graph_metrics
from src.analysis.techniques.best_technique import export_best_techniques
from src.analysis.techniques.gain import export_gain
from src.runner.experiment import Experiment
from src.runner.progress_bar_factory import create_bar
from src.runner.types import ExperimentTraceType

RETRIEVAL_TECHNIQUE_EXPERIMENT_DESCRIPTION = "This experiment calculates all direct, transitive, and combined " \
                                             "technique for some given dataset. For each technique accuracy metrics" \
                                             " are created and stored in table alonside identifying information of " \
                                             "each technique."

RETRIEVAL_TECHNIQUES_ID = "RETRIEVAL_TECHNIQUES"

EXPERIMENT_LOADING_MESSAGE = "...calculating techniques..."
TechniqueID = Tuple[Optional[AlgebraicModel],  # direct algebraic model
                    Optional[ExperimentTraceType],  # transitive experiment trace type
                    Optional[AlgebraicModel],  # transitive algebraic model
                    Optional[ScalingMethod],  # transitive scaling type
                    Optional[AggregationMethod],  # transitive aggregation method
                    Optional[AggregationMethod]]  # technique aggregation


class RetrievalTechniques:
    """
    Defines the main experiment loop for calculating a metric table for each direct, transitive, and combined
    techniques.
    """

    def __iter__(self) -> Tuple[str, str]:
        # direct
        for t_am in AlgebraicModel:
            t_id = (t_am, ExperimentTraceType.DIRECT, None, None, None, None)
            yield format_direct_technique(t_am), create_entry(t_id)

        # transitive
        for trace_type in ExperimentTraceType:
            for t_am in AlgebraicModel:
                for t_scaling in ScalingMethod:
                    for transitive_aggregation in AggregationMethod:
                        t_id = (None, trace_type, t_am, t_scaling, transitive_aggregation, None)
                        yield format_transitive_technique(t_am, t_scaling, transitive_aggregation,
                                                          trace_type), create_entry(
                            t_id)

        # combined
        for trace_type in ExperimentTraceType:  # pylint: disable=too-many-nested-blocks
            if trace_type == ExperimentTraceType.DIRECT:
                continue
            for direct_am in AlgebraicModel:
                for t_am in AlgebraicModel:
                    for t_scaling in ScalingMethod:
                        for transitive_aggregation in AggregationMethod:
                            for technique_aggregation in AggregationMethod:
                                t_id = (
                                    direct_am, trace_type, t_am, t_scaling, transitive_aggregation,
                                    technique_aggregation)
                                yield format_combined_technique(t_id), create_entry(t_id)

    def __len__(self):
        return get_n_direct() + get_n_transitive() + get_n_combined()


def calculate_technique_metric_table(dataset: str) -> Table:
    """
    Creates a metric table for each technique (direct, transitive, and combined) containing identifying information
    for each technique and the default set of accuracy metrics provided by Tracer engine.
    :param dataset: the name of the dataset
    :return: MetricTable - contains default accuracy metrics for techniques
    """
    tracer = Tracer()
    metric_table = Table()

    techniques = RetrievalTechniques()
    with create_bar(EXPERIMENT_LOADING_MESSAGE, techniques, length=len(techniques)) as techniques:
        for t_name, t_entry in techniques:
            t_metrics = tracer.get_metrics(dataset, t_name)
            metric_table.add(t_metrics, t_entry)

    return metric_table


def get_n_combined():
    """
    :return: int - the number of combined techniques
    """
    return len(AlgebraicModel) * len(ExperimentTraceType) * \
           len(AlgebraicModel) * len(ScalingMethod) * len(AggregationMethod) * len(AggregationMethod)


def get_n_transitive():
    """
    :return: int - the number of transitive techniques
    """
    return len(ExperimentTraceType) * len(AlgebraicModel) * len(ScalingMethod) * len(AggregationMethod)


def get_n_direct():
    """
    :return: int - the number of direct techniques
    """
    return len(AlgebraicModel)  # type: ignore


def create_export_path(dataset: str):
    """
    :param dataset: the dataset being experimented on
    :return: the export path for retrieval techniques experiment when applying it to given dataset
    """
    export_path: str = os.path.join(PATH_TO_TECHNIQUE_SOURCE_DATA, dataset + ".csv")
    return export_path


def prompt_for_dataset() -> str:
    """
    Prompts user for a dataset name
    :return: name of dataset given by user.
    """
    dataset: str = click.prompt("Dataset name").strip()
    assert len(dataset) > 0, "expected at least one dataset"
    return dataset


def format_direct_technique(algebraic_model: AlgebraicModel):
    """
    Creates technique definition for direct technique using specified algebraic model
    :param algebraic_model: the algebraic model used to directly compare artifacts
    :return: str - the technique definition
    """
    technique_definition = "(%s (%s NT) (0 2))" % (DIRECT_COMMAND_SYMBOL, algebraic_model.value)
    return technique_definition


def format_transitive_technique(transitive_algebraic_model: AlgebraicModel,
                                scaling_method: ScalingMethod,
                                transitive_aggregation: AggregationMethod,
                                trace_type: ExperimentTraceType):
    """
    Creates code for transitive technique by embedding direct components between top/middle
    and middle/bottom artifact layers.
    :param transitive_algebraic_model: the algebraic model of direct component techniques
    :param scaling_method: how the upper and lower similarity technique_matrices are scaled
    :param transitive_aggregation: method in which transitive scores are aggregated into one
    :param trace_type: what type of traces to use (none, lower, upper, all)
    :return: string representing lisp-like code given to Tracer to build a technique
    """
    a_trace, b_trace = get_component_trace_types(trace_type)
    upper_component = "(%s (%s %s) (0 1))" % (
        DIRECT_COMMAND_SYMBOL, transitive_algebraic_model.value, a_trace.value)

    lower_component = "(%s (%s %s) (1 2))" % (
        DIRECT_COMMAND_SYMBOL, transitive_algebraic_model.value, b_trace.value)

    transitive = "(%s (%s %s) (%s %s))" % (
        TRANSITIVE_COMMAND_SYMBOL, transitive_aggregation.value, scaling_method.value, upper_component,
        lower_component)
    return transitive


def format_combined_technique(t_id: TechniqueID):
    """
    Creates the code required to construct technique with given parameters:
    :param t_id: tuple - containing all identifying information for given technique
    :return:
    """

    d_am, trace_type, t_am, t_scaling, t_aggregation, technique_aggregation = t_id

    direct = format_direct_technique(d_am)
    transitive = format_transitive_technique(t_am,
                                             t_scaling,
                                             t_aggregation,
                                             trace_type)

    return "(%s (%s) (%s %s))" % (COMBINED_COMMAND_SYMBOL, technique_aggregation.value, direct, transitive)


def create_entry(t_id: TechniqueID) -> dict:
    """
    Creates a dictionary object containing all of the identifying information given using standardized names
    :param t_id: tuple - contains all of the information to identify direct, transitive, and combined techniques
    :return: dictionary containing all of the identifying information
    """
    d_am, trace_type, t_am, t_scaling, transitive_agg, technique_agg = t_id
    if technique_agg is None and t_am is None:
        technique_type = DIRECT_ID
    elif technique_agg is None and t_am is not None:
        technique_type = TRANSITIVE_ID
    else:
        technique_type = COMBINED_ID
    return {
        TECHNIQUE_TYPE_COLNAME: technique_type,
        DIRECT_ALGEBRAIC_MODEL_COLNAME: UNDEFINED_TECHNIQUE if d_am is None else d_am.value,
        ALGEBRAIC_MODEL_COLNAME: UNDEFINED_TECHNIQUE if t_am is None else t_am.value,
        TRANSITIVE_SCALING_COLNAME: UNDEFINED_TECHNIQUE if t_scaling is None else t_scaling.value,
        TRANSITIVE_AGGREGATION_COLNAME: UNDEFINED_TECHNIQUE if transitive_agg is None else transitive_agg.value,
        TECHNIQUE_AGGREGATION_COLNAME: UNDEFINED_TECHNIQUE if technique_agg is None else
        technique_agg.value,
        TRANSITIVE_TRACE_TYPE_COLNAME: UNDEFINED_TECHNIQUE if trace_type is None else trace_type.value
    }


def get_component_trace_types(experiment_trace_type: ExperimentTraceType):
    """
    Returns the upper and lower traces types associated with given experiment trace type
    :param experiment_trace_type: the type of tracing used (defined by experiment terminology)
    :return: tuple of two where each component is either traced or not traced
    """
    a_trace, b_trace = TraceType.NOT_TRACED, TraceType.NOT_TRACED
    if experiment_trace_type == ExperimentTraceType.LOWER:
        b_trace = TraceType.TRACED
    elif experiment_trace_type == ExperimentTraceType.UPPER:
        a_trace = TraceType.TRACED
    elif experiment_trace_type == ExperimentTraceType.ALL:
        a_trace = TraceType.TRACED
        b_trace = TraceType.TRACED
    return a_trace, b_trace


def post_processing(dataset: str, metric_table: Table):
    """
    Post processing steps:
    1. Rank the techniques
    2. Calculate gain on direct best technique
    3. Export intermediate table
    :param dataset:
    :param metric_table:
    :return:
    """
    metric_table_values = metric_table.table

    export_best_techniques(metric_table.table, dataset)
    export_gain(create_graph_metrics(metric_table.table), dataset)

    direct_mask = metric_table_values[TRANSITIVE_TRACE_TYPE_COLNAME] == ExperimentTraceType.DIRECT.value
    none_mask = metric_table_values[TRANSITIVE_TRACE_TYPE_COLNAME] == ExperimentTraceType.NONE.value
    rq1_df = metric_table_values[none_mask | direct_mask]
    rq2_df = metric_table_values[(~none_mask) | direct_mask]

    setup_for_graph(rq1_df).to_csv(os.path.join(PATH_TO_NOTRACES_INTERMEDIARY, dataset + '.csv'), index=False)
    setup_for_graph(rq2_df).to_csv(os.path.join(PATH_TO_WITHTRACES_INTERMEDIARY, dataset + '.csv'), index=False)

    no_traces_agg_path = os.path.join(PATH_TO_DATA_PROCESSED, TECHNIQUES_ID, NOTRACES_ID + '.csv')
    with_traces_agg_path = os.path.join(PATH_TO_DATA_PROCESSED, TECHNIQUES_ID, WITHTRACES_ID + '.csv')

    update_aggregate(PATH_TO_NOTRACES_INTERMEDIARY, no_traces_agg_path)
    update_aggregate(PATH_TO_WITHTRACES_INTERMEDIARY, with_traces_agg_path)

    print("No traces aggregate exported to: ", no_traces_agg_path)
    print("With traces aggregate exported to:", with_traces_agg_path)


class RetrievalTechniquesExperiment(Experiment):
    """
    Implements the Experiment interface for calculating the metric of all the retrieval techniques.
    """

    def run(self) -> Table:
        """
        calculates metric table for all techniques and applies post processing techinques defined in module
        :return: metric table with metrics
        """
        dataset_name = prompt_for_dataset()
        metric_table = calculate_technique_metric_table(dataset_name)
        post_processing(dataset_name, metric_table)
        return metric_table

    @property
    def description(self) -> str:
        """
        :return: a description of what this experiments
        """
        return RETRIEVAL_TECHNIQUE_EXPERIMENT_DESCRIPTION

    @staticmethod
    def name() -> str:
        """
        :return: the name of the experiment
        """
        return RETRIEVAL_TECHNIQUES_ID


if __name__ == "__main__":
    Cache.CACHE_ON = True
    experiment = RetrievalTechniquesExperiment()
    experiment.run()
