# HHNK Hydro Workflows

Reusable GitHub Actions workflows for all `hhnk-hydro-*` packages.

## Setup

1. Push this repository to GitHub as `HHNK/hhnk-hydro-workflows`
2. Make sure the repository is **public** (required for reusable workflows to work across repositories)

## Available Workflows

### Test Workflow (`reusable-test.yml`)

Runs tests using pixi with optional multi-OS matrix support.

```yaml
jobs:
  test:
    uses: HHNK/hhnk-hydro-workflows/.github/workflows/reusable-test.yml@main
    with:
      os: '["ubuntu-latest"]'           # optional, JSON array of OS
      run-style-check: true             # optional, default: true
      style-command: 'pixi run style-check'  # optional
      test-command: 'pixi run test'     # optional
      upload-coverage: true             # optional, default: true
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}  # optional
```

**Multi-OS example:**
```yaml
jobs:
  test:
    uses: HHNK/hhnk-hydro-workflows/.github/workflows/reusable-test.yml@main
    with:
      os: '["ubuntu-latest", "windows-latest"]'
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

### Style Check Workflow (`reusable-style.yml`)

Runs code style checks only (ruff format, ruff check).

```yaml
jobs:
  style:
    uses: HHNK/hhnk-hydro-workflows/.github/workflows/reusable-style.yml@main
    with:
      style-command: 'pixi run style-check'  # optional
```

### Publish Workflow (`reusable-publish.yml`)

Publishes package to GitHub Releases and/or PyPI.

```yaml
jobs:
  publish:
    uses: HHNK/hhnk-hydro-workflows/.github/workflows/reusable-publish.yml@main
    with:
      run-tests: true                   # optional, default: true
      build-command: 'pixi run build'   # optional
      upload-to-github: true            # optional, default: true
      upload-to-pypi: false             # optional, default: false
    secrets:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}  # only if upload-to-pypi: true
```

## Complete Example

In your repository, create `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    if: github.event_name == 'push' || github.event.pull_request.draft == false
    uses: HHNK/hhnk-hydro-workflows/.github/workflows/reusable-test.yml@main
    secrets:
      CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

And `.github/workflows/publish.yml`:

```yaml
name: Publish

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  publish:
    uses: HHNK/hhnk-hydro-workflows/.github/workflows/reusable-publish.yml@main
    secrets:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Requirements

- Repository must have a `pixi.toml` with the required tasks (`test`, `style-check`, `build`)
- For publish workflow with PyPI, configure `PYPI_API_TOKEN` secret in repository settings
- The workflows repository must be **public** for cross-repo usage

## Packages Using These Workflows

- `hhnk-hydro-core`
- `hhnk-hydro-business`
- `hhnk-hydro-gui`
- `hhnk-hydro-qgis`
- `hhnk-hydro-notebooks`



# HHNK Hydro Pre-Commit Hooks

Install the hooks locally;

- `pre-commit clean` # clears the pre-commit cache
- `pre-commit install --install-hooks --hook-type pre-commit --hook-type pre-push`

## Hook: export-pixi-requirements
This hook enables Dependabot security scanning for repositories that use Pixi.

Dependabot does not currently detect dependencies from a `pixi.toml` file. Therefore, the dependencies defined in the Pixi environment are translated into requirements files that Dependabot can automatically detect and scan.

The hook generates the following files:

- `security/conda_requirements.txt`
- `security/requirements.txt`

The files are generated based on the contents of `pixi.lock`.

The hook only runs when pixi.lock changes.

For the initial setup, run `pre-commit run export-pixi-requirements --all-files`


### Installation
Add the following to .pre-commit-config.yaml:
```yaml
  - repo: https://github.com/HHNK/hhnk-hydro-workflows
    rev: v0.1.0
    hooks:
     - id: export-pixi-requirements
```

Optionally, add a Pixi task:
```toml
export-pixi-requirements = "pre-commit run export-pixi-requirements --all-files"
```

## Hook development
To develop hooks locally, update the consuming repository (for example hhnk-hydro-core) to reference your local clone of hhnk-hydro-workflows instead of the GitHub repository.

```yaml
  - repo: <PATHTO>\hhnk-hydro-workflows
    rev: HEAD
    hooks:
      - id: export-pixi-requirements
```

After making changes to hhnk-hydro-workflows, follow these steps (do not skip any):
1. Commit the changes in `hhnk-hydro-workflows`.
2. In the target repository, clear the pre-commit cache: `pre-commit clean`
3. Reinstall the hooks: `pre-commit install --install-hooks --hook-type pre-commit --hook-type pre-push`
4. Run the hook: `pre-commit run export-pixi-requirements --all-files`


