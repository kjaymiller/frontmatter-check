"""Tests all the classes and functions in src/frontmatter_check/frontmatter_validator"""

import logging

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from frontmatter_check.rule_validations import ValidationRule, RulesetValidator
from frontmatter_check.logger import memory_handler

logger = logging.getLogger("FrontmatterCheck")
logger.propagate = True

settings.register_profile(
    "logging tests", suppress_health_check=[HealthCheck.function_scoped_fixture]
)
settings.load_profile("logging tests")
# ---------------------------------
# Test the ValidationRule DataClass
# ---------------------------------

# Strategies
field_names = st.text(min_size=1, max_size=50).filter(bool)
invalid_level = st.sampled_from([logging.DEBUG, logging.CRITICAL])
skip_level = st.sampled_from([logging.INFO])
valid_levels = st.sampled_from([logging.WARNING, logging.ERROR])
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
        field_name=field_name,
        missing_field_logging_level=missing_level,
        null_value_logging_level=null_level,
    )
    assert rule.field_name == field_name
    assert rule.missing_field_logging_level == missing_level
    assert rule.null_value_logging_level == null_level


@given(missing_level=valid_levels)
def test_has_field_check(caplog, missing_level):
    caplog.set_level(logging.INFO, logger="FrontmatterCheck")
    caplog.clear()

    metadata = {}  # "missing_key" is not in the dict
    missing_key = "missing_key"
    rule = ValidationRule(missing_key, missing_field_logging_level=missing_level)
    rule.has_field(metadata)
    missing_message = f"Missing field: '{missing_key}'"

    if "field_name" not in metadata:
        assert caplog.record_tuples == [
            (
                "FrontmatterCheck",
                rule.missing_field_logging_level,
                missing_message,
            )
        ]


@given(field_name_and_metadata=metadata_dicts(), null_level=valid_levels)
def test_has_null(caplog, field_name_and_metadata, null_level):
    caplog.set_level(logging.INFO, logger="FrontmatterCheck")
    caplog.clear()
    field_name, metadata = field_name_and_metadata
    metadata[field_name] = None
    rule = ValidationRule(field_name, null_value_logging_level=null_level)
    rule.null_value(metadata)

    null_message = f"{rule.field_name} Value is 'Null'"
    assert caplog.record_tuples == [
        (
            "FrontmatterCheck",
            rule.null_value_logging_level,
            null_message,
        )
    ]


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
        field_name=field_name,
        missing_field_logging_level=missing_level,
        null_value_logging_level=null_level,
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
                field_name=field,
                missing_field_logging_level=missing_level,
                null_value_logging_level=null_level,
            )
        )
        if draw(st.booleans()):
            metadata[field] = value

    return rules, metadata


@given(ruleset_data=generate_ruleset_data())
def test_ruleset_validator_init(ruleset_data):
    """Test that RulesetValidator initializes correctly with given rules"""
    rules, _ = ruleset_data
    validator = RulesetValidator(rules=rules)
    assert validator.rules == rules


@given(ruleset_data=generate_ruleset_data())
def test_validates_no_errors(caplog, ruleset_data):
    """Test validation when there are no errors in the metadata"""
    rules, metadata = ruleset_data

    # Ensure all fields exist and have non-null values
    for rule in rules:
        metadata[rule.field_name] = "test_value"

    validator = RulesetValidator(rules=rules)

    # Clear any existing logs
    caplog.clear()
    memory_handler.buffer.clear()

    result = validator.validates(metadata)
    assert result is True

    # Check that no ERROR level logs were created
    error_logs = [
        record for record in memory_handler.buffer if record.levelno == logging.ERROR
    ]
    assert len(error_logs) == 0


def test_validates_with_missing_fields():
    """Test validation when fields are missing from metadata"""

    # Empty the metadata to ensure missing fields
    validator = RulesetValidator(rules=[ValidationRule(field_name="name")])

    # Clear any existing logs and set proper level
    memory_handler.buffer.clear()

    result = validator.validates({})
    assert not result

    # Check that ERROR level logs were created for each missing field
    assert "Missing field: 'name'" in [
        record.getMessage() for record in memory_handler.buffer
    ]


def test_validationrule_case_sensitivity():
    """Tests that case_sensitivity in ValidationRule"""

    test_metadata = {"test": "foo"}
    case_sensitive_rule = ValidationRule(field_name="Test", case_sensitivity=True)
    case_insensitve_rule = ValidationRule(field_name="Test", case_sensitivity=False)
    assert not case_sensitive_rule.has_field(frontmatter_metadata=test_metadata)
    assert case_insensitve_rule.has_field(frontmatter_metadata=test_metadata)
    assert case_insensitve_rule.null_value(frontmatter_metadata=test_metadata)


@given(ruleset_data=generate_ruleset_data())
def test_validates_success(caplog, ruleset_data):
    """Test validation when all fields are present and valid"""
    rules, metadata = ruleset_data

    # Ensure all fields exist with valid values
    for rule in rules:
        metadata[rule.field_name] = "valid_value"

    validator = RulesetValidator(rules=rules)

    # Clear any existing logs and set proper level
    caplog.set_level(logging.INFO, logger="frontmatter_check")
    caplog.clear()
    memory_handler.buffer.clear()

    result = validator.validates(metadata)
    assert result is True

    # Check that no ERROR level logs were created
    error_logs = [
        record for record in memory_handler.buffer if record.levelno == logging.ERROR
    ]
    assert len(error_logs) == 0  # No errors should be present


def test_validates_with_null_values():
    """Test validation when fields have null values"""
    # Set all fields to None
    metadata = {"name": None}
    validator = RulesetValidator(rules=[ValidationRule(field_name="name")])

    # Clear any existing logs and set proper level
    memory_handler.buffer.clear()

    assert not validator.validates(metadata)

    error_logs = [
        record for record in memory_handler.buffer if record.levelno == logging.ERROR
    ]
    assert len(error_logs) == 1  # One error per rule


def test_validates_mixed_errors():
    """Test validation with a mix of missing fields and null values"""
    metadata = {
        "name": None,
    }

    rules = [
        ValidationRule(field_name="name"),
        ValidationRule(field_name="description"),
    ]

    validator = RulesetValidator(rules)

    # Clear half the fields and set the other half to None
    metadata.clear()
    memory_handler.buffer.clear()
    result = validator.validates(metadata)
    assert result is False

    # Check that ERROR level logs were created appropriately
    error_logs = [
        record for record in memory_handler.buffer if record.levelno == logging.ERROR
    ]
    assert len(error_logs) == len(rules)  # One error per rule
