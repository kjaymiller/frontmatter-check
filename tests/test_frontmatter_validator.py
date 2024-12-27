import pytest
from frontmatter_check.frontmatter_validator import ValidationLevel


@pytest.mark.parametrize(
    "validation_level_string, validation_level",
    ("skip", ValidationLevel.SKIP),
    ("warn", ValidationLevel.WARN),
    ("error", ValidationLevel.ERROR),
)
def test_validation_level_valid_values():
    """Test that valid string values are correctly converted to enum values"""
    assert ValidationLevel.from_str


def test_validation_level_case_insensitive():
    """Test that the conversion is case-insensitive"""
    assert ValidationLevel.from_str("SKIP") == ValidationLevel.SKIP
    assert ValidationLevel.from_str("Warn") == ValidationLevel.WARN
    assert ValidationLevel.from_str("ERROR") == ValidationLevel.ERROR
    assert ValidationLevel.from_str("sKiP") == ValidationLevel.SKIP


def test_validation_level_invalid_values():
    """Test that invalid values raise ValueError with correct message"""
    invalid_values = ["invalid", "none", "", "skipp", "warning"]

    for value in invalid_values:
        with pytest.raises(ValueError) as exc_info:
            ValidationLevel.from_str(value)

        expected_msg = f"Invalid Validation Level value='{value}'. Must be one of: 'skip', 'warn', 'error'"
        assert str(exc_info.value) == expected_msg


def test_validation_level_type_comparison():
    """Test that the returned values are correct ValidationLevel enum instances"""
    result = ValidationLevel.from_str("skip")
    assert isinstance(result, ValidationLevel)
    assert result.value == "skip"


def test_validation_level_none_input():
    """Test that None input raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        ValidationLevel.from_str(None)

    assert "object has no attribute 'lower'" in str(exc_info.value)


def test_validation_level_direct_enum_values():
    """Test that enum values are correctly set"""
    assert ValidationLevel.SKIP.value == "skip"
    assert ValidationLevel.WARN.value == "warn"
    assert ValidationLevel.ERROR.value == "error"
