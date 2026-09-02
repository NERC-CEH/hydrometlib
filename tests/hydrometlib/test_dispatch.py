import builtins
from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd
import polars as pl
import pytest
from _dispatch_fns import add, scale
from polars.testing import assert_series_equal


class TestExpressionMode:
    def test_expr_in_expr_out(self) -> None:
        """Test that Polars expressions in gives a Polars expression out."""
        result = add(pl.col("x"), pl.col("y"))
        assert isinstance(result, pl.Expr)
        df = pl.DataFrame({"x": [1.0, 2.0], "y": [10.0, 20.0]}).with_columns(result.alias("out"))
        assert df["out"].to_list() == [11.0, 22.0]

    def test_column_name_strings(self) -> None:
        """Test that column name strings are promoted to Polars expressions."""
        result = add("x", "y")
        assert isinstance(result, pl.Expr)
        df = pl.DataFrame({"x": [1.0], "y": [2.0]}).select(result.alias("out"))
        assert df["out"].to_list() == [3.0]

    def test_scalar_passthrough(self) -> None:
        """Test that scalar arguments pass through untouched in expression mode."""
        result = scale(pl.col("x"), 3.0)
        df = pl.DataFrame({"x": [1.0, 2.0]}).select(result.alias("out"))
        assert df["out"].to_list() == [3.0, 6.0]


class TestPolarsSeriesMode:
    def test_series_in_series_out(self) -> None:
        """Test that Polars Series in gives a Polars Series named after the function out."""
        out = add(pl.Series("x", [1.0, 2.0, 3.0]), pl.Series("y", [4.0, 5.0, 6.0]))
        assert isinstance(out, pl.Series)
        assert_series_equal(out, pl.Series("add", [5.0, 7.0, 9.0]))

    def test_scalar_passthrough(self) -> None:
        """Test that scalar arguments pass through untouched in Polars Series mode."""
        out = scale(pl.Series("x", [1.0, 2.0]), 10.0)
        assert out.to_list() == [10.0, 20.0]

    def test_unequal_length_raises(self) -> None:
        """Test that Polars Series of differing lengths raise a ValueError."""
        with pytest.raises(ValueError, match="same length"):
            add(pl.Series("x", [1.0, 2.0]), pl.Series("y", [1.0]))


class TestPandasSeriesMode:
    def test_series_in_series_out(self) -> None:
        """Test that pandas Series in gives a pandas Series named after the function out."""
        out = add(pd.Series([1.0, 2.0, 3.0]), pd.Series([4.0, 5.0, 6.0]))
        assert isinstance(out, pd.Series)
        assert out.to_list() == [5.0, 7.0, 9.0]
        assert out.name == "add"

    def test_index_is_ignored_positional_alignment(self) -> None:
        """Test that pandas Series are aligned positionally, so mismatched indexes are ignored."""
        a = pd.Series([1.0, 2.0, 3.0], index=[10, 20, 30])
        b = pd.Series([4.0, 5.0, 6.0], index=[1, 2, 3])
        out = add(a, b)
        assert out.to_list() == [5.0, 7.0, 9.0]

    def test_scalar_passthrough(self) -> None:
        """Test that scalar arguments pass through untouched in pandas Series mode."""
        out = scale(pd.Series([1.0, 2.0]), 5.0)
        assert out.to_list() == [5.0, 10.0]


class TestNumpyMode:
    def test_array_in_array_out(self) -> None:
        """Test that numpy arrays in gives a numpy array out."""
        out = add(np.array([1.0, 2.0, 3.0]), np.array([4.0, 5.0, 6.0]))
        assert isinstance(out, np.ndarray)
        assert out.tolist() == [5.0, 7.0, 9.0]

    def test_scalar_passthrough(self) -> None:
        """Test that scalar arguments pass through untouched in numpy mode."""
        out = scale(np.array([1.0, 2.0]), 10.0)
        assert out.tolist() == [10.0, 20.0]

    def test_unequal_length_raises(self) -> None:
        """Test that numpy arrays of differing lengths raise a ValueError."""
        with pytest.raises(ValueError):
            add(np.array([1.0, 2.0]), np.array([1.0]))


