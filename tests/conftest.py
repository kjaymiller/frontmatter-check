import pytest


@pytest.fixture(scope="session")
def fake_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("test_dir")


@pytest.fixture(scope="session")
def example_frontmatter():
    return """
---
name: Miles Morales
---

This is Spiderman.
"""
