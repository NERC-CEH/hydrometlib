"""Generate the calculation modules' ``.pyi`` stubs from their signatures.

Each calculation is a pure Polars expression wrapped in ``@flexible``, which also accepts column names strings,
Polars Series, Pandas Series, and NumPy arrays. The accepted types are declared as one ``@overload`` per input kind
in a stub.

The kinds are spelled out rather than tied together with a constrained ``TypeVar``. A TypeVar expresses
"every column argument is the same kind" more directly, but not every editor models one, and one that collapses it to
a single constraint reports valid pandas and NumPy calls as errors.

These overloads cannot live on the functions themselves: an overload declared next to an implementation must be
consistent with it, and these deliberately are not, since the implementation only ever takes a ``pl.Expr``.
Keeping them in a stub also leaves the implementations annotated ``pl.Expr``, so their bodies stay type checked.

The stubs are derived from the implementation signatures rather than written by hand, so they cannot drift.
Run ``make stubs`` after adding or changing a calculation; ``tests/hydrometlib/test_overloads.py`` fails if
what is committed no longer matches the source.
"""

import ast
import subprocess
import sys
from pathlib import Path

# The parameter categories, as annotated on an implementation. A data column carries measured values;
# an Attribute is a site attribute that may instead be given as the single number it usually is.
COLUMN = "pl.Expr"
OPTIONAL_COLUMN = "pl.Expr | None"
ATTRIBUTE = "Attribute"
OPTIONAL_ATTRIBUTE = "Attribute | None"
CONSTANT = "float"

# What each overload's column parameters accept, and what that overload returns. A column name is the
# one kind whose result differs from its argument. ``pl.Expr`` leads deliberately - see the module
# docstring.
KINDS = {
    COLUMN: COLUMN,
    "str": COLUMN,
    "pl.Series": "pl.Series",
    "pd.Series": "pd.Series",
    "np.ndarray": "np.ndarray",
    CONSTANT: "float | None",
}

HEADER = '''"""Type stubs for ``hydrometlib.{module}``.

Auto-generated from the module's signatures by ``make stubs``.
"""

from typing import overload

import numpy as np
import pandas as pd
import polars as pl

'''


def calculations(tree: ast.Module) -> list[ast.FunctionDef]:
    """Collect the ``@flexible``-decorated functions a module defines, in source order.

    Args:
        tree: The parsed module

    Returns:
        The calculations to declare overloads for
    """
    return [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and any(ast.unparse(decorator) == "flexible" for decorator in node.decorator_list)
    ]


def overload_for(function: ast.FunctionDef, kind: str) -> str:
    """Render one overload declaration for a calculation.

    Args:
        function: The calculation to declare
        kind: What a column parameter accepts, one of :data:`KINDS`

    Returns:
        The declaration, as source text
    """
    args = function.args
    named = [a.arg for a in args.args]
    defaults = dict(zip(named[len(named) - len(args.defaults) :], [ast.unparse(d) for d in args.defaults], strict=True))

    parameters = []
    for argument in args.args:
        annotation = ast.unparse(argument.annotation) if argument.annotation else ""
        if annotation == COLUMN:
            annotation = kind
        elif annotation == OPTIONAL_COLUMN:
            annotation = f"{kind} | None"
        elif annotation == ATTRIBUTE:
            annotation = CONSTANT if kind == CONSTANT else f"{kind} | {CONSTANT}"
        elif annotation == OPTIONAL_ATTRIBUTE:
            annotation = f"{CONSTANT} | None" if kind == CONSTANT else f"{kind} | {CONSTANT} | None"
        parameter = f"{argument.arg}: {annotation}"
        if argument.arg in defaults:
            parameter += f" = {defaults[argument.arg]}"
        parameters.append(parameter)

    return f"@overload\ndef {function.name}({', '.join(parameters)}) -> {KINDS[kind]}: ...\n"


def generate(module: Path) -> Path:
    """Write the stub for one calculation module.

    Args:
        module: Path to the module's ``.py`` file

    Returns:
        The path written
    """
    tree = ast.parse(module.read_text())
    body = "".join("".join(overload_for(function, kind) for kind in KINDS) for function in calculations(tree))
    stub = module.with_suffix(".pyi")
    stub.write_text(HEADER.format(module=module.stem) + body)
    return stub


def main() -> int:
    """Regenerate every calculation module's stub and format the result.

    Returns:
        Process exit code.
    """
    modules = sorted(p for p in Path("src/hydrometlib").glob("*.py") if not p.name.startswith("_"))
    written = [generate(module) for module in modules]
    subprocess.run(["ruff", "format", "--quiet", *map(str, written)], check=True)
    for stub in written:
        print(f"wrote {stub}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
