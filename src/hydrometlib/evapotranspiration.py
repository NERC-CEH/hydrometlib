import polars as pl

from hydrometlib._dispatch import flexible


@flexible
def saturation_vapour_pressure(ta: pl.Expr) -> pl.Expr:
    r"""Saturation vapour pressure (es) [kPa]

    .. math::

        e_s = 0.6108 \, \exp\!\left( \frac{17.27 \, T_a}{T_a + 237.3} \right)

    References:
        - FAO-56 Chapter 3 (eq. 11) https://www.fao.org/4/x0490e/x0490e07.htm#calculation%20procedures

    Args:
        ta: Air temperature [degC]

    Returns:
        Expression or Series to calculate es
    """
    return 0.6108 * ((17.27 * ta) / (ta + 237.3)).exp()


@flexible
def actual_vapour_pressure(es: pl.Expr, rh: pl.Expr) -> pl.Expr:
    r"""Actual vapour pressure (ea) [kPa]

    .. math::

        e_a = e_s \cdot \frac{RH}{100}

    References:
        - FAO-56 Chapter 4 (eq. 54) https://www.fao.org/4/x0490e/x0490e08.htm

    Args:
        es: Saturation vapour pressure [kPa]
        rh: Relative humidity [%]

    Returns:
        Expression or Series to calculate ea
    """
    return es * (rh / 100)


@flexible
def vapour_pressure_curve_slope(es: pl.Expr, ta: pl.Expr) -> pl.Expr:
    r"""Slope of vapour pressure curve (delta) [kPa degC-1]

    .. math::

        \Delta = \frac{4098 \, e_s}{(T_a + 237.3)^2}

    References:
        - FAO-56 Chapter 3 (eq. 13) https://www.fao.org/4/x0490e/x0490e07.htm#calculation%20procedures

    Args:
        es: Saturation vapour pressure [kPa]
        ta: Air temperature [degC]

    Returns:
        Expression or Series to calculate delta
    """
    return (4098 * es) / ((ta + 237.3) ** 2)


@flexible
def latent_heat_of_vaporization(ta: pl.Expr) -> pl.Expr:
    r"""Latent heat of vaporization (lambda) [MJ kg-1]

    .. math::

        \lambda = 2.501 - 2.361 \times 10^{-3} \, T_a

    References:
        - Harrison, L.P. 1963. "Fundamental concepts and definitions relating to humidity."
          In: Wexler, A. & Wildhack, W.A. (eds.) Humidity and Moisture. Vol. 3.
          Reinhold Publishing Company, New York
        - FAO-56 Annex 3 https://www.fao.org/4/x0490e/x0490e0k.htm

    Args:
        ta: Air temperature [degC]

    Returns:
        Expression or Series to calculate lambda
    """
    return 2.501 - (2.361e-3 * ta)


@flexible
def psychrometric_constant(pa: pl.Expr, lv: pl.Expr) -> pl.Expr:
    r"""Psychrometric constant (gamma) [kPa degC-1]

    .. math::

        \gamma = \frac{1.013 \times 10^{-3} \cdot (p_a / 10)}{0.622 \, \lambda}

    where :math:`p_a` is in hPa (divided by 10 to give kPa) and :math:`\lambda` is the latent heat
    of vaporization.

    References:
        - FAO-56 Chapter 3 (eq. 8) https://www.fao.org/4/x0490e/x0490e07.htm#psychrometric%20constant%20(g)

    Args:
        pa: Atmospheric pressure [hPa]
        lv: Latent heat of vaporization [MJ kg-1]

    Returns:
        Expression or Series to calculate gamma
    """
    cp = 1.013e-3  # Specific heat at constant pressure
    e_ratio = 0.622  # Ratio molecular weight of water vapour/dry air
    return (cp * (pa / 10)) / (e_ratio * lv)


@flexible
def wind_speed_height_correction(ws: pl.Expr, measured_height: pl.Expr) -> pl.Expr:
    r"""Convert wind speed to 2m height [m s-1]

    .. math::

        u_2 = u_z \cdot \frac{4.87}{\ln(67.8 \, z - 5.42)}

    where :math:`u_z` is the wind speed measured at height :math:`z` [m].

    References:
        - FAO-56 Chapter 3 (eq. 47) https://www.fao.org/4/x0490e/x0490e07.htm#wind%20profile%20relationship

    Args:
        ws: Wind speed measured at ``measured_height`` [m s-1]
        measured_height: The height above ground the wind was measured at [m]

    Returns:
        Expression or Series to calculate wind speed height correction
    """
    return ws * (4.87 / ((67.8 * measured_height) - 5.42).log())