class TestBadMixes:
    """Every column argument must be the same kind, matching the overloads in the .pyi stubs."""

    def test_mixed_expr_and_column_name(self) -> None:
        """Test that mixing an expression with a column name raises a TypeError."""
        with pytest.raises(TypeError):
            add(pl.col("a"), "b")  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa deliberately wrong type

    def test_mixed_expr_and_series(self) -> None:
        """Test that mixing a Polars expression with a Series raises a TypeError."""
        with pytest.raises(TypeError):
            add(pl.col("a"), pl.Series("y", [2.0]))  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa deliberately wrong type

    def test_mixed_polars_and_pandas_series(self) -> None:
        """Test that mixing Polars and pandas Series raises a TypeError."""
        with pytest.raises(TypeError):
            add(pl.Series("x", [1.0]), pd.Series([2.0]))  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa deliberately wrong type

    def test_mixed_numpy_and_polars_series(self) -> None:
        """Test that mixing a numpy array with a Polars Series raises a TypeError."""
        with pytest.raises(TypeError):
            add(np.array([1.0]), pl.Series("y", [2.0]))  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa deliberately wrong type

    def test_mixed_column_name_and_numpy(self) -> None:
        """Test that mixing a column name with a numpy array raises a TypeError."""
        with pytest.raises(TypeError):
            add("a", np.array([1.0]))  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa deliberately wrong type

    def test_scalars_do_not_count_as_columns(self) -> None:
        """Test that a constant argument never triggers the same-type rule."""
        assert isinstance(scale(pl.col("x"), 3.0), pl.Expr)


class TestOptionalExtras:
    def test_pandas_without_pyarrow(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that pandas input without pyarrow installed raises a helpful ModuleNotFoundError."""
        real_import = builtins.__import__

        def no_pyarrow(
            name: str,
            _globals: Mapping[str, object] | None = None,
            _locals: Mapping[str, object] | None = None,
            fromlist: Sequence[str] = (),
            level: int = 0,
        ) -> object:
            if name == "pyarrow":
                raise ModuleNotFoundError("No module named 'pyarrow'")
            return real_import(name, _globals, _locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", no_pyarrow)
        with pytest.raises(ModuleNotFoundError, match=r"requires the 'pandas' extra"):
            add(pd.Series([1.0]), pd.Series([2.0]))


class TestUnsupportedArguments:
    def test_number_for_a_column_parameter(self) -> None:
        """Test that a bare number where a column is expected raises a TypeError."""
        with pytest.raises(TypeError):
            add(pl.Series("x", [1.0]), 2.0)  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa deliberately wrong type

    def test_list_for_a_column_parameter(self) -> None:
        """Test that a list where a column is expected raises a TypeError."""
        with pytest.raises(TypeError):
            add(pl.Series("x", [1.0]), [2.0])  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa deliberately wrong type

    def test_array_for_a_constant_parameter(self) -> None:
        """Test that a numpy array where a constant is expected raises a TypeError."""
        with pytest.raises(TypeError):
            scale(pl.Series("x", [1.0]), np.array([2.0]))  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa deliberately wrong type

    def test_none_for_a_constant_parameter(self) -> None:
        """Test that None where a constant is expected raises a TypeError."""
        with pytest.raises(TypeError):
            scale(pl.Series("x", [1.0]), None)  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa deliberately wrong type

    def test_bool_for_a_constant_parameter(self) -> None:
        """Test that a bool where a constant is expected raises a TypeError."""
        with pytest.raises(TypeError):
            scale(pl.Series("x", [1.0]), True)

    def test_numpy_scalar_is_a_valid_constant(self) -> None:
        """Test that numpy numeric scalars are accepted where a constant is expected."""
        out = scale(pl.Series("x", [1.0, 2.0]), np.float64(10.0))
        assert out.to_list() == [10.0, 20.0]


class TestMetadata:
    def test_wraps_preserves_identity(self) -> None:
        """Test that the decorator preserves the wrapped function's name, docstring and __wrapped__."""
        assert add.__name__ == "add"
        assert add.__doc__ == "Add two columns."
        assert hasattr(add, "__wrapped__")
