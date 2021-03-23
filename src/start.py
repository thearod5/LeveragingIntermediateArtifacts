"""
This module is responsible for storing all of the registered experiements and providing
a command line interface to run any of them.
"""

import os
import sys
from pathlib import Path  # Python 3.6+ only
from typing import List, Type, Dict

import click

PATH_TO_ROOT = os.path.join(Path(__file__).parent.absolute())
sys.path.append(os.path.join(PATH_TO_ROOT, ".."))
sys.path.append(os.path.join(PATH_TO_ROOT, "..", "Tracer", "src"))

from runner.Experiment import Experiment
from techniques.retrieval_techniques import RetrievalTechniquesExperiment

REGISTERED_EXPERIMENTS: List[Type[Experiment]] = [RetrievalTechniquesExperiment]

EXPERIMENT_DECOMPOSITION = list(map(lambda e: {e.name(): e}, REGISTERED_EXPERIMENTS))
EXPERIMENT_NAME_MAP: Dict[str, Type[Experiment]] = {k: v for x in EXPERIMENT_DECOMPOSITION for k, v in x.items()}
REGISTERED_EXPERIMENT_NAMES: List[str] = list(map(lambda e: e.name(), REGISTERED_EXPERIMENTS))


@click.command()
@click.option('--experiment-name',
              prompt="What experiment would you like to run?",
              type=click.Choice(REGISTERED_EXPERIMENT_NAMES, case_sensitive=False))
def run_experiment(experiment_name):
    experiment = EXPERIMENT_NAME_MAP[experiment_name]()
    experiment.run()


if __name__ == "__main__":
    run_experiment()
    print("Done!")
