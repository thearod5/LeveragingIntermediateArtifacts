"""
This module is responsible for storing all of the registered experiements and providing
a command line interface to run any of them.
"""

import os
import sys
from pathlib import Path  # Python 3.6+ only
from typing import Dict, List, Type

import click

PATH_TO_ROOT = os.path.join(Path(__file__).parent.absolute())
sys.path.append(os.path.join(PATH_TO_ROOT, ".."))
sys.path.append(os.path.join(PATH_TO_ROOT, "..", "Tracer", "src"))

# TODO: imports
# pylint: disable=wrong-import-position, ungrouped-imports
from api.extension.cache import (
    Cache,
)  # pylint: disable=wrong-import-position, ungrouped-imports

# pylint: disable=wrong-import-position, ungrouped-imports
from experiments.calculate_individual_queries import (
    CalculateIndividualQueries,
)  # pylint: disable=wrong-import-position
from experiments.create_gain_correlation_table import (
    GainCorrelationTable,
)  # pylint: disable=wrong-import-position
from experiments.find_best_ranked_techniques import (
    FindBestRankedTechniques,
)  # pylint: disable=wrong-import-position

# pylint: disable=wrong-import-position, ungrouped-imports
from experiments.create_correlation_table import (
    CalculateCorrelation,
)  # pylint: disable=wrong-import-position, ungrouped-imports
from experiments.create_gain_table import (
    CalculateGain,
)  # pylint: disable=wrong-import-position
from experiments.calculate_percent_best import (
    CreateBestTechnique,
)  # pylint: disable=wrong-import-position
from experiments.experiment import Experiment  # pylint: disable=wrong-import-position
from experiments.create_metric_table import (
    CreateMetricTable,
)  # pylint: disable=wrong-import-position
from experiments.create_sampled_table import (
    CreateSampledTable,
)  # pylint: disable=wrong-import-position

REGISTERED_EXPERIMENTS: List[Type[Experiment]] = [
    CreateMetricTable,
    CreateBestTechnique,
    CalculateGain,
    CreateSampledTable,
    CalculateCorrelation,
    FindBestRankedTechniques,
    GainCorrelationTable,
    CalculateIndividualQueries,
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
if __name__ == "__main__":
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
