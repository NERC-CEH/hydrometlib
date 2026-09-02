"""Toy calculations wrapped with :func:`flexible`, for the dispatch tests.

These live in their own module so that ``_dispatch_fns.pyi`` can give them the same
overloaded stubs the real calculation modules get - a module's own ``.pyi`` is only
consulted when another module imports it, never when type-checking its own source.
"""

import polars as pl

from hydrometlib._dispatch import flexible


@flexible
def add(a: pl.Expr, b: pl.Expr) -> pl.Expr:
    """Add two columns."""
    return a + b


@flexible
def scale(col: pl.Expr, factor: float) -> pl.Expr:
    """Multiply a column by a scalar factor."""
    return col * factor
