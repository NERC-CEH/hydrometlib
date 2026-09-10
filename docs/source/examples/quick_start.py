"""Examples for the "Quick start" page."""

import pandas as pd
import polars as pl

from hydrometlib import flux, meteorology

# The energy-balance frame the two chaining examples start from. Building it is not the point of
# those examples, so it lives here rather than in the region the page shows.
_ENERGY_BALANCE = {
    "rn": [80.0, 120.0],
    "shf": [5.0, 8.0],
    "h": [30.0, 40.0],
    "ta": [15.0, 18.0],
}


def polars_expressions() -> None:
    """Derive a column inside with_columns, naming the input columns as plain strings."""
    # fmt: off
    # [start:polars_expressions]
    import polars as pl

    from hydrometlib import meteorology

    df = pl.DataFrame(
        {
            "swin": [22.9, 19.3, 14.0, 25.1],
            "swout": [4.9, 4.2, 3.0, 5.5],
            "lwin": [24.1, 26.0, 26.2, 23.1],
            "lwout": [31.2, 31.9, 30.9, 30.8],
        }
    )

    # string inputs should match your dataframe column names:
    df = df.with_columns(
        rn=meteorology.net_radiation(
            "swin", "swout", "lwin", "lwout"
        )
    )

    # equivalent with pl.col():
    df = df.with_columns(
        rn=meteorology.net_radiation(
            pl.col("swin"), pl.col("swout"), pl.col("lwin"), pl.col("lwout")
        )
    )
    # [end:polars_expressions]
    # fmt: on
    print(df)


def polars_series() -> None:
    """Call a function with Polars Series and get a Series straight back."""
    # [start:polars_series]
    swin = pl.Series("swin", [22.9, 19.3])
    swout = pl.Series("swout", [4.9, 4.2])
    lwin = pl.Series("lwin", [24.1, 26.0])
    lwout = pl.Series("lwout", [31.2, 31.9])

    pl_series = meteorology.net_radiation(swin, swout, lwin, lwout)
    # [end:polars_series]
    print(type(pl_series))
    print(pl_series)


def pandas_series() -> None:
    """Pass Pandas columns and get a Series back, ready to assign."""
    # [start:pandas_series]
    import pandas as pd

    from hydrometlib import meteorology

    df = pd.DataFrame(
        {
            "swin": [22.9, 19.3, 14.0, 25.1],
            "swout": [4.9, 4.2, 3.0, 5.5],
            "lwin": [24.1, 26.0, 26.2, 23.1],
            "lwout": [31.2, 31.9, 30.9, 30.8],
        }
    )

    pd_series = meteorology.net_radiation(df["swin"], df["swout"], df["lwin"], df["lwout"])
    # [end:pandas_series]
    print(type(pd_series))
    print(pd_series)


def numpy_arrays() -> None:
    """Pass NumPy arrays and get an array back."""
    # [start:numpy_arrays]
    import numpy as np

    from hydrometlib import meteorology

    swin = np.array([22.9, 19.3])
    swout = np.array([4.9, 4.2])
    lwin = np.array([24.1, 26.0])
    lwout = np.array([31.2, 31.9])

    np_array = meteorology.net_radiation(swin, swout, lwin, lwout)
    # [end:numpy_arrays]
    print(type(np_array))
    print(np_array)


def chaining_polars() -> None:
    """Feed one derived column into the next calculation, in Polars."""
    df = pl.DataFrame(_ENERGY_BALANCE)
    # [start:chaining_polars]
    df = df.with_columns(
        le=flux.latent_heat_flux("rn", "shf", "h"),
    ).with_columns(
        et=flux.evapotranspiration_from_latent_heat_flux("le", "ta"),
    )
    # [end:chaining_polars]
    print(df)


def chaining_pandas() -> None:
    """Feed one derived column into the next calculation, in Pandas."""
    df = pd.DataFrame(_ENERGY_BALANCE)
    # [start:chaining_pandas]
    df["le"] = flux.latent_heat_flux(df["rn"], df["shf"], df["h"])
    df["et"] = flux.evapotranspiration_from_latent_heat_flux(df["le"], df["ta"])
    # [end:chaining_pandas]
    print(df)
