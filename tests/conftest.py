import pytest


@pytest.fixture(scope="session")
def fake_dir(tmp_path_factory):
    return tmp_path_factory.getbasetemp()


@pytest.fixture(scope="session")
def example_frontmatter():
    return """
---
name: Miles Morales
---

This is Spiderman.
"""


@pytest.fixture(scope="session")
def example_file(fake_dir, example_frontmatter):
    sample_filepath = fake_dir / "sample_file.md"
    sample_filepath.write_text(example_frontmatter)
    return sample_filepath
