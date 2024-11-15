"""
The FrontmatterValidator is the object responsible for checking a passed in frontmatter `Post` object
"""

import logging
import pathlib
from collections import defaultdict
from typing import Any, TypedDict

import frontmatter
import yaml

DEFAULT_CONFIG_FILE_PATH = pathlib.Path(".frontmatter_check_config.yaml")


class RULESET_FROM_DICT_TYPE(TypedDict):
    default: Any
    warning: bool


class FrontmatterValidator:
    """
    Base object for the validator

    Attributes:
        ruleset: dictionary of rules to check against
        overwrite: should the file overwrite

    """

    ruleset: dict[str, RULESET_FROM_DICT_TYPE] = defaultdict()

    def __init__(self, config_file: pathlib.Path = DEFAULT_CONFIG_FILE_PATH):
        if not config_file.exists():
            return
        self.config_file = config_file
        _base_config_yaml = yaml.safe_load(self.config_file.read_text())

        for name, rule in _base_config_yaml.items():
            self.add_validator(name, rule)

    def add_validator(self, name: str, rule: RULESET_FROM_DICT_TYPE) -> None:
        """Adds a defined dictionary set to the ruleset"""
        if rule:
            self.ruleset[name] = {
                "default": rule.get("default", None),
                "warning": rule.get("warning", False),
            }
        else:
            self.ruleset[name] = {
                "default": None,
                "warning": False,
            }

    def validates(self, post: frontmatter.Post):
        validates = True
        errors = []

        for name, rule in self.ruleset.items():
            print(f"{name=}, {rule=}")
            print(f"{post.metadata=}")

            if name not in post.metadata.keys():
                errors.append(name)

                if not rule["warning"]:
                    validates = False

        return (validates, errors)
