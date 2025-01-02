"""Tests all the classes and functions in src/frontmatter_check/frontmatter_validator"""

import logging

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from frontmatter_check.rule_validations import ValidationRule

settings.register_profile(
    "logging tests", suppress_health_check=[HealthCheck.function_scoped_fixture]
)
settings.load_profile("logging tests")
# ---------------------------------
# Test the ValidationRule DataClass
# ---------------------------------

# Strategies
field_names = st.text(min_size=1, max_size=50).filter(bool)
invalid_leves = st.sampled_from([logging.DEBUG, logging.CRITICAL])
valid_levels = st.sampled_from([logging.INFO, logging.WARNING, logging.ERROR])
metadata_values = st.one_of(st.none(), st.text(), st.integers(), st.booleans())


@st.composite
def metadata_dicts(draw) -> tuple[str, dict[str, str | bool | int | None]]:
    field_name = draw(field_names)
    value = draw(metadata_values)
    extra_fields = draw(
        st.dictionaries(field_names.filter(lambda x: x != field_name), metadata_values)
    )
    return field_name, {
        **extra_fields,
        **{field_name: value},
    }


@given(field_name=field_names, missing_level=valid_levels, null_level=valid_levels)
def test_validation_rule_init(field_name, missing_level, null_level):
    rule = ValidationRule(
        field_name=field_name, missing_level=missing_level, null_level=null_level
    )
    assert rule.field_name == field_name
    assert rule.missing_level == missing_level
    assert rule.null_level == null_level


@given(missing_level=valid_levels)
def test_has_field_check(caplog, missing_level):
    caplog.set_level(logging.INFO, logger="frontmatter_check")

    metadata = {}  # "missing_key" is not in the dict
    missing_key = "missing_key"
    rule = ValidationRule(missing_key, missing_level=missing_level)
    rule.has_field(metadata)
    missing_message = f"Missing field: '{missing_key}'"
    assert caplog.record_tuples == [
        (
            "frontmatter_check",
            rule.missing_level,
            missing_message,
        )
    ]
    caplog.clear()


@given(field_name_and_metadata=metadata_dicts(), null_level=valid_levels)
def test_has_null(caplog, field_name_and_metadata, null_level):
    caplog.set_level(logging.INFO, logger="frontmatter_check")
    caplog.clear()
    field_name, metadata = field_name_and_metadata
    metadata[field_name] = None
    rule = ValidationRule(field_name, null_level=null_level)
    rule.null_value(metadata)

    if field_name not in metadata:
        null_message = f"{rule.field_name} Value is 'Null'"
        assert caplog.record_tuples == (
            "frontmatter_check",
            rule.null_level,
            null_message,
        )


@given(
    field_name=field_names,
    missing_level=valid_levels,
    null_level=valid_levels,
    field_name_and_metadata=metadata_dicts(),
)
def test_check_calls_all_rules(
    mocker, field_name, missing_level, null_level, field_name_and_metadata
):
    _, metadata = field_name_and_metadata
    rule = ValidationRule(
        field_name=field_name, missing_level=missing_level, null_level=null_level
    )
    has_field = mocker.patch.object(ValidationRule, "has_field")
    has_field.reset()
    null_value = mocker.patch.object(ValidationRule, "null_value")
    null_value.reset()
    rule.check(metadata)
    has_field.assert_called_once()
    null_value.assert_called_once()


# ---------------------------------
# Test the RulesetValidator DataClass
# ---------------------------------


@st.composite
def generate_ruleset_data(draw):
    num_rules = draw(st.integers(min_value=1, max_value=5))
    rules = []
    metadata = {}

    for _ in range(num_rules):
        field = draw(field_names)
        missing_level = draw(valid_levels)
        null_level = draw(valid_levels)
        value = draw(st.one_of(st.none(), st.text()))

        rules.append(
            ValidationRule(
                field_name=field, missing_level=missing_level, null_level=null_level
            )
        )
        if draw(st.booleans()):
            metadata[field] = value

    return rules, metadata
