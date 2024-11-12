"""
The FronmatterValidator is the object responsible for checking a passed in frontmatter `Post` object
"""

import pathlib
from collections import defaultdict
from typing import Any, TypedDict

import frontmatter
import yaml

DEFAULT_CONFIG_FILE_PATH = pathlib.Path(".frontmatter_check_config.yaml")


class RULESET_FROM_DICT_TYPE(TypedDict):
    default: Any
    warning: bool


class FronmatterValidator:
    """
    Base object for the validator

    Attributes:
        ruleset: dictionary of rules to check against
        overwrite: should the file overwrite

    """

    ruleset: dict[str, RULESET_FROM_DICT_TYPE] = defaultdict()
    overwrite: bool

    def __init__(self, config_file: pathlib.Path = DEFAULT_CONFIG_FILE_PATH):
        self.config_file = config_file
        _base_config_yaml = yaml.safe_load(self.config_file.read_text())
        self.overwrite = _base_config_yaml.get("overwrite", True)

        for name, rule in _base_config_yaml.items():
            self.add_validator(name, rule)

    def add_validator(self, name: str, rule: RULESET_FROM_DICT_TYPE) -> None:
        """Adds a defined dictionary set to the ruleset"""
        self.ruleset[name] = {
            "default": rule.get("default", None),
            "warning": rule.get("warning", False),
        }

    def validates(self, post: frontmatter.Post):
        validates = True
        errors = []

        for name, rule in self.ruleset.items():
            if rule not in post.metadata:
                errors.append(name)

                if not rule["warning"]:
                    validates = False

            if self.overwrite:
                if default := rule["default"]:
                    post.metadata[name] = default

        return (validates, errors)
