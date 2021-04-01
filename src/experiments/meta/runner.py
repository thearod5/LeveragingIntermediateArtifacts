"""
This module is responsible for storing all of the registered experiements and providing
a command line interface to run any of them.
"""

import os
from typing import Dict, List, Type

import click

from api.constants.paths import PATH_TO_ROOT
from api.extension.cache import (
    Cache,
)
from api.tables.table import Table
from experiments.calculate_individual_queries import (
    CalculateIndividualQueries,
)
from experiments.calculate_percent_best import (
    CreateBestTechnique,
)
from experiments.create_correlation_table import (
    CalculateCorrelation,
)
from experiments.create_datasets import CreateDatasets
from experiments.create_gain_correlation_table import (
    GainCorrelationTable,
)
from experiments.create_gain_table import (
    CalculateGain,
)
from experiments.create_metric_table import (
    CreateMetricTable,
)
from experiments.create_sampled_table import (
    CreateSampledTable,
)
from experiments.dataset_sizes import DatasetSizes
from experiments.evaluate_paths import EvaluatePaths
from experiments.find_best_ranked_techniques import (
    FindBestRankedTechniques,
)
from experiments.meta.experiment import Experiment

REGISTERED_EXPERIMENTS: List[Type[Experiment]] = [
    CreateDatasets,
    CreateMetricTable,
    CreateBestTechnique,
    CalculateGain,
    CreateSampledTable,
    CalculateCorrelation,
    GainCorrelationTable,
    CalculateIndividualQueries,
    FindBestRankedTechniques,
    EvaluatePaths,
    DatasetSizes,
]

EXPERIMENT_DECOMPOSITION = list(map(lambda e: {e.name(): e}, REGISTERED_EXPERIMENTS))
EXPERIMENT_NAME_MAP: Dict[str, Type[Experiment]] = {
    k: v for x in EXPERIMENT_DECOMPOSITION for k, v in x.items()
}
REGISTERED_EXPERIMENT_NAMES: List[str] = list(
    map(lambda e: e.name(), REGISTERED_EXPERIMENTS)
)
EXIT_COMMAND = "EXIT"
EXPERIMENT_RUN_DELIMITER = "-" * 50
WELCOME_MESSAGE = "Welcome to the experiment runner."


class Runner(Experiment):
    def run(self) -> Table:
        Cache.CACHE_ON = True

        print(WELCOME_MESSAGE, end="\n\n")

        while True:
            experiment_name = click.prompt(
                "What experiment would you like to run?",
                type=click.Choice(
                    REGISTERED_EXPERIMENT_NAMES + [EXIT_COMMAND], case_sensitive=False
                ),
            )
            if experiment_name == EXIT_COMMAND:
                print("\n\nGoodbye!")
                break
            print(EXPERIMENT_RUN_DELIMITER)
            print("Running Experiment: %s" % experiment_name)
            experiment = EXPERIMENT_NAME_MAP[experiment_name]()
            result = experiment.run()
            for e_path in experiment.export_paths:
                print(
                    "Exported: ",
                    os.path.normpath(
                        os.path.relpath(e_path, start=os.path.join(PATH_TO_ROOT, ".."))
                    ),
                )
            print(EXPERIMENT_RUN_DELIMITER)
        return Table()

    def name(self) -> str:
        pass