@flexible
def potential_evapotranspiration_30min(
    rn: pl.Expr, g: pl.Expr, ta: pl.Expr, rh: pl.Expr, ws: pl.Expr, pa: pl.Expr, wind_height: pl.Expr
) -> pl.Expr:
    r"""Calculate potential evapotranspiration (pet) [mm 30min-1]

    PET is the maximum amount of water that could be evapotranspirated in a given climate, given a theoretical
    continuous expanse of vegetation covering the whole ground and a continuous supply of water.

    .. math::

        PET = \frac{0.408 \, \Delta \, (R_n - G)
                    + \gamma \, \dfrac{19}{T_a + 273} \, u_2 \, (e_s - e_a)}
                   {\Delta + \gamma \, (1 + 0.34 \, u_2)}

    where :math:`R_n` and :math:`G` are converted from W m-2 to MJ m-2 (30 min)-1 by multiplying by
    0.0018, :math:`u_2` is the wind speed corrected to 2 m, and :math:`e_s - e_a` is the vapour
    pressure deficit. The numerator constant 19 is the FAO-56 daily value (900) scaled to a 30-minute
    step (900 / 48).

    Applied here on a 30-minute step. FAO-56 on shorter timescales: "With the advent of electronic,
    automated weather stations, weather data are increasingly reported for hourly or shorter periods
    ... When applying the FAO Penman-Monteith equation on an hourly or shorter timescale, the equation
    and some of the procedures for calculating meteorological data should be adjusted for the smaller
    time step".

    References:
        - FAO-56 Chapter 2, FAO Penman-Monteith equation https://www.fao.org/4/x0490e/x0490e06.htm
        - FAO-56 Chapter 4 (eq. 53), hourly time step https://www.fao.org/4/x0490e/x0490e08.htm

    Args:
        rn: Net radiation [W m-2] (converted to MJ m-2 30min-1 internally)
        g: Soil heat flux density [W m-2] (converted to MJ m-2 30min-1 internally)
        ta: Air temperature [degC]
        rh: Relative humidity [%]
        ws: Wind speed measured at ``wind_height`` [m s-1] (corrected to 2 m internally)
        pa: Atmospheric pressure [hPa]
        wind_height: Height above ground of the wind sensor [m]

    Returns:
        Expression or Series computing PET [mm 30min-1]
    """
    es = saturation_vapour_pressure(ta)
    ea = actual_vapour_pressure(es, rh)
    vpd = es - ea  # Vapour pressure deficit
    delta = vapour_pressure_curve_slope(es, ta)
    lv = latent_heat_of_vaporization(ta)
    gamma = psychrometric_constant(pa, lv)
    ws_2m = wind_speed_height_correction(ws, wind_height)

    # Convert RN and G from W/m2 - MJ per 30 min (input provided as W/m2)
    rn_mj = rn * 0.0018
    g_mj = g * 0.0018

    # FAO constants
    # The Numerator and denominator constants for reference type and calculation time step are defined in the
    #   following references:
    #     Allen, R. G., Walter, I. A., Elliot, R. L., Howell, T.A., Itenfisu, D., Jensen, M. E.
    #         and Snyder, R. 2005. The ASCE standardized reference evapotranspiration equation. ASCE and American
    #         Society of Civil Engineers.
    #     FAO-56 Chapter 4 - Determination of ETo - "Hourly time step"
    #         https://www.fao.org/4/x0490e/x0490e08.htm

    # Numerator given as 900 for daily, and 37 for hourly. Here for 30 min data, adjusted to
    #   900 / 48 = 18.75 (rounded to 19)
    reference_crop_type_numerator = 19
    # Denominator is the same between daily and hourly in FAO-56 Chapter 4, eq. 53. Assume same is okay for 30min.
    reference_crop_type_denominator = 0.34

    # PET equation (FAO-56, adapted to 30-minute)
    radiation_term = 0.408 * delta * (rn_mj - g_mj)
    aerodynamic_term = gamma * (reference_crop_type_numerator / (ta + 273)) * ws_2m * vpd
    resistance_term = delta + gamma * (1 + (reference_crop_type_denominator * ws_2m))

    return (radiation_term + aerodynamic_term) / resistance_term
