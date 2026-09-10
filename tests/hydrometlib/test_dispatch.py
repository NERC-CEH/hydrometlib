import builtins
from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd
import polars as pl
import pytest
from _dispatch_fns import add, add_optional, offset, offset_optional, scale
from polars.testing import assert_series_equal

from hydrometlib import evapotranspiration, meteorology
from hydrometlib._dispatch import _column_annotation


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


class TestOptionalColumn:
    """A parameter annotated ``Column | None`` may be omitted, and then plays no part in dispatch."""

    def test_omitted_in_expr_mode(self) -> None:
        """Test that omitting the optional column returns an expression built from the other columns."""
        result = add_optional("x")
        assert isinstance(result, pl.Expr)
        df = pl.DataFrame({"x": [1.0, 2.0]}).select(result.alias("out"))
        assert df["out"].to_list() == [1.0, 2.0]

    def test_explicit_none_matches_omitted(self) -> None:
        """Test that passing ``None`` explicitly behaves the same as omitting the argument."""
        out = add_optional(pl.Series("x", [1.0, 2.0]), None)
        assert_series_equal(out, pl.Series("add_optional", [1.0, 2.0]))

    def test_provided_optional_column_is_used(self) -> None:
        """Test that a supplied optional column is treated like any other column argument."""
        out = add_optional(pl.Series("x", [1.0, 2.0]), pl.Series("y", [10.0, 20.0]))
        assert_series_equal(out, pl.Series("add_optional", [11.0, 22.0]))

    def test_omitted_does_not_force_a_mode(self) -> None:
        """Test that the omitted column does not clash with pandas Series in the other argument."""
        out = add_optional(pd.Series([1.0, 2.0]))
        assert isinstance(out, pd.Series)
        assert out.to_list() == [1.0, 2.0]

    def test_omitted_is_exempt_from_the_equal_length_check(self) -> None:
        """Test that the omitted column is ignored when Series lengths are compared."""
        out = add_optional(pl.Series("x", [1.0, 2.0, 3.0]))
        assert out.to_list() == [1.0, 2.0, 3.0]

    def test_provided_optional_column_must_match_kind(self) -> None:
        """Test that a supplied optional column still has to match the other column arguments."""
        with pytest.raises(TypeError):
            add_optional(pl.Series("x", [1.0]), "y")  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa deliberately wrong type


class TestMetadata:
    def test_wraps_preserves_identity(self) -> None:
        """Test that the decorator preserves the wrapped function's name, docstring and __wrapped__."""
        assert add.__name__ == "add"
        assert add.__doc__ == "Add two columns."
        assert hasattr(add, "__wrapped__")


