[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Language](https://img.shields.io/github/languages/top/NERC-CEH/hydrometlib)
[![tests badge](https://github.com/NERC-CEH/hydrometlib/actions/workflows/pipeline.yml/badge.svg)](https://github.com/NERC-CEH/hydrometlib/actions)
[![Docs](https://img.shields.io/badge/docs-%F0%9F%93%9A%20online-blue)](https://nerc-ceh.github.io/hydrometlib)

# Hydrometeorology Calculation Library

A trusted library of verified and referenced hydrometeorological calculations and derivations.

## Overview

TODO

## License

This project is licensed under the [MIT license](LICENSE).

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

If you use this software, please cite it using the metadata in [`CITATION.cff`](./CITATION.cff).

Built with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [NERC-CEH/fdri-cookiecutter-pypackage](https://github.com/NERC-CEH/fdri-cookiecutter-pypackage) template.
