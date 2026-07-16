"""Export Pixi dependencies to requirements files.

This script extracts package information for a configured Pixi platform
and writes:

- security/requirements.txt
- security/conda_requirements.txt

The generated files can be used by Dependabot and other tooling that
does not natively support Pixi.
"""

import argparse
import json
import subprocess
from pathlib import Path


def main() -> None:
    """Generate requirements files for a configured Pixi platform."""

    root = Path.cwd() / "security"

    # Use a single platform to ensure deterministic output across
    # developer machines and CI environments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--platform",
        default="linux-64",
        help="Pixi platform to export requirements for (default: linux-64).",
    )
    args = parser.parse_args()

    # Call pixi to get the JSON output
    try:
        result = subprocess.run(
            ["pixi", "list", "--platform", args.platform, "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error calling pixi: {e.stderr}")
        raise e

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
    pypi_file = root / "requirements.txt"
    conda_file = root / "conda_requirements.txt"

    # Write packages with an empty line at end of file for end-of-file-fixer hook.
    pypi_file.write_text("\n".join(pypi_packages) + "\n")
    conda_file.write_text("\n".join(conda_packages) + "\n")

    print(f"{pypi_file} generated with {len(pypi_packages)} PyPI packages.")
    print(f"{conda_file} generated with {len(conda_packages)} Conda packages.")


if __name__ == "__main__":
    main()
