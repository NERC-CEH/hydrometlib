"""Shared helpers for the calculation tests."""

import math
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import pandas as pd
import polars as pl

# Make the user guide's example package importable, so test_examples.py can run the code the docs show.
# This lives here rather than in a repo-root conftest.py because a second top-level "conftest" module
# would shadow this one, which the calculation tests import MODES/run_case/assert_allclose from.
sys.path.insert(0, str(Path(__file__).parents[1] / "docs" / "source"))

MODES = ["expr", "pl_series", "pd_series"]


def run_case(
    func: Callable[..., Any],
    columns: dict[str, Sequence[Any]],
    scalars: dict[str, Any] | None = None,
    mode: str = "expr",
) -> list[Any]:
    """Call ``func`` with ``columns`` (+ ``scalars``) in the requested input mode, return a list."""
    scalars = scalars or {}

    if mode == "expr":
        frame = pl.DataFrame(dict(columns))
        expr = func(**{name: pl.col(name) for name in columns}, **scalars)
        return frame.select(expr.alias("out")).get_column("out").to_list()

    if mode == "pl_series":
        out = func(**{name: pl.Series(name, list(values)) for name, values in columns.items()}, **scalars)
        assert isinstance(out, pl.Series)
        return out.to_list()

    if mode == "pd_series":
        out = func(**{name: pd.Series(list(values), name=name) for name, values in columns.items()}, **scalars)
        assert isinstance(out, pd.Series)
        return out.to_list()

    raise ValueError(f"unknown mode {mode!r}")


def _norm(x: Any) -> Any:
    if x is None or x is pd.NA:
        return None
    if isinstance(x, float) and math.isnan(x):
        return None
    return x


def assert_allclose(got: Sequence[Any], expected: Sequence[Any], atol: float = 1e-3) -> None:
    """Compare two sequences elementwise, treating ``None`` / ``NaN`` / ``pd.NA`` as equal."""
    got = [_norm(x) for x in got]
    expected = [_norm(x) for x in expected]
    assert len(got) == len(expected), f"length {len(got)} != {len(expected)}"
    for i, (g, e) in enumerate(zip(got, expected, strict=True)):
        if e is None or g is None:
            assert g is None and e is None, f"index {i}: {g!r} != {e!r}"
        elif isinstance(e, bool) or isinstance(g, bool):
            assert bool(g) == bool(e), f"index {i}: {g!r} != {e!r}"
        else:
            assert abs(g - e) <= atol, f"index {i}: {g} != {e} (atol={atol})"
