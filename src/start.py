"""
This module is responsible for storing all of the registered experiements and providing
a command line interface to run any of them.
"""

import os
import sys
from pathlib import Path  # Python 3.6+ only

PATH_TO_ROOT = os.path.join(Path(__file__).parent.absolute())
sys.path.append(os.path.join(PATH_TO_ROOT, ".."))
sys.path.append(os.path.join(PATH_TO_ROOT, "..", "Tracer", "src"))

from experiments.meta.runner import Runner  # pylint: disable=wrong-import-position

if __name__ == "__main__":
    Runner().run()
