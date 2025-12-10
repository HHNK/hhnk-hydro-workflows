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
