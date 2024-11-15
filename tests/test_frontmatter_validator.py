import yaml

import frontmatter
from hypothesis import given, strategies as st
import pytest


from frontmatter_check import frontmatter_validator

base_json = st.fixed_dictionaries(
    {},
    optional={
        "name": st.fixed_dictionaries(
            {}, optional={"default": st.text(), "warning": st.booleans()}
        )
    },
)


@pytest.fixture(scope="session")
def fake_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("test_dir")


@given(base_json)
def test_frontmattervalidator_init(fake_dir, base_json):
    yaml_config = yaml.dump(base_json)
    fake_config_file = fake_dir / "test_config.yaml"
    fake_config_file.write_text(yaml_config)

    """create a new frontmatterValidator"""

    new_validator = frontmatter_validator.FrontmatterValidator(
        config_file=fake_config_file
    )

    assert new_validator.config_file == fake_config_file
    # TODO: Add test for if there is a ruleset that it has a name
    # TODO: Add test for if there is a ruleset that it has a default that matches the default
    # TODO: Add test for if there is a ruleset that it has a warning that matches the warning


good_frontmatter = """
---
name: Miles Morales
---

This is Spiderman.
"""

bad_frontmatter = """
---
age: 16
___

This is Spiderman.
"""


@pytest.mark.parametrize(
    "frontmatter_text, validation, error",
    (
        (good_frontmatter, True, []),
        (bad_frontmatter, False, ["name"]),
    ),
)
def test_validation_possibilities(frontmatter_text: str, validation: bool, error: list):
    """Tests that frontmatter is parsed correctly"""
    test_validator = frontmatter_validator.FrontmatterValidator()
    test_validator.ruleset = {"name": {"default": None, "warning": False}}
    assert test_validator.validates(frontmatter.loads(frontmatter_text)) == (
        validation,
        error,
    )
