import pathlib

import pytest
from typer.testing import CliRunner

from frontmatter_check.cli import app


@pytest.fixture
def runner():
    return CliRunner(mix_stderr=False)


def test_app_success_no_error(
    runner: CliRunner, fake_dir: pathlib.Path, example_file: pathlib.Path
):
    """Test that app returns error when no files are provided"""
    config_file = fake_dir / "config_file.yaml"
    config_file.write_text("name:")
    args = [str(example_file), "--config-file", str(config_file)]
    result = runner.invoke(app, args)
    print(vars(result))
    assert result.exit_code == 0
    assert not result.stdout.strip()
    assert not result.stderr.strip()


def test_app_failure(runner, fake_dir, example_file):
    """Test that app returns error when no files are provided"""
    config_file = fake_dir / "config_file.yaml"
    config_file.write_text("age:")
    args = [str(example_file), "--config-file", str(config_file)]
    result = runner.invoke(app, args)
    assert result.exit_code == 1
    assert str(example_file) in result.stderr.replace("\n", "")
    assert "age" in result.stderr
    assert not result.stdout.strip()


def test_app_warning(runner, fake_dir, example_file):
    """Tests that warnings pass the information to standard out but the result code is 0"""
    config_file = fake_dir / "config_file.yaml"
    config_file.write_text("age:\n  warning: true")
    args = [str(example_file), "--config-file", str(config_file)]
    result = runner.invoke(app, args)
    print(vars(result))
    assert result.exit_code == 0
    assert str(example_file) in result.stdout.replace("\n", "")
    assert "age" in result.stdout
