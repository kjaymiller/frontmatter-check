import pathlib

import pytest
from typer.testing import CliRunner

from frontmatter_check.cli import app


@pytest.fixture
def runner():
    return CliRunner()


def test_app_success_no_error(runner, fake_dir, example_frontmatter):
    """Test that app returns error when no files are provided"""

    file_name = "test_app_success_no_error.md"
    test_file = fake_dir / file_name
    test_file.write_text(example_frontmatter)
    config_file = pathlib.Path("test_app_success_no_error.yaml")
    config_file.write_text("name:")
    result = runner.invoke(app, [test_file, "--config_file", config_file])
    assert result.exit_code == 1


def test_app_failure(runner, fake_dir, example_frontmatter):
    """Test that app returns error when no files are provided"""

    file_name = "test_app_failure.md"
    test_file = fake_dir / file_name
    test_file.write_text(example_frontmatter)
    config_file = pathlib.Path("test_app_failure.yaml")
    config_file.write_text("age:")
    print(f"{str(test_file.absolute())=}", f"{config_file.absolute()=}")
    result = runner.invoke(
        app, [str(test_file.absolute()), "--config_file", str(config_file.absolute())]
    )
    assert result.exit_code == 0
