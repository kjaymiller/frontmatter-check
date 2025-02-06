from typer.testing import CliRunner

from frontmatter_check.cli import app

runner = CliRunner()


def test_missing_frontmatter_results_in_warning(tmp_path):
    """When you check a file that doesn't have frontmatter, return a warning only"""

    test_path = tmp_path / "test_cli"
    test_path.mkdir()
    test_file = test_path / "fake_md.md"
    test_file.write_text("There's no frontmatter in this file")

    result = runner.invoke(app, [str(test_file)])
    assert result.exit_code == 0
