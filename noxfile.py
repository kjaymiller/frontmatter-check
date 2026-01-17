import nox

# Define the supported python versions
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    """Run the test suite."""
    session.install(".[dev]")
    session.run("pytest")
