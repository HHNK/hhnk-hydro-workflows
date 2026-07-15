"""Export Pixi dependencies to requirements files.

This script extracts package information from the current Pixi
environment and writes:

- security/requirements.txt
- security/conda_requirements.txt

The generated files can be used by Dependabot and other tooling that
does not natively support Pixi.
"""

import json
import subprocess
from pathlib import Path


def main() -> None:
    """Generate requirements files from the current Pixi environment."""

    root = Path.cwd() / "security"

    # Call pixi to get the JSON output
    result = subprocess.run(
        ["pixi", "list", "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    packages = json.loads(result.stdout)

    # Prepare lists for PyPI and Conda packages and fill with the package name and version.
    pypi_packages = []
    conda_packages = []

    for pkg in packages:
        kind = pkg.get("kind")
        name = pkg.get("name")
        version = pkg.get("version")
        line = f"{name}=={version}" if version else name

        if kind == "pypi":
            pypi_packages.append(line)
        elif kind == "conda":
            conda_packages.append(line)

    # Write PyPI packages
    root.mkdir(exist_ok=True)
    with open(root / "requirements.txt", "w") as f:
        f.write("\n".join(pypi_packages))

    # Write Conda packages
    with open(root / "conda_requirements.txt", "w") as f:
        f.write("\n".join(conda_packages))

    print(f"{root / 'requirements.txt'} generated with {len(pypi_packages)} PyPI packages.")
    print(f"{root / 'conda_requirements.txt'} generated with {len(conda_packages)} Conda packages.")


if __name__ == "__main__":
    main()
