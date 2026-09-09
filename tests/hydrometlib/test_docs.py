"""Check that the function reference lists exactly the functions the library actually provides.

The lists in ``docs/source/api/`` are written by hand, and the same function is named on two pages: its
module page, and the "All calculations" overview. Nothing in Sphinx ties either list back to the code, so a
new calculation can be added and silently left undocumented. These tests make sure any new calculation has a
docs entry, otherwise it will fail the unit test run.
"""

import importlib
import re
from pathlib import Path
from types import ModuleType

import pytest

import hydrometlib

_API_DIR = Path(__file__).parents[2] / "docs" / "source" / "api"
_OVERVIEW = _API_DIR / "index.rst"

_PAGES = {
    "meteorology": "meteorology.rst",
    "evapotranspiration": "evapotranspiration.rst",
    "cosmos": "cosmos_soil_moisture.rst",
    "flux": "flux.rst",
}

_CURRENTMODULE = re.compile(r"^\.\.\s+currentmodule::\s*(\S+)\s*$")
_AUTOSUMMARY = re.compile(r"^\.\.\s+autosummary::\s*$")
_OPTION = re.compile(r"^\s+:\S+:")


def _documented_names(page: Path) -> dict[str, set[str]]:
    """Collect the names each ``autosummary`` block on a page lists, keyed by module.

    Args:
        page: The reStructuredText page to read

    Returns:
        A mapping of module name (as given by the preceding ``currentmodule``) to the set of names listed
    """
    found: dict[str, set[str]] = {}
    module: str | None = None
    in_block = False

    for line in page.read_text().splitlines():
        if match := _CURRENTMODULE.match(line):
            module = match.group(1)
            continue
        if _AUTOSUMMARY.match(line):
            assert module is not None, f"{page.name}: autosummary block with no preceding currentmodule"
            in_block = True
            continue
        if not in_block:
            continue
        if not line.strip() or _OPTION.match(line):
            continue
        if not line.startswith((" ", "\t")):  # dedent ends the block
            in_block = False
            continue
        found.setdefault(module, set()).add(line.strip())  # pyright: ignore[reportArgumentType]

    return found


def _public_functions(module: ModuleType) -> set[str]:
    """Return the names of the public calculations a module defines.

    Args:
        module: The imported hydrometlib module

    Returns:
        The public callables the module defines itself, excluding anything it merely imported
    """
    return {
        name
        for name, value in vars(module).items()
        if not name.startswith("_") and callable(value) and getattr(value, "__module__", None) == module.__name__
    }


@pytest.mark.parametrize("module_name", sorted(_PAGES))
def test_module_page_lists_every_function(module_name: str) -> None:
    """Test that a module's own reference page lists exactly the functions it provides."""
    page = _API_DIR / _PAGES[module_name]
    documented = _documented_names(page).get(f"hydrometlib.{module_name}", set())
    assert documented == _public_functions(importlib.import_module(f"hydrometlib.{module_name}")), (
        f"{page.name} is out of step with hydrometlib.{module_name}"
    )


@pytest.mark.parametrize("module_name", sorted(_PAGES))
def test_overview_page_lists_every_function(module_name: str) -> None:
    """Test that the "All calculations" page lists exactly the functions each module provides."""
    documented = _documented_names(_OVERVIEW).get(f"hydrometlib.{module_name}", set())
    assert documented == _public_functions(importlib.import_module(f"hydrometlib.{module_name}")), (
        f"{_OVERVIEW.name} is out of step with hydrometlib.{module_name}"
    )


def test_every_module_is_documented() -> None:
    """Test that no whole module is missing from the reference, so a new one cannot be overlooked."""
    assert set(hydrometlib.__all__) == set(_PAGES), "hydrometlib.__all__ has a module with no reference page"
