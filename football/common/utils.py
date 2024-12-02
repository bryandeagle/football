import logging
import sys
from os import path

import yaml

# Configure logging
logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format="%(levelname)s: %(message)s"
)
log = logging.getLogger(__name__)

# Configuration dictionary
base = path.dirname(path.abspath(__file__))
with open(path.join(base, "..", "..", "config.yml"), "rt") as f:
    config = yaml.safe_load(f)
