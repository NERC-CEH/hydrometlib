"""Check that the overloads give callers the types they declare."""

from typing import assert_type

import numpy as np
import pandas as pd
import polars as pl
import pytest

from hydrometlib import cosmos, evapotranspiration, meteorology


def test_column_names_give_an_expression() -> None:
    """Test that column-name strings infer a Polars expression, ready for select or with_columns."""
    assert_type(meteorology.net_radiation("swin", "swout", "lwin", "lwout"), pl.Expr)
    assert_type(cosmos.absolute_humidity_factor("q", 7.0), pl.Expr)


def test_expressions_give_an_expression() -> None:
    """Test that Polars expressions infer a Polars expression."""
    assert_type(meteorology.net_radiation(pl.col("a"), pl.col("b"), pl.col("c"), pl.col("d")), pl.Expr)


def test_each_series_kind_gives_the_same_kind_back() -> None:
    """Test that the eager input kinds each infer their own type as the result."""
    polars = pl.Series([1.0])
    assert_type(meteorology.net_radiation(polars, polars, polars, polars), pl.Series)

    pandas = pd.Series([1.0])
    assert_type(meteorology.net_radiation(pandas, pandas, pandas, pandas), "pd.Series")

    numpy = np.array([1.0])
    assert_type(meteorology.net_radiation(numpy, numpy, numpy, numpy), np.ndarray)


def test_constants_stay_separate_from_columns() -> None:
    """Test that a site attribute does not take part in the column kind, so it can differ from it."""
    assert_type(cosmos.absolute_humidity_factor(pl.Series([1.0]), 7.0), pl.Series)
    assert_type(cosmos.d86(pl.Series([25.0]), pl.Series([1000.0]), 0.01, 1.4, 0.02, 5.0), pl.Series)


def test_an_optional_column_can_be_omitted_or_given() -> None:
    """Test that omitting an optional column keeps the result kind of the columns that were passed."""
    series = pl.Series([1.0])
    assert_type(
        evapotranspiration.potential_evapotranspiration_30min(series, series, series, series, series, series),
        pl.Series,
    )
    assert_type(
        evapotranspiration.potential_evapotranspiration_30min(
            series, series, series, series, series, series, wind_height=series
        ),
        pl.Series,
    )


def test_mixing_column_kinds_is_rejected() -> None:
    """Test that the constrained type parameter refuses a call mixing kinds, as dispatch does at runtime.

    ``_decide_mode`` raises ``TypeError`` for these at runtime; the point here is that they no longer
    reach runtime for a caller who type-checks.
    """
    polars, pandas, numpy = pl.Series([1.0]), pd.Series([1.0]), np.array([1.0])
    with pytest.raises(TypeError, match="must be the same type"):
        meteorology.net_radiation(polars, pandas, numpy, polars)  # pyright: ignore[reportCallIssue, reportArgumentType]
