"""Examples for the "Flexible inputs" user guide page."""

# Several examples here deliberately make a call the library rejects, so that the page can show the
# real error message. Those calls are type errors by construction; suppress them at file level so the
# directive stays out of the regions the docs render.
# pyright: reportArgumentType=false, reportCallIssue=false

import pandas as pd
import polars as pl

from hydrometlib import meteorology


def constant_arguments() -> None:
    """Mix column arguments with the single numbers that are the same for every row."""
    # [start:constant_arguments]
    from hydrometlib import cosmos

    cosmos.volumetric_water_content(
        "cts_mod_corr",  # column argument
        ref_soc=0.01,  # constant arguments from here on
        ref_bulkdensity=1.35,
        ref_latticewater=0.02,
        n0_mod=2000,
        n_min=400,
        n_max=4000,
    )
    # [end:constant_arguments]


def optional_column_argument() -> None:
    """Show a column argument that can be left out entirely."""
    # fmt: off
    # [start:optional_column_argument]
    from hydrometlib import evapotranspiration as et

    # wind sensor at 2 m - no height correction
    et.potential_evapotranspiration_30min(
        "rn", "g", "ta", "rh", "ws", "pa"
    )

    # wind sensor height varies row by row
    et.potential_evapotranspiration_30min(
        "rn", "g", "ta", "rh", "ws", "pa", "wind_height"
    )
    # [end:optional_column_argument]
    # fmt: on


def one_kind_per_call() -> None:
    """Show that every column argument in a call must be the same kind."""
    # [start:one_kind_per_call]
    # This works fine - every column argument is a column name
    meteorology.net_radiation("swin", "swout", "lwin", "lwout")

    # a column name mixed with an expression
    try:
        meteorology.net_radiation("swin", pl.col("swout") * 1.0, "lwin", "lwout")
    except TypeError as err:
        print(err)

    # a pl.Series mixed with a pd.Series
    try:
        meteorology.net_radiation(
            pl.Series([22.9]),
            pd.Series([4.9]),
            pl.Series([24.1]),
            pl.Series([31.2]),
        )
    except TypeError as err:
        print(err)
    # [end:one_kind_per_call]


def same_length() -> None:
    """Show that Series and array inputs must all be the same length."""
    # [start:same_length]
    try:
        meteorology.net_radiation(
            pl.Series([22.9, 19.3]),
            pl.Series([4.9]),
            pl.Series([24.1, 26.0]),
            pl.Series([31.2, 31.9]),
        )
    except ValueError as err:
        print(err)
    # [end:same_length]


def unsupported_types() -> None:
    """Show the error when an argument is not a valid value for its parameter."""
    # [start:unsupported_types]
    # a column argument given something that is not one of the accepted containers
    try:
        meteorology.net_radiation([22.9, 19.3], "swout", "lwin", "lwout")
    except TypeError as err:
        print(err)

    # a constant argument given something that is not a number
    try:
        meteorology.mean_sea_level_pressure("pa", "ta", altitude="high")
    except TypeError as err:
        print(err)
    # [end:unsupported_types]
