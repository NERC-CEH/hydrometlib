"""Input dispatch for the calculation functions.

The calculation functions in this package are written as pure Polars expressions: they take ``pl.Expr`` arguments
and return a ``pl.Expr``. The :func:`flexible` decorator lets callers use them with whatever they happen to have:

==============  ==============  ============================================================
In              Out             Notes
==============  ==============  ============================================================
``pl.Expr``     ``pl.Expr``
``str``         ``pl.Expr``     A column name, converted to ``pl.col()`` internally.
``pl.Series``   ``pl.Series``
``pd.Series``   ``pd.Series``   Requires the ``pandas`` extra library installation.
``np.ndarray``  ``np.ndarray``  Requires the ``numpy`` extra library installation.
==============  ==============  ============================================================

A parameter annotated ``pl.Expr | None`` is an optional column: callers may omit it, and the calculation then
receives ``None`` and chooses a fallback.
"""

import functools
import inspect
import numbers
import sys
import types
from collections.abc import Callable
from typing import Any, Literal, Union, get_args, get_origin

import polars as pl

Kind = Literal["expr", "pl_series", "pd_series", "np_array", "str", "scalar", "omitted", "unsupported"]
Mode = Literal["expr", "polars", "pandas", "numpy"]

_COLUMN_KIND_NAMES: dict[Kind, str] = {
    "expr": "pl.Expr",
    "str": "column name",
    "pl_series": "pl.Series",
    "pd_series": "pd.Series",
    "np_array": "np.ndarray",
}

_MODE_FOR_KIND: dict[Kind, Mode] = {
    "expr": "expr",
    "str": "expr",
    "pl_series": "polars",
    "pd_series": "pandas",
    "np_array": "numpy",
}


def _column_annotation(annotation: object) -> tuple[bool, bool]:
    """Classify a parameter annotation as a column parameter and whether it is optional.

    A column parameter is annotated ``pl.Expr``. An *optional* column parameter is annotated
    ``pl.Expr | None``; it may be omitted, in which case the calculation receives ``None`` and decides what to do
    with it.

    Args:
        annotation: The parameter's annotation, as resolved by :func:`inspect.signature`.

    Returns:
        A ``(is_column, is_optional)`` pair.
    """
    if annotation is pl.Expr:
        return True, False
    if get_origin(annotation) in (Union, types.UnionType) and set(get_args(annotation)) == {pl.Expr, type(None)}:
        return True, True
    return False, False


def _classify(value: object, expects_column: bool) -> Kind:
    """Classify a single argument value into a dispatch kind.

    Args:
        value: The argument value to classify.
        expects_column: Whether the parameter it was passed for is annotated ``pl.Expr``.

    Returns:
        The kind of column type
    """
    if not expects_column:
        if isinstance(value, bool) or not isinstance(value, numbers.Real):
            return "unsupported"
        return "scalar"

    if isinstance(value, pl.Expr):
        return "expr"
    if isinstance(value, pl.Series):
        return "pl_series"
    if isinstance(value, str):
        return "str"
    np = sys.modules.get("numpy")
    if np is not None and isinstance(value, np.ndarray):
        return "np_array"
    pd = sys.modules.get("pandas")
    if pd is not None and isinstance(value, pd.Series):
        return "pd_series"
    return "unsupported"


def _check_supported(func_name: str, values: dict[str, Any], kinds: dict[str, Kind], columns: dict[str, bool]) -> None:
    """Check that every argument is a valid value for the parameter it was passed for.

    Args:
        func_name: Name of the wrapped calculation, used only in error messages.
        values: Mapping of argument name to the value passed for it.
        kinds: Mapping of argument name to the dispatch kind returned by :func:`_classify`.
        columns: Mapping of argument name to whether its parameter is annotated ``pl.Expr``.

    Raises:
        TypeError: If any argument is not a valid value for its parameter.
    """
    for name, kind in kinds.items():
        if kind == "unsupported":
            wanted = (
                "a pl.Expr, a column-name str, a pl.Series, a pd.Series or a np.ndarray"
                if columns[name]
                else "a number"
            )
            raise TypeError(f"{func_name}(): {name} expects {wanted}, got {type(values[name]).__name__}.")


def _decide_mode(func_name: str, kinds: dict[str, Kind]) -> Mode:
    """Decide which evaluation mode to use, or raise ``TypeError`` if the column kinds are mixed.

    Args:
        func_name: Name of the wrapped calculation, used only in error messages.
        kinds: Mapping of argument name to the dispatch kind returned by :func:`_classify`.

    Returns:
        The mode that :func:`flexible` should evaluate in.

    Raises:
        TypeError: If the column arguments are not all the same kind.
    """
    present: set[Kind] = {kind for kind in kinds.values() if kind in _COLUMN_KIND_NAMES}

    if len(present) > 1:
        got = "; ".join(
            f"{name} ({', '.join(n for n, k in kinds.items() if k == kind)})"
            for kind, name in _COLUMN_KIND_NAMES.items()
            if kind in present
        )
        raise TypeError(f"{func_name}(): all column arguments must be the same type - got {got}.")

    return _MODE_FOR_KIND[present.pop()] if present else "expr"


