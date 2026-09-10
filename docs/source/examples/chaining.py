"""Examples for the "Chaining calculations" user guide page."""

import pandas as pd
import polars as pl

from hydrometlib import flux

# The energy-balance frame the two chaining examples start from. Building it is not the point of
# those examples, so it lives here rather than in the region the page shows.
_ENERGY_BALANCE = {
    "rn": [80.0, 120.0],
    "shf": [5.0, 8.0],
    "h": [30.0, 40.0],
    "ta": [15.0, 18.0],
}


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
    # fmt: off
    # [start:chaining_pandas]
    df["le"] = flux.latent_heat_flux(
        df["rn"], df["shf"], df["h"]
    )

    df["et"] = flux.evapotranspiration_from_latent_heat_flux(
        df["le"], df["ta"]
    )
    # [end:chaining_pandas]
    # fmt: on
    print(df)
