"""
The FrontmatterValidator is the object responsible for checking a passed in frontmatter `Post` object.
"""

from enum import Enum
import dataclasses
import logging
import pathlib
from collections import namedtuple
from typing import Any

import yaml
import frontmatter


class ValidationLevel(Enum):
    SKIP = "skip"
    WARN = "warn"
    ERROR = "error"

    @classmethod
    def from_str(cls, value: str) -> "ValidationLevel":
        """Convert the string value to an Enum"""

        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(
                f"Invalid Validation Level {value=}. Must be one of: 'skip', 'warn', 'error'"
            )
        except AttributeError:
            raise AttributeError(
                "Validation Level cannot be empty. Must be one of: 'skip', 'warn', 'error'"
            )


@dataclasses.dataclass()
class ValidationResults:
    validates: bool = True
    errors: list = dataclasses.field(default_factory=list)
    warnings: list = dataclasses.field(default_factory=list)


SingleCheckResults = namedtuple("SingleCheckResults", ["test", "fail_message"])


@dataclasses.dataclass
class ValidationRule:
    """A Single Validation Rule Configuration"""

    field_name: str
    level: ValidationLevel = ValidationLevel.ERROR

    def __post_init__(self):
        """Checks that level is either warn or error"""
        if self.level not in (ValidationLevel.WARN, ValidationLevel.ERROR):
            raise ValueError(
                "'level' must be either ValidationLevel.WARN or ValidationLevel.ERROR"
            )

    def has_field(self, frontmatter_metadata: dict[str, Any]) -> SingleCheckResults:
        """Checks that the frontmatter_matadata has the field"""

        return SingleCheckResults(
            test=self.field_name in frontmatter_metadata,
            fail_message=f"Missing field: '{self.field_name}'",
        )

    def null_value(self, frontmatter_metadata: dict[str, Any]) -> SingleCheckResults:
        """Checks that field value is not None"""

        return SingleCheckResults(
            test=lambda _: frontmatter_metadata[self.field_name] is not None,
            fail_message=f"{self.field_name} Value is 'Null'",
        )

    def validates(self, frontmatter_metadata: dict[str, Any]) -> ValidationResults:
        """Iterates through validation tests and returns the validation results based on rule settings"""

        validation_tests: list[SingleCheckResults] = [
            self.has_field(frontmatter_metadata),
            self.null_value(frontmatter_metadata),
        ]

        validation = ValidationResults()

        for check in validation_tests:
            if not check.test:
                match self.level:
                    case ValidationLevel.ERROR:
                        validation.errors.append(check.fail_message)
                        validation.validates = False
                    case ValidationLevel.WARN:
                        validation.warnings.append(check.fail_message)

        return validation


class RulesetValidator:
    """
    Base object for the validator

    Attributes:
        ruleset: dictionary of rules to check against
    """

    rulesets: list[ValidationRule]
    validation: ValidationResults

    def __init__(self, rulesets: list[ValidationRule]):
        self.rulesets = rulesets

    def validates(self, frontmatter_metadata: dict[str, Any]) -> ValidationResults:
        """Iterates through the ruleset checking a frontmatter post for each value"""
        logging.info(
            "%s being checked for %s"
            % (
                frontmatter_metadata.keys(),
                [ruleset.field_name for ruleset in self.rulesets],
            )
        )

        for rule in self.rulesets:
            validation = rule.validates(frontmatter_metadata)

            if self.validation.validates:
                self.validation.validates = validation.validates

            self.validation.errors.extend(validation.errors)
            self.validation.warnings.extend(validation.warnings)

        return self.validation


class FrontMatterValidator:
    """
    Attributes:
        rule_validators [str]: The post type is the key and the value is a RulesetValidator
    rule_validators: dict[str, FrontmatterRuleValidator]
    settings: dict[str, dict[str, bool|str|None]]
    """

    def __init__(self):
        pass

    def get_validation_type(self, file_path: pathlib.Path) -> str:
        """
        Given a list of types containing their file_path patterns. Identify the first match

        Example:

        in yaml:
            ```yaml
            types:
            post:
                filepaths:
                - content/*.md
                ... # everything else is ignored
            microblog:
                filepaths:
                - content/microblog/*.md
            ```
        is equivalent in Python to:

        ```python
        {
            "post": ["content/*.md"],
            "microblog": ["content/microblog/*.md"],
        }
        ```

        Returns the key of the first matching pattern.
        """

        for _type, patterns in self.types.items():
            if any([file_path.full_match(pattern) for pattern in patterns]):
                return _type

    def validates(self, file_path: pathlib.Path):
        """
        - Identify the rule_validator to use
        - load the frontmatter post
        - run rule_validator.validates(frontmatter.Post, **overriding_site_rules)
        """
        pass


class FrontmatterValueDefaultLoader:
    """Class responsible for overwriting values in frontmatter as well as default function loading"""

    def add_formula(self, formula):
        pass

    def __init__(self, config_file: pathlib.Path, overwrites: bool = False):
        self.config_file = config_file
        _base_config_yaml = yaml.safe_load(self.config_file.read_text())
        self.overwrites = overwrites

    def replace_with_defaults(self, post: frontmatter.Post) -> None:
        """checks the given fronmatter.Post for missing keys and supplies the assigned defaults"""
        pass
