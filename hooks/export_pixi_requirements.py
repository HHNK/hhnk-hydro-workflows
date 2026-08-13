"""Export Pixi dependencies to requirements files.

This script extracts package information per environment for a configured Pixi platform
and writes:

- security/requirements-{ENVIRONMENT}.txt
- security/conda_requirements-{ENVIRONMENT}.txt

The generated files can be used by Dependabot and other tooling that
does not natively support Pixi.
"""

import argparse
import json
import subprocess
from pathlib import Path

# get folder location based on the location of this file
root = Path(__file__).parent.resolve()


def get_environments() -> list[str]:
    """Discover all pixi environments from the project."""
    result = subprocess.run(
        ["pixi", "project", "environment", "list"],
        capture_output=True,
        text=True,
    )
    environments = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("- ") and line.endswith(":"):
            env_name = line[2:-1]  # Strip "- " prefix and ":" suffix
            environments.append(env_name)
    return environments


def get_packages_for_environment(env: str) -> list[dict]:
    """Get the package list for a specific pixi environment."""
    # Use a single platform to ensure deterministic output across
    # developer machines and CI environments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--platform",
        default="linux-64",
        help="Pixi platform to export requirements for (default: linux-64).",
    )
    args = parser.parse_args()

    result = subprocess.run(
        ["pixi", "list", "--platform", args.platform, "--json", "-e", env], capture_output=True, text=True, check=True
    )
    if result.returncode != 0:
        print(f"Warning: failed to list packages for environment '{env}'")
        return []
    return json.loads(result.stdout)


def main():
    """Generate requirements files for a configured Pixi platform."""

    root = Path.cwd() / "security"

    environments = get_environments()
    print(f"Scanning environments: {environments}")

    for env in environments:
        pypi_packages: dict[str, str] = {}
        conda_packages: dict[str, str] = {}

        packages = get_packages_for_environment(env)
        for pkg in packages:
            kind = pkg.get("kind")
            name = pkg.get("name")
            version = pkg.get("version") or ""

            if kind == "pypi":
                pypi_packages[name] = version
            elif kind == "conda":
                conda_packages[name] = version

        # Format and sort for deterministic output
        pypi_lines = sorted(f"{name}=={version}" if version else name for name, version in pypi_packages.items())
        conda_lines = sorted(f"{name}=={version}" if version else name for name, version in conda_packages.items())

        # Write per-environment files
        with open(root / f"requirements-{env}.txt", "w") as f:
            f.write("\n".join(pypi_lines))

        with open(root / f"conda_requirements-{env}.txt", "w") as f:
            f.write("\n".join(conda_lines))

        print(f"  {env}: {len(pypi_lines)} PyPI, {len(conda_lines)} Conda packages.")


if __name__ == "__main__":
    main()
