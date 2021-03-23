from enum import Enum


class ExperimentTraceType(Enum):
    DIRECT = "direct"
    NONE = "none"
    UPPER = "upper"
    LOWER = "lower"
    ALL = "all"


class SamplingExperiment(Enum):
    TRACES = "traces"
    ARTIFACTS = "artifacts"
