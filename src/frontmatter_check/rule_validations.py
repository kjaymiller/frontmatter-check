"""
The FrontmatterValidator is the object responsible for checking a passed in frontmatter `Post` object.
"""

import logging
import dataclasses
from typing import Any

from .logger import logger, memory_handler

_frontmatter_metadata = dict[str, Any]


@dataclasses.dataclass
class ValidationRule:
    """A Single Validation Rule Configuration"""

    field_name: str
    case_sensitivity: bool = False
    default: str | None = None
    # the `int`s below are due to being able to change your logging level values
    missing_field_logging_level: int = logging.ERROR
    null_value_logging_level: int = logging.ERROR

    @property
    def _checkable_field_name(self):
        if not self.case_sensitivity:
            return self.field_name.casefold()
        return self.field_name

    def _checkable_metadata(self, frontmatter_metadata: dict) -> dict:
        if not self.case_sensitivity:
            return {
                x.casefold(): y
                for x, y in frontmatter_metadata.items()
                if not self.case_sensitivity
            }
        return frontmatter_metadata

    def has_field(self, frontmatter_metadata: _frontmatter_metadata):
        """Checks that the frontmatter_matadata has the field"""

        if self._checkable_field_name not in self._checkable_metadata(
            frontmatter_metadata
        ):
            fail_message = f"Missing field: '{self.field_name}'"
            logger.log(
                self.missing_field_logging_level,
                fail_message,
            )
            return False

        return True

    def null_value(self, frontmatter_metadata: _frontmatter_metadata):
        """Checks that field value is not None"""

        if (
            self._checkable_metadata(frontmatter_metadata).get(
                self._checkable_field_name
            )
            is None
        ):
            fail_message = f"{self.field_name} Value is 'Null'"
            logger.log(self.null_value_logging_level, fail_message)
            return False

        return True

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
