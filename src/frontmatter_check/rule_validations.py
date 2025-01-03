"""
The FrontmatterValidator is the object responsible for checking a passed in frontmatter `Post` object.
"""

import dataclasses
import logging
from logging.handlers import MemoryHandler
from typing import Any

logger = logging.getLogger("FrontmatterCheck")
logger.propagate = False

memory_handler = MemoryHandler(capacity=1000)
memory_handler.setLevel(logging.ERROR)

formatter = logging.Formatter("%(levelname)s - %(message)s")
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
console.setFormatter(formatter)

logger.addHandler(console)
logger.addHandler(memory_handler)

_frontmatter_metadata = dict[str, Any]


@dataclasses.dataclass
class ValidationRule:
    """A Single Validation Rule Configuration"""

    field_name: str
    default: str | None
    # the `int`s below are due to being able to change your logging level values
    missing_field_logging_level: int = logging.ERROR
    null_value_logging_level: int = logging.ERROR

    def has_field(self, frontmatter_metadata: _frontmatter_metadata):
        """Checks that the frontmatter_matadata has the field"""

        if self.field_name not in frontmatter_metadata:
            fail_message = f"Missing field: '{self.field_name}'"
            logger.log(
                self.missing_field_logging_level,
                fail_message,
            )
            return False

        return True

    def null_value(self, frontmatter_metadata: _frontmatter_metadata):
        """Checks that field value is not None"""

        if frontmatter_metadata.get(self.field_name) is None:
            fail_message = f"{self.field_name} Value is 'Null'"
            logger.log(self.null_value_logging_level, fail_message)
            return False

    def check(self, frontmatter_metadata: _frontmatter_metadata):
        if not self.has_field(frontmatter_metadata):
            return
        self.null_value(frontmatter_metadata)


rules = list[ValidationRule]


@dataclasses.dataclass
class RulesetValidator:
    """Base object for the validator"""

    rules: rules

    def validates(self, frontmatter_metadata: _frontmatter_metadata) -> bool:
        """Iterates through the rules checking a frontmatter post for each value"""
        # clear the memory_handler buffer

        for rule in self.rules:
            rule.check(frontmatter_metadata)

        errors = [
            record
            for record in memory_handler.buffer
            if record.levelno == logging.ERROR
        ]
        return not errors
