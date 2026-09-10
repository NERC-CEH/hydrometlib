"""Check that the committed ``.pyi`` stubs still match the calculations they describe."""

import ast
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

import hydrometlib

# What each overload's column parameters accept, in declaration order.
_KINDS = ("pl.Expr", "str", "pl.Series", "pd.Series", "np.ndarray")


def _generator() -> ModuleType:
    """Load ``scripts/gen_stubs.py``, which is a script rather than an importable package.

    Returns:
        The imported generator module
    """
    path = Path(__file__).parents[2] / "scripts" / "gen_stubs.py"
    spec = importlib.util.spec_from_file_location("gen_stubs", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _expected_stub(module: ModuleType) -> str:
    """Render the stub the generator would write for a calculation module.

    Args:
        module: The imported hydrometlib module

    Returns:
        The stub source text
    """
    generator = _generator()
    assert module.__file__ is not None
    tree = ast.parse(Path(module.__file__).read_text())
    body = "".join(
        "".join(generator.overload_for(function, kind) for kind in generator.KINDS)
        for function in generator.calculations(tree)
    )
    return generator.HEADER.format(module=module.__name__.rsplit(".", 1)[-1]) + body


def _committed_stub(module: ModuleType) -> str:
    """Read the stub committed alongside a calculation module.

    Args:
        module: The imported hydrometlib module

    Returns:
        The stub source text

    Raises:
        AssertionError: If the module has no stub beside it
    """
    assert module.__file__ is not None
    stub = Path(module.__file__).with_suffix(".pyi")
    assert stub.exists(), f"{stub.name} is missing"
    return stub.read_text()


def _declared(stub: str) -> dict[str, list[ast.FunctionDef]]:
    """Collect a stub's ``@overload`` declarations, keyed by function name.

    Args:
        stub: The stub source text

    Returns:
        A mapping of function name to its declarations, in source order
    """
    found: dict[str, list[ast.FunctionDef]] = {}
    for node in ast.parse(stub).body:
        if isinstance(node, ast.FunctionDef):
            found.setdefault(node.name, []).append(node)
    return found


def _calculations(module: ModuleType) -> set[str]:
    """Collect the public calculations a module defines itself.

    Args:
        module: The imported hydrometlib module

    Returns:
        The names of the calculations, excluding anything merely imported
    """
    return {
        name
        for name, value in vars(module).items()
        if not name.startswith("_") and callable(value) and getattr(value, "__module__", None) == module.__name__
    }


@pytest.mark.parametrize("module_name", sorted(hydrometlib.__all__))
def test_stub_matches_what_the_generator_would_write(module_name: str) -> None:
    """Test that a stub cannot drift from the signatures it describes.

    Compared as syntax trees so that formatting differences do not matter, only the declarations.
    """
    module: Any = getattr(hydrometlib, module_name)
    committed = ast.dump(ast.parse(_committed_stub(module)))
    expected = ast.dump(ast.parse(_expected_stub(module)))
    assert committed == expected, f"{module_name}.pyi is out of step with {module_name}.py - run 'make stubs'"


@pytest.mark.parametrize("module_name", sorted(hydrometlib.__all__))
def test_every_calculation_is_declared_for_every_input_kind(module_name: str) -> None:
    """Test that no calculation is left out of the stub, which would narrow it to pl.Expr for typed callers."""
    module: Any = getattr(hydrometlib, module_name)
    declared = _declared(_committed_stub(module))
    for name in _calculations(module):
        assert name in declared, f"{module_name}.pyi does not declare {name} - run 'make stubs'"
        got = len(declared[name])
        assert got == len(_KINDS), f"{module_name}.{name} has {got} overloads, expected {len(_KINDS)}"
    assert set(declared) == _calculations(module), f"{module_name}.pyi declares functions the module does not define"