def _check_equal_length(series: dict[str, pl.Series]) -> None:
    """Check that every column argument has the same length.

    Args:
        series: Mapping of argument name to the Polars Series passed for it.

    Raises:
        ValueError: If the Series are not all the same length.
    """
    lengths = {name: len(s) for name, s in series.items()}
    if len(set[int](lengths.values())) > 1:
        raise ValueError(f"Series arguments must all be the same length, got {lengths}.")


def _to_polars_series(values: dict[str, Any], kinds: dict[str, Kind], mode: Mode) -> dict[str, pl.Series]:
    """Collect the column arguments of an eager call, as Polars Series.

    Args:
        values: Mapping of argument name to the value passed for it.
        kinds: Mapping of argument name to the dispatch kind returned by :func:`_classify`.
        mode: The mode returned by :func:`_decide_mode`.

    Returns:
        Mapping of argument name to Polars Series, empty in ``"expr"`` mode.

    Raises:
        ModuleNotFoundError: If pandas Series are passed without the ``pandas`` extra installed
            (which also provides ``pyarrow``).
    """
    if mode == "polars":
        return {name: values[name] for name, kind in kinds.items() if kind == "pl_series"}
    if mode == "numpy":
        return {name: pl.Series(name, values[name]) for name, kind in kinds.items() if kind == "np_array"}
    if mode == "pandas":
        try:
            import pyarrow  # noqa: F401
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "pandas Series input requires the 'pandas' extra: pip install hydrometlib[pandas]"
            ) from exc
        return {name: pl.Series(pl.from_pandas(values[name])) for name, kind in kinds.items() if kind == "pd_series"}
    return {}


def _evaluate(func: Callable[..., pl.Expr], call: dict[str, Any]) -> pl.Expr:
    """Call a calculation with the arguments dispatch has prepared for it.

    Args:
        func: The undecorated calculation.
        call: Mapping of argument name to the value to pass for it.

    Returns:
        The Polars expression the calculation builds.
    """
    return func(**call)


def flexible[**P](func: Callable[P, pl.Expr]) -> Callable[P, pl.Expr]:
    """Let a Polars-expression calculation also accept Series, arrays or column names.

    Parameters annotated ``pl.Expr`` in the parent function are considered to be "column-like", and accept a
    ``pl.Expr``, a column-name ``str``, a ``pl.Series``, a ``pd.Series`` or a ``np.ndarray``. Every column-like
    argument in one call must be the same kind. A parameter annotated ``pl.Expr | None`` is an *optional*
    column: it may be omitted (``None``), in which case the calculation receives ``None`` and it takes no part
    in the same-kind or equal-length checks. Every other parameter is a constant and accepts only a number.
    The wrapped function returns the same type as the input column-like parameters.

    Args:
        func: The calculation to wrap. It must be written as a pure Polars expression, with every
            column-like parameter annotated ``pl.Expr`` (or ``pl.Expr | None``) and returning a ``pl.Expr``.

    Returns:
        The wrapped calculation.
    """
    sig = inspect.signature(func, eval_str=True)
    _annotations = {name: _column_annotation(p.annotation) for name, p in sig.parameters.items()}
    columns = {name: is_column for name, (is_column, _) in _annotations.items()}
    optional_columns = {name: is_optional for name, (_, is_optional) in _annotations.items()}

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        """Dispatch one call to ``func`` based on the kinds of its column arguments.

        Args:
            *args: Positional arguments for ``func``.
            **kwargs: Keyword arguments for ``func``.

        Returns:
            A ``pl.Expr`` when the column arguments are expressions or column names, otherwise a
            ``pl.Series``, ``pd.Series`` or ``np.ndarray`` to match what was passed in.

        Raises:
            TypeError: If an argument is not valid for the parameter it was passed for, or column
                arguments from different libraries are mixed.
        """
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        values = bound.arguments
        kinds: dict[str, Kind] = {
            name: "omitted" if (optional_columns[name] and value is None) else _classify(value, columns[name])
            for name, value in values.items()
        }

        _check_supported(func.__name__, values, kinds, columns)
        mode = _decide_mode(func.__name__, kinds)
        series = _to_polars_series(values, kinds, mode)

        call = {
            name: (
                None
                if kinds[name] == "omitted"
                else pl.col(name)
                if name in series
                else pl.col(value)
                if kinds[name] == "str"
                else value
            )
            for name, value in values.items()
        }
        expr = _evaluate(func, call)

        if not series:
            return expr

        _check_equal_length(series)
        frame = pl.DataFrame(series)
        result = frame.select(expr.alias(func.__name__)).to_series()
        if mode == "pandas":
            return result.to_pandas()
        if mode == "numpy":
            return result.to_numpy()
        return result

    return wrapper
