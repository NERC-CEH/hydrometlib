# Hydrometeorology Calculation Library

A trusted library of verified and referenced hydrometeoroloigical calculations and derivations.

* [GitHub](https://github.com/NERC-CEH/hydrometlib/) | [Documentation](https://NERC-CEH.github.io/hydrometlib/)

## Features

* TODO

## Documentation

Documentation is built with [Sphinx](https://www.sphinx-doc.org/) and deployed to GitHub Pages.

* **Live site:** https://NERC-CEH.github.io/hydrometlib/
* **Preview locally:** `make docs-serve` (serves at http://localhost:8000)
* **Build:** `make docs-build`

API documentation is auto-generated from docstrings using [sphinx-autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html).

## Development

To set up for local development:

```bash
git clone git@github.com:NERC-CEH/hydrometlib.git
cd hydrometlib
uv sync
```

Run tests:

```bash
uv run pytest
```

Run quality checks (format, lint, type check, test):

```bash
make qa
```

## Citation

If you use this software, please cite it using the metadata in [`CITATION.cff`](./CITATION.cff).

## Licence

MIT

Built with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [NERC-CEH/fdri-cookiecutter-templates](https://github.com/NERC-CEH/fdri-cookiecutter-templates) template.
