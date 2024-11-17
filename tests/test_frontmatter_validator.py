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


@pytest.mark.parametrize(
    "rule, validation, error",
    (
        ({"name": {"default": None, "warning": False}}, True, []),
        ({"age": {"default": None, "warning": False}}, False, ["age"]),
    ),
)
def test_validation_possibilities(
    example_frontmatter: str,
    rule: dict[str, dict[str, None | bool]],
    validation: bool,
    error: list,
):
    """Tests that frontmatter is parsed correctly"""
    test_validator = frontmatter_validator.FrontmatterValidator()
    test_validator.ruleset = rule
    assert test_validator.validates(frontmatter.loads(example_frontmatter)) == (
        validation,
        error,
    )
