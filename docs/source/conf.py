# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from importlib.metadata import version as get_version

project = "hydrometlib"
copyright = "2026, UKCEH"
author = "UKCEH"
release = get_version("hydrometlib")
version = release

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_autodoc_typehints",
    "sphinx_contributors",
    "sphinx_iconify",
]

# -- Intersphinx -----------------------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "polars": ("https://docs.pola.rs/api/python/stable", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
    "numpy": ("https://numpy.org/doc/stable", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

# -- Autodoc / autosummary ---------------------------------------------------
autosummary_generate = True
autodoc_typehints = "description"
autoclass_content = "class"

# -- HTML output -------------------------------------------------------------
html_theme = "shibuya"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

html_context = {
    "license": "MIT",
}

html_theme_options = {
    "accent_color": "blue",
    # Expand the first level of every sidebar toctree by default, so the per-module
    # function lists under "Function reference" are visible without a click.
    "globaltoc_expand_depth": 1,
    "nav_links": [
        {"title": "Getting started", "url": "getting_started/installation"},
        {"title": "User guide", "url": "user_guide/flexible_inputs"},
        {"title": "Function reference", "url": "api/cosmos"},
        {"title": "Contributing", "url": "developer/contributing"},
    ],
    "github_url": "https://github.com/NERC-CEH/hydrometlib",
}

# -- Napoleon settings -------------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_param = True
napoleon_use_rtype = False
