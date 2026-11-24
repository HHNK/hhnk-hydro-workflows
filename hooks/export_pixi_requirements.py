"""Export Pixi dependencies to requirements files.

This script extracts package information per environment for a configured Pixi platform
and writes:

- security/requirements-{ENVIRONMENT}.txt
- security/conda_requirements-{ENVIRONMENT}.txt

The generated files can be used by Dependabot and other tooling that
does not natively support Pixi. Dependabot reads both files as pip requirements, so it checks
conda packages against PyPI advisories by name. A conda package that pip cannot parse is left out,
as one such line fails the whole file: a `_`-prefixed placeholder name such as `_openmp_mutex`, or
a version outside PEP 440 such as `tzdata==2026e`.
"""

import argparse
import json
import subprocess
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement

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


def get_packages_for_environment(env: str, platform: str) -> list[dict]:
    """Get the package list for a specific pixi environment."""
    result = subprocess.run(
        ["pixi", "list", "--platform", platform, "--json", "-e", env], capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def write_requirements(path: Path, lines: list[str]) -> None:
    """Write one requirement per line, with LF on every OS, as git stores them.

    Every line ends in a newline and an environment without packages gives an empty file; otherwise the
    mixed-line-ending and end-of-file-fixer hooks rewrite the file after every export.
    """
    path.write_text("".join(f"{line}\n" for line in lines), newline="\n")


def format_requirement(name: str, version: str) -> str:
    """One requirement line: the package pinned to its version, or the bare name without one."""
    return f"{name}=={version}" if version else name


def is_pip_requirement(line: str) -> bool:
    """Whether pip parses the line as a requirement."""
    try:
        Requirement(line)
    except InvalidRequirement:
        return False
    return True


def main():
    """Generate requirements files for a configured Pixi platform."""
    # Use a single platform to ensure deterministic output across
    # developer machines and CI environments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--platform",
        default="linux-64",
        help="Pixi platform to export requirements for (default: linux-64).",
    )
    args = parser.parse_args()

    root = Path.cwd() / "security"

    environments = get_environments()
    print(f"Scanning environments: {environments}")

    for env in environments:
        pypi_packages: dict[str, str] = {}
        conda_packages: dict[str, str] = {}

        packages = get_packages_for_environment(env, args.platform)
        for pkg in packages:
            kind = pkg.get("kind")
            name = pkg.get("name")
            version = pkg.get("version") or ""

            if kind == "pypi":
                pypi_packages[name] = version
            elif kind == "conda":
                conda_packages[name] = version

        # Format and sort for deterministic output
        pypi_lines = sorted(format_requirement(name, version) for name, version in pypi_packages.items())
        conda_all = sorted(format_requirement(name, version) for name, version in conda_packages.items())
        conda_lines = [line for line in conda_all if is_pip_requirement(line)]
        conda_dropped = [line for line in conda_all if line not in conda_lines]

        # Write per-environment files
        write_requirements(root / f"requirements-{env}.txt", pypi_lines)
        write_requirements(root / f"conda_requirements-{env}.txt", conda_lines)

        print(f"  {env}: {len(pypi_lines)} PyPI, {len(conda_lines)} Conda packages.")
        if conda_dropped:
            print(f"    left out, not valid pip: {', '.join(conda_dropped)}")


if __name__ == "__main__":
    main()