class TestSiteAttribute:
    """A parameter marked ``Attribute`` takes a column, or the single number it usually is."""

    def test_number_in_expr_mode(self) -> None:
        """Test that an attribute number is broadcast alongside an expression."""
        out = pl.DataFrame({"x": [1.0, 2.0]}).select(offset(pl.col("x"), 10.0).alias("out"))
        assert out["out"].to_list() == [11.0, 12.0]

    def test_number_in_column_name_mode(self) -> None:
        """Test that an attribute number is broadcast alongside a column name."""
        out = pl.DataFrame({"x": [1.0, 2.0]}).select(offset("x", 10.0).alias("out"))
        assert out["out"].to_list() == [11.0, 12.0]

    def test_number_in_polars_series_mode(self) -> None:
        """Test that an attribute number does not change a Polars Series result."""
        out = offset(pl.Series("x", [1.0, 2.0]), 10.0)
        assert isinstance(out, pl.Series)
        assert out.to_list() == [11.0, 12.0]

    def test_number_in_pandas_series_mode(self) -> None:
        """Test that an attribute number does not change a pandas Series result."""
        out = offset(pd.Series([1.0, 2.0]), 10.0)
        assert isinstance(out, pd.Series)
        assert out.to_list() == [11.0, 12.0]

    def test_number_in_numpy_mode(self) -> None:
        """Test that an attribute number does not change a NumPy array result."""
        out = offset(np.array([1.0, 2.0]), 10.0)
        assert isinstance(out, np.ndarray)
        assert out.tolist() == [11.0, 12.0]

    def test_attribute_may_still_be_a_column(self) -> None:
        """Test that marking a parameter an attribute does not stop it being a column."""
        out = offset(pl.Series("x", [1.0, 2.0]), pl.Series("by", [10.0, 20.0]))
        assert out.to_list() == [11.0, 22.0]

    def test_number_is_exempt_from_the_equal_length_check(self) -> None:
        """Test that an attribute number is broadcast rather than length-checked against the columns."""
        out = offset(pl.Series("x", [1.0, 2.0, 3.0]), 10.0)
        assert out.to_list() == [11.0, 12.0, 13.0]

    def test_number_does_not_decide_the_mode(self) -> None:
        """Test that an attribute number never triggers the same-kind rule, so it pairs with any kind."""
        assert isinstance(offset(pd.Series([1.0]), 2.0), pd.Series)
        assert isinstance(offset(pl.Series("x", [1.0]), 2.0), pl.Series)

    def test_optional_attribute_omitted_number_or_column(self) -> None:
        """Test that an optional attribute can be omitted, given as a number, or given as a column."""
        x = pl.Series("x", [1.0, 2.0])
        assert offset_optional(x).to_list() == [1.0, 2.0]
        assert offset_optional(x, 10.0).to_list() == [11.0, 12.0]
        assert offset_optional(x, pl.Series("by", [10.0, 20.0])).to_list() == [11.0, 22.0]

    def test_a_data_column_still_refuses_a_number(self) -> None:
        """Test that only attributes take a number while real columns are present."""
        with pytest.raises(TypeError, match="is a data column"):
            offset(2.0, pl.Series("by", [1.0]))  # pyright: ignore[reportCallIssue, reportArgumentType]  # noqa deliberately wrong type


class TestAllConstantCall:
    """Giving every column argument as a number evaluates the calculation for that one set of values."""

    def test_returns_a_number_not_an_expression(self) -> None:
        """Test that an all-constant call is evaluated rather than handed back as an expression."""
        assert add(1.0, 2.0) == 3.0

    def test_mixes_data_columns_and_attributes(self) -> None:
        """Test that an all-constant call covers attributes as well as data columns."""
        assert offset(1.0, 10.0) == 11.0

    def test_constant_parameters_are_unaffected(self) -> None:
        """Test that a parameter which was never a column still takes its number."""
        assert scale(3.0, 10.0) == 30.0

    def test_null_by_design_comes_back_as_none(self) -> None:
        """Test that a calculation which yields null for these values returns None, not a number."""
        assert meteorology.albedo(0.0, 5.0, 1.0) is None

    def test_a_boolean_calculation_returns_a_bool(self) -> None:
        """Test that a calculation returning a boolean gives one back rather than a float."""
        assert meteorology.is_snow_day(0.6, 0.35, 0.5) is True

    def test_reference_value(self) -> None:
        """Test an all-constant call against a known result, so evaluation is not merely type-correct."""
        # FAO-56 Example 14: 10 m s-1 measured at 10 m corrects to 7.48 m s-1 at 2 m.
        got = evapotranspiration.wind_speed_height_correction(10.0, 10.0)
        assert got is not None
        assert abs(got - 7.48) < 0.01

    def test_optional_column_may_be_omitted(self) -> None:
        """Test that omitting an optional attribute still counts as an all-constant call."""
        assert offset_optional(1.0) == 1.0


def test_a_non_column_union_is_not_an_optional_column() -> None:
    """Test that only ``pl.Expr | None`` marks an optional column, so other unions stay constants."""
    assert _column_annotation(float | None) == (False, False, False)
