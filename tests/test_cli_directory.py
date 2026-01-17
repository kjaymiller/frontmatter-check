from typer.testing import CliRunner
from frontmatter_check.cli import app

runner = CliRunner()


def test_check_directory(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    (d / "a.md").write_text("---\ntitle: A\n---\n")
    (d / "b.md").write_text("---\ntitle: B\n---\n")

    config = tmp_path / "config.yaml"
    config.write_text("""
patterns:
  - name: posts
    pattern: "**/*.md"
    rules:
      - field_name: title
        level: error
""")

    result = runner.invoke(app, [str(d), "--config-file", str(config)])
    assert result.exit_code == 0
    assert "Checking File" in result.stdout
    assert "a.md" in result.stdout
    assert "b.md" in result.stdout
