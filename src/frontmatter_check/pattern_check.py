"""
Pattern check is used to check against multiple patterns.
"""

import dataclasses
import logging
import pathlib

import frontmatter
import yaml

from .rule_validations import (
    RulesetValidator,
    ValidationRule,
)

_VALID_LOGGING_STRINGS = {
    "skip": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}

FRONTMATTER_CHECK_LOGGING_LEVEL = logging.ERROR


def convert_error_strings(
    error_string: str | int,
):
    """Convert the error strings to the appropriate logging level"""

    if isinstance(error_string, str):
        return _VALID_LOGGING_STRINGS[error_string]

    return error_string


def _to_validation_rule(rule: dict) -> ValidationRule:
    """convert the dictionary version of the validation rules to a ValidationRule"""
    missing_field_logging_level = convert_error_strings(
        rule.get("is_missing", rule.get("level", logging.ERROR))
    )
    null_value_logging_level = convert_error_strings(
        rule.get("is_null", rule.get("level", logging.ERROR))
    )

    return ValidationRule(
        field_name=rule.get("field_name", None),
        default=rule.get("default", None),
        missing_field_logging_level=missing_field_logging_level,
        null_value_logging_level=null_value_logging_level,
    )


@dataclasses.dataclass
class PatternRuleset:
    """
    Pattern for the yaml files

    Example PatternRuleset:
    {
        "name": "Docs"
        "pattern": "docs/*.md"
        "rules": [
                {
                    "field_name": "title",
                    "level": "error",
                },
                {
                    "field_name": "author",
                    "level": "error",
                },
        ],
    }
    """

    name: str
    pattern: str
    rules: RulesetValidator

    @classmethod
    def from_dict(cls, config_dict):
        rules = RulesetValidator(
            [_to_validation_rule(rule) for rule in config_dict.get("rules")]
        )
        logging.debug(rules)
        return cls(
            name=config_dict.get("name"),
            pattern=config_dict.get("pattern"),
            rules=rules,
        )


def _check_pattern(pattern_ruleset: PatternRuleset, file_path: pathlib.Path):
    return file_path.full_match(pattern_ruleset.pattern)


class FrontmatterPatternMatchCheck:
    """
    Example PatternSet:
    [
        {
            "name": "Blog Posts"
            "pattern": "posts/*.md"
            "rules": [
                    {
                        "field_name": "date",
                        "level": "error",
                        default: python.datetime.datetime(2025, 1, 1, 0, 0, 0, tz_info=0),
                    },
                    {
                        "field_name": "title",
                        "level": "error",
                    },
            ],
        },
        {
            "name": "Docs"
            "pattern": "docs/*.md"
            "rules": [
                    {
                        "field_name": "title",
                        "level": "error",
                    },
            ],
        },
    ]
    """

    pattern_sets: list[PatternRuleset]

    def __init__(self, *pattern_rulesets):
        self.pattern_sets = [
            PatternRuleset.from_dict(rule_set) for rule_set in pattern_rulesets
        ]
        logging.debug(self.__dict__)

    def validates(
        self,
        frontmatter_file: pathlib.Path,
    ):
        """Iterates through the ruleset"""
        frontmatter_metadata = frontmatter.load(
            str(frontmatter_file.absolute())
        ).metadata

        _validates = True

        if not frontmatter_metadata:
            logging.warning("No Frontmatter Found for %s" % frontmatter_file)
            return _validates

        for pattern in self.pattern_sets:
            if _check_pattern(pattern, frontmatter_file):
                logging.debug(
                    "Checking %s against %s" % (frontmatter_file, pattern.name)
                )
                if not pattern.rules.validates(frontmatter_metadata):
                    _validates = False
                # TODO: Implement fail fast here.

        return _validates

    @classmethod
    def from_yaml_config(cls, config_file: pathlib.Path):
        """Create a FrontmatterPatternCheck object with rules from a yaml_file"""
        with open(config_file, mode="rt") as yaml_file:
            config = {}

            for config_section in yaml.safe_load_all(yaml_file):
                config.update(config_section)

            if not config:
                raise ValueError("Invalid Config File: must convert to a dictionary")

        if settings := config.get("settings", None):
            if level := settings.get("level", None):
                global FRONTMATTER_CHECK_LOGGING_LEVEL
                FRONTMATTER_CHECK_LOGGING_LEVEL = level

        return FrontmatterPatternMatchCheck(*config["patterns"])
