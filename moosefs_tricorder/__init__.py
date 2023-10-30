# Copyright 2023 Joe Block <jpb@unixorn.net>
import logging
from importlib import metadata

# Read version from the package metadata
__version__ = metadata.version(__package__)

logger = logging.getLogger(__name__)
