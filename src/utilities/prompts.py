"""
This module contains all of the user prompts for all defined experiments in start.py.
"""
import click

from api.constants.processing import DATASET_COLUMN_ORDER, SAMPLING_METHODS


def prompt_for_dataset() -> str:
    """
    Prompts user for a dataset name
    :return: name of dataset given by user.
    """
    dataset_name = click.prompt(
        "Please select a dataset: ",
        type=click.Choice(DATASET_COLUMN_ORDER, case_sensitive=False),
    )
    return dataset_name


def prompt_for_sampling_method() -> str:
    """
    Prompts user to select one of the two sampling methods
    :return: str - the enum value of the sampling method selected
    """
    sampling_method = click.prompt(
        "Please select a sampling method: ",
        type=click.Choice(SAMPLING_METHODS, case_sensitive=False),
    )
    return sampling_method
