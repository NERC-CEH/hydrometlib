"""Toy calculations wrapped with :func:`flexible`, for the dispatch tests.

These live in their own module so that ``_dispatch_fns.pyi`` can give them the same
overloaded stubs the real calculation modules get - a module's own ``.pyi`` is only
consulted when another module imports it, never when type-checking its own source.
"""

import polars as pl

from hydrometlib._dispatch import Attribute, flexible


@flexible
def add(a: pl.Expr, b: pl.Expr) -> pl.Expr:
    """Add two columns."""
    return a + b


@flexible
def scale(col: pl.Expr, factor: float) -> pl.Expr:
    """Multiply a column by a scalar factor."""
    return col * factor


@flexible
def add_optional(a: pl.Expr, b: pl.Expr | None = None) -> pl.Expr:
    """Add ``b`` to ``a``, or return ``a`` unchanged when ``b`` is omitted."""
    return a if b is None else a + b


@flexible
def offset(col: pl.Expr, by: Attribute) -> pl.Expr:
    """Add a site attribute to a column; ``by`` may be a column or the single number it usually is."""
    return col + by


@flexible
def offset_optional(col: pl.Expr, by: Attribute | None = None) -> pl.Expr:
    """Add ``by`` to ``col``, or return ``col`` unchanged when the attribute is omitted."""
    return col if by is None else col + by
