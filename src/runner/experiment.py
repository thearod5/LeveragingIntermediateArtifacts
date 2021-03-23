"""
The following module is responsible for defining an interface for any experiment producing a final table.
After extending and creating an experiment register it in the start.py file so that a user can access all
of this projects experiments in one place.
"""
from abc import ABC, abstractmethod

from api.metrics.models import Table


class Experiment(ABC):
    """
    Interface for running experiment under a common interface
    """

    @abstractmethod
    def run(self) -> Table:
        """
        :return: Table - the output of the experiment
        """

    @property
    @abstractmethod
    def description(self) -> str:
        """
        :return: str - the description for this experiment
        """

    @staticmethod
    @abstractmethod
    def name() -> str:
        """
        :return: str - the name of the experiment
        """