import polars as pl

from hydrometlib._dispatch import flexible
from hydrometlib.evapotranspiration import latent_heat_of_vaporization


@flexible
def latent_heat_flux(rn: pl.Expr, shf: pl.Expr, h: pl.Expr) -> pl.Expr:
    r"""Calculate latent heat flux LE = Rn - SHF - H [W m-2].

    .. math::

        LE = R_n - G - H

    where :math:`G` is the soil heat flux and :math:`H` the sensible heat flux.

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
    r"""Evapotranspiration (ET) from latent heat flux [mm h-1]

    .. math::

        ET = \frac{3600 \, LE}{10^{6} \, \lambda} = 0.0036 \, \frac{LE}{\lambda}

    where :math:`LE` is the latent heat flux [W m-2] and :math:`\lambda` is the latent heat of vaporization
    [MJ kg-1] at air temperature :math:`T_a`, from :func:`~hydrometlib.evapotranspiration.latent_heat_of_vaporization`.

    Dividing the energy flux by the energy needed to evaporate a unit mass of water gives the mass flux of water
    evaporated, :math:`LE / (10^{6} \, \lambda)` [kg m-2 s-1], where :math:`10^{6}` converts :math:`\lambda` from
    MJ kg-1 to J kg-1. Taking the density of water as 1000 kg m-3, 1 kg m-2 of water is a depth of 1 mm, so this is
    also a depth rate [mm s-1], and the factor 3600 converts it to mm h-1.

    References:
        - FAO-56 Chapter 1, Units and Table 1 (1 mm of water is equivalent to 2.45 MJ m-2)
          https://www.fao.org/4/x0490e/x0490e04.htm
        - FAO-56 Chapter 3 (eq. 20), equivalent evaporation as radiation divided by :math:`\lambda`
          https://www.fao.org/4/x0490e/x0490e07.htm

    Args:
        le: Latent heat flux [W m-2]
        ta: Air temperature [degC]

    Returns:
        Expression or Series computing ET [mm h-1]
    """
    lv = latent_heat_of_vaporization(ta)
    return 3600 * le / (1e6 * lv)
