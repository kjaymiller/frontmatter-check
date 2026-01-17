import nox
import subprocess
import shutil
import re
import os


def get_pyenv_python_paths():
    """
    Discover available python versions from pyenv and return a list of full paths.
    Falls back to simple version strings if pyenv is not available or fails.
    """
    # Default fallback
    default_versions = ["3.10", "3.11", "3.12", "3.13", "3.14"]

    if not shutil.which("pyenv"):
        return default_versions

    try:
        # Get list of versions
        output = subprocess.check_output(["pyenv", "versions", "--bare"], text=True)
        versions = [v.strip() for v in output.splitlines()]

        # Map major.minor to latest installed patch version
        found_versions = {}
        for v in versions:
            match = re.match(r"^(\d+\.\d+)\.\d+$", v)
            if match:
                major_minor = match.group(1)

                # Check if this major.minor is one we care about (optional, but good practice to filter)
                # Let's support everything found, or maybe just 3.10+
                if float(major_minor) < 3.10:
                    continue

                # Compare versions to keep latest
                if major_minor not in found_versions:
                    found_versions[major_minor] = v
                else:
                    current = found_versions[major_minor]
                    # Simple comparison assuming version format
                    if list(map(int, v.split("."))) > list(
                        map(int, current.split("."))
                    ):
                        found_versions[major_minor] = v

        paths = []
        # Sort by version number
        for key in sorted(
            found_versions.keys(), key=lambda x: list(map(int, x.split(".")))
        ):
            version = found_versions[key]
            try:
                # Get the prefix (path) for this version
                prefix = subprocess.check_output(
                    ["pyenv", "prefix", version], text=True
                ).strip()
                python_path = os.path.join(prefix, "bin", "python")
                paths.append(python_path)
            except subprocess.CalledProcessError:
                continue

        if paths:
            return paths
        return default_versions

    except Exception:
        return default_versions


# Get dynamic versions or fallback
PYTHON_VERSIONS = get_pyenv_python_paths()


@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    """Run the test suite."""
    session.install(".[dev]")
    session.run("pytest")
