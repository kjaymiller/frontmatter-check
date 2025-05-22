"""
The logging manager for the output of Frontmatter Check.

The errors are checked against the `memory_handler`.
Warnings are sent to `stdout` with `stdout_handler`
Errors are sent to `stderr` with `stderr_handler`
"""

import sys
import logging
from logging.handlers import MemoryHandler

logger = logging.getLogger("FrontmatterCheck")
logger.propagate = False


class WarningOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.WARNING


memory_handler = MemoryHandler(capacity=1000)
memory_handler.setLevel(logging.ERROR)

formatter = logging.Formatter("%(levelname)s - %(message)s")

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.WARNING)
stdout_handler.setFormatter(formatter)
stdout_handler.addFilter(WarningOnlyFilter())

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)
stderr_handler.setFormatter(formatter)

logger.addHandler(stdout_handler)
logger.addHandler(stderr_handler)
logger.addHandler(memory_handler)
