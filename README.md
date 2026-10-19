[![PyPI](https://img.shields.io/pypi/v/hydrometlib.svg)](https://pypi.org/project/hydrometlib/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/NERC-CEH/hydrometlib/blob/main/LICENSE)
![Language](https://img.shields.io/github/languages/top/NERC-CEH/hydrometlib)
[![tests badge](https://github.com/NERC-CEH/hydrometlib/actions/workflows/pipeline.yml/badge.svg)](https://github.com/NERC-CEH/hydrometlib/actions)
[![Docs](https://img.shields.io/badge/docs-%F0%9F%93%9A%20online-blue)](https://nerc-ceh.github.io/hydrometlib)

# Hydrometeorology Calculation Library

A trusted library of verified and referenced hydrometeorological calculations and derivations.

## Overview

`hydrometlib` is a small collection of standard calculations used to turn raw hydrometeorological
measurements into derived quantities: net radiation, potential evapotranspiration, absolute humidity, soil moisture
from cosmic-ray neutron counts, and more. Each one is a single function you call with the data types you already have.

- **Flexible inputs**: call every function with a Polars expression, a column name, a Polars Series, a pandas Series
  or a NumPy array, and get the result back in the same form. Site attributes, such as a sensor height or latitude,
  take a plain number or a column.
- **Referenced and tested**: every calculation cites the paper or standard it comes from, and is checked against
  known-good values across all supported input types.
- **Trusted source**: developed and maintained by [UKCEH](https://www.ceh.ac.uk/) as part of the
  [Floods and Droughts Research Infrastructure (FDRI)](https://fdri.org.uk/).

See the [quick start](https://nerc-ceh.github.io/hydrometlib/getting_started/quick_start.html) for example calculations
using Polars, pandas and NumPy, and the [calculation library](https://nerc-ceh.github.io/hydrometlib/api/index.html) for
every function with its inputs, units and source.

## Installation

```bash
pip install hydrometlib
```

or with uv:

```bash
uv add hydrometlib
```

pandas and NumPy inputs need the matching extra, e.g. `pip install "hydrometlib[pandas]"`.
See the [installation guide](https://nerc-ceh.github.io/hydrometlib/getting_started/installation.html) for details.

## License

This project is licensed under the [MIT license](https://github.com/NERC-CEH/hydrometlib/blob/main/LICENSE).

## Contributing

Contributions are welcome. Please feel free to submit a Pull Request.

1. Clone the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure your code passes all tests and follows the coding style before submitting a PR.
See **developer setup** below for more information.

## Developer Setup

This is for active development on the hydrometlib package itself.

### Requirements

#### Install uv

[Official instructions](https://docs.astral.sh/uv/getting-started/installation/)

### Clone the repository

```bash
git clone https://github.com/NERC-CEH/hydrometlib.git
cd hydrometlib
```

### Setting up and activating a virtual environment

```commandline
uv sync
source .venv/bin/activate
```

### Linting
Linting uses ruff using the config in pyproject.toml
```
ruff check --fix
```

### Formatting
Formating uses ruff using the config in pyproject.toml which follows the default black settings.
```
ruff format .
```

### Testing
Testing is done using pytest and tests are in the /tests directory.
```
pytest
```

### Pre commit hooks
Run below to setup the pre-commit hooks.
```
git config --local core.hooksPath .githooks/
```
This will set this repo up to use the git hooks in the `.githooks/` directory.
The hook runs `ruff format --check` and `ruff check` to prevent commits that are not formatted correctly or have errors.
The hook intentionally does not alter the files, but informs the user which command to run.

## Documentation

For full documentation, visit https://nerc-ceh.github.io/hydrometlib/

To build the documentation locally:

```bash
# Install documentation dependencies (but they are included by default)
uv sync --group docs

# Build the documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

## Citation

If you use this software, please cite it using the metadata in [`CITATION.cff`](https://github.com/NERC-CEH/hydrometlib/blob/main/CITATION.cff).

Built with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [NERC-CEH/fdri-cookiecutter-pypackage](https://github.com/NERC-CEH/fdri-cookiecutter-pypackage) template.
