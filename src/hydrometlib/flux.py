import polars as pl

from hydrometlib._dispatch import flexible
from hydrometlib.evapotranspiration import latent_heat_of_vaporization


@flexible
def latent_heat_flux(rn: pl.Expr, shf: pl.Expr, h: pl.Expr) -> pl.Expr:
    """Calculate latent heat flux LE = Rn - SHF - H [W m-2].

    Args:
        rn: Net radiation [W m-2]
        shf: Soil heat flux [W m-2]
        h: Sensible heat flux [W m-2]

    Returns:
        Expression or Series computing LE [W m-2]
    """
    return rn - shf - h


@flexible
def evapotranspiration_from_latent_heat_flux(le: pl.Expr, ta: pl.Expr) -> pl.Expr:
    """Calculate evapotranspiration ET = LE / lambda / 1000.

    Args:
        le: Latent heat flux [W m-2]
        ta: Air temperature [degC]

    Returns:
        Expression or Series computing ET
    """
    lv = latent_heat_of_vaporization(ta)
    return le / lv / 1000.0
