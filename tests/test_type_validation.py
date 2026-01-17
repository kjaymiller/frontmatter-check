import logging
import datetime
import pytest
from frontmatter_check.rule_validations import ValidationRule
from frontmatter_check.logger import memory_handler


@pytest.fixture(autouse=True)
def clear_log_buffer():
    memory_handler.buffer.clear()
    yield
    memory_handler.buffer.clear()


@pytest.mark.parametrize(
    "expected_type, value, is_valid",
    [
        ("str", "hello", True),
        ("str", 123, False),
        ("int", 123, True),
        ("int", "123", False),
        ("bool", True, True),
        ("bool", "True", False),
        ("list", [1, 2], True),
        ("list", "not a list", False),
        ("dict", {"a": 1}, True),
        ("dict", "not a dict", False),
        ("datetime", datetime.date(2023, 1, 1), True),
        ("datetime", datetime.datetime(2023, 1, 1, 12, 0, 0), True),
        ("datetime", "2023-01-01", False),
    ],
)
def test_validate_type(expected_type, value, is_valid):
    rule = ValidationRule(field_name="test_field", type=expected_type)
    metadata = {"test_field": value}

    assert rule.validate_type(metadata) == is_valid


def test_check_logs_error_on_invalid_type():
    rule = ValidationRule(field_name="test_field", type="int")
    metadata = {"test_field": "not an int"}

    rule.check(metadata)

    error_logs = [
        record for record in memory_handler.buffer if record.levelno == logging.ERROR
    ]
    assert len(error_logs) == 1
    assert "Value is not of type 'int'" in error_logs[0].getMessage()


def test_validate_type_handles_none_value():
    # If value is None, validate_type should return True (as null check is separate)
    rule = ValidationRule(field_name="test_field", type="int")
    metadata = {"test_field": None}

    assert rule.validate_type(metadata) is True


def test_check_does_not_validate_type_if_null():
    # If value is None and null logging level is ERROR, validate_type should not run/log
    # But check() handles the logic.
    rule = ValidationRule(field_name="test_field", type="int")
    metadata = {"test_field": None}

    rule.check(metadata)

    # Should log "Value is 'Null'" but NOT "Value is not of type 'int'"
    error_logs = [
        record.getMessage()
        for record in memory_handler.buffer
        if record.levelno == logging.ERROR
    ]

    assert any("Value is 'Null'" in msg for msg in error_logs)
    assert not any("Value is not of type" in msg for msg in error_logs)
