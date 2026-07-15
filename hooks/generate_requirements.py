# TODO create shared repository to use this script as pre-commit.
import json
import subprocess
from pathlib import Path

# get folder location based on the location of this file
root = Path.cwd() / "security"

# Call pixi to get the JSON output
result = subprocess.run(["pixi", "list", "--json"], capture_output=True, text=True)
packages = json.loads(result.stdout)

# Prepare lists
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
with open(root / "requirements.txt", "w") as f:
    f.write("\n".join(pypi_packages))

# Write Conda packages
with open(root / "conda_requirements.txt", "w") as f:
    f.write("\n".join(conda_packages))

print(f"requirements.txt generated with {len(pypi_packages)} PyPI packages.")
print(f"conda_requirements.txt generated with {len(conda_packages)} Conda packages.")
