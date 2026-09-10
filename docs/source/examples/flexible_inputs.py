"""Examples for the "Flexible inputs" user guide page."""

# Several examples here deliberately make a call the library rejects, so that the page can show the
# real error message. Those calls are type errors by construction; suppress them at file level so the
# directive stays out of the regions the docs render.
# pyright: reportArgumentType=false, reportCallIssue=false

import pandas as pd
import polars as pl

from hydrometlib import meteorology


def site_attributes() -> None:
    """Give the site attributes as single numbers, or as columns when a frame covers several sites."""
    # [start:site_attributes]
    from hydrometlib import cosmos

    # 1. Pass through a number for each attribute: the attributes
    #    are static values from a single site
    cosmos.volumetric_water_content(
        "cts_mod_corr",  # measured column
        ref_soc=0.01,  # site attributes from here on
        ref_bulkdensity=1.35,
        ref_latticewater=0.02,
        n0_mod=2000,
        n_min=400,
        n_max=4000,
    )

    # 2. Pass through columns for an attribute: for example, your data
    #    may have several sites in one frame so the attributes can vary across rows
    cosmos.volumetric_water_content(
        "cts_mod_corr",
        ref_soc="ref_soc",
        ref_bulkdensity="ref_bulkdensity",
        ref_latticewater="ref_latticewater",
        n0_mod="n0_mod",
        n_min=400,  # still a single number if it is the same everywhere
        n_max=4000,
    )
    # [end:site_attributes]


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


def all_constant_call() -> None:
    """Give every argument as a number to evaluate a calculation there and then."""
    # [start:all_constant_call]
    # a value comes straight back, rather than a column to add to a frame
    print(meteorology.net_radiation(100.0, 20.0, 300.0, 350.0))
    # [end:all_constant_call]
