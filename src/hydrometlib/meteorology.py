import polars as pl

from hydrometlib._dispatch import flexible


@flexible
def net_radiation(swin: pl.Expr, swout: pl.Expr, lwin: pl.Expr, lwout: pl.Expr) -> pl.Expr:
    """Calculate net radiation (rn) [W m-2]

    The difference between the downward and upward total radiation.

    Reference:
        FAO-56 method (eq40) https://www.fao.org/4/x0490e/x0490e07.htm#net%20radiation%20(rn)

    Args:
        swin: Incoming shortwave radiation [W m-2]
        swout: Outgoing shortwave radiation [W m-2]
        lwin: Incoming longwave radiation [W m-2]
        lwout: Outgoing longwave radiation [W m-2]

    Returns:
        Expression or Series computing rn [W m-2]
    """
    return swin - swout + lwin - lwout


@flexible
def mean_soil_heat_flux(g1: pl.Expr, g2: pl.Expr) -> pl.Expr:
    """Calculate the mean soil heat flux (g) [W m-2] from two soil heat flux measurements.

    Soil heat flux defines the amount of thermal energy transferred through the soil, in a vertical
    direction, per unit of time.

    Args:
        g1: Soil heat flux measurement 1 [W m-2]
        g2: Soil heat flux measurement 2 [W m-2]

    Returns:
        Expression or Series computing g [W m-2]
    """
    return pl.mean_horizontal(g1, g2)


@flexible
def mean_sea_level_pressure(pa: pl.Expr, ta: pl.Expr, altitude: float) -> pl.Expr:
    """Calculate mean sea level pressure (mslp) [hPa]

    Adjusts measured atmospheric pressure to its sea-level equivalent. Measured pressure depends on the
    altitude of the sensor. This converts it to the pressure that would be observed at sea level, using
    the site altitude and air temperature to account for the decrease in pressure with height according
    to the standard atmosphere model.

    See US Standard Atmosphere, eq. 33a: https://ntrs.nasa.gov/api/citations/19770009539/downloads/19770009539.pdf
    See also: https://www.fao.org/4/x0490e/x0490e07.htm

    Args:
        pa: Atmospheric pressure [hPa]
        ta: Air temperature [Celsius]
        altitude: Site altitude [m]

    Returns:
        Expression or Series computing mslp [hPa]
    """
    return pa * (1 - ((0.0065 * altitude) / (ta + (0.0065 * altitude) + 273.15))).pow(-5.257)


@flexible
def absolute_humidity(ta: pl.Expr, rh: pl.Expr) -> pl.Expr:
    """Calculate absolute humidity Q [g m-3] (grams per cubic meter)

    A measure of the actual amount of water vapor in the air.

    References:
        - Saturation vapour pressure (step 1): Bolton, D. (1980). The computation of equivalent potential
            temperature. Monthly Weather Review, 108(7), 1046-1053, eq. 10
            https://doi.org/10.1175/1520-0493(1980)108%3C1046:TCOEPT%3E2.0.CO;2
        - Absolute humidity from vapour pressure (steps 3-4): WMO Guide to Instruments and Methods of
            Observation (WMO-No. 8), Volume I, Chapter 4 "Measurement of humidity" - Annex 4.A

    Steps to derive Q:

    (1) Saturation vapour pressure [Bolton 1980, eq. 10], in hPa
        (The vapour pressure when air is fully saturated (RH = 100%))
        Psat = 6.112 exp((17.67 Tc) / (Tc + 243.5))

    (2) Actual vapour pressure at any relative humidity (RH):
        P = 6.112 exp((17.67 Tc) / (Tc + 243.5)) * RH/100

    (3) Apply the ideal gas law:
        PV = nRT, => n = PV/RT
        [where P = Pressure of the gas, V = Volume occupied by the gas, R = universal gas constant, T = Temperature]

        Set V=1 to get density per cubic metre
        n = P / RT

        Multiply by molecular weight of water = 18.02 grams/mol
        Q = 18.02 * P / RT

        Substitute P from step 2, scaling it from hPa to Pa (x100) so it matches the units of R:

        Q = (18.02 * 100 * 6.112 * exp((17.67 Tc) / (Tc + 243.5)) * RH/100) / (R Tk)

    (4) Plug in the constants
        R = 8.314 J mol-1 K-1
        18.02 / 8.314 = 2.1674

        The hPa -> Pa scaling (x100) cancels the RH percentage (/100), so RH enters as a percentage
        and no factor of 100 survives:

        Q = 6.112 * exp((17.67 Tc) / (Tc + 243.5)) * RH * 2.1674 / Tk

        where Tc is air temperature in Celsius and Tk = Tc + 273.15 is the same temperature in Kelvin.

    Args:
        ta: Air temperature [Celsius]
        rh: Relative humidity [%]

    Returns:
        Expression or Series computing absolute humidity, Q [g m-3]
    """
    q1 = ((17.67 * ta) / (ta + 243.5)).exp()
    q2 = 273.15 + ta

    return (6.112 * q1 * rh * 2.1674) / q2


@flexible
def solar_zenith(time: pl.Expr, latitude: float) -> pl.Expr:
    """Calculate angle of the sun from the vertical [radians]

    Taken from https://en.wikipedia.org/wiki/Solar_zenith_angle, with some approximations.

    theta_s is solar zenith in radians:
        0 = overhead
        pi/2 = horizon
        pi = nadir

    cos(theta_s) > 0 means sun above horizon, proxy for daylight hours.

    Args:
        time: Datetime column of the observations [local clock time]. The hour angle is taken
            straight from the clock time, so this must be a local time in which solar noon is
            approximately 12:00 - longitude and the equation of time are not accounted for.
            For UK sites, UTC is close enough; do not pass a summer-time (BST) clock.
        latitude: Site latitude [degrees, positive north]

    Returns:
        Expression or Series for solar zenith angle, theta_s [radians]
    """
    # hour angle [radians]: used solar noon ~ 12:00
    h = (time.dt.hour() + time.dt.minute() / 60.0 - 12.0) * (pl.lit(15).radians())

    # number of days after beginning of year
    ordinal_days = time.dt.ordinal_day()

    # Declination delta (radians)
    axis_tilt = 23.44  # tilt of the Earth, degrees
    delta = -pl.lit(axis_tilt).radians() * (((360 / 365) * (ordinal_days + 10.0)).radians()).cos()

    # Convert latitude to radians
    phi = pl.lit(latitude).radians()

    # cos(theta_s)
    cos_theta_s = phi.sin() * delta.sin() + phi.cos() * delta.cos() * h.cos()

    # Return solar zenith angle in radians
    return cos_theta_s.arccos()


@flexible
def albedo(swin: pl.Expr, swout: pl.Expr, solar_zenith_angle: pl.Expr) -> pl.Expr:
    """Calculate albedo [unitless fraction]

    The ratio of reflected solar radiation to the total incoming solar radiation.

    References:
        - https://www.fao.org/4/x0490e/x0490e07.htm
        - https://onlinelibrary.wiley.com/doi/epdf/10.1002/hyp.14048

    This calculation does not account for correction due to site being on a slope. That is handled
    separately by a correction method.

    Args:
        swin: Shortwave incoming radiation [W m-2]
        swout: Shortwave outgoing radiation [W m-2]
        solar_zenith_angle: Solar zenith angle [radians]

    Returns:
        Expression or Series for albedo. Value is null at night or where invalid, otherwise between 0 and 1.
    """
    albedo_expr = pl.when((swin.is_not_null()) & (swin > 0)).then(swout / swin).otherwise(None)

    # Remove nighttime values
    swin_clear = solar_zenith_angle.cos()
    albedo_day = pl.when(swin_clear > 0).then(albedo_expr).otherwise(None)

    return albedo_day.clip(0.0, 1.0)


@flexible
def is_snow_day(albedo_expr: pl.Expr, albedo_min_threshold: float, albedo_max_threshold: float) -> pl.Expr:
    """Calculate if a given day is a snow day. True is snow, False if not.

    Simple rules:
        - If today's albedo is None, then is_snow_day is None
        - albedo >= albedo_max_threshold is a proxy for is_snow_day = True
        - albedo < albedo_min_threshold is a proxy for is_snow_day = False

    Normally: albedo_min_threshold = 0.5, albedo_max_threshold = 0.35, see: https://doi.org/10.1002/hyp.14048

    Complex rules:
        - It is more likely that today is (not) a snow day if yesterday was (not).
        - If there was snow the previous day, i.e. the previous day's albedo >= 0.5, then
            the current day is a snow day if the albedo > 0.35.
        - If there was no snow the previous day, i.e. the previous day's albedo < 0.5, then
            the current day is a snow day if the albedo >= 0.5.

    Args:
        albedo_expr: Albedo - measure of reflection with values between 0 and 1 [unitless fraction]
        albedo_min_threshold: Albedo threshold below which there is no snow [unitless fraction, 0-1]
        albedo_max_threshold: Albedo threshold above which there is snow [unitless fraction, 0-1]

    Returns:
        Expression or Series with boolean values.

    Note:
        Order-dependent: rows must be sorted by time (one row per day), as the calculation
        compares each day with the previous one.
    """
    albedo_prev = albedo_expr.shift()
    return (
        pl.when(albedo_prev.is_null())
        .then(
            pl.when(albedo_expr >= albedo_max_threshold)
            .then(True)
            .when(albedo_expr < albedo_min_threshold)
            .then(False)
            .otherwise(None)
        )
        .when(albedo_prev >= albedo_max_threshold)
        .then(
            pl.when(albedo_expr >= albedo_min_threshold)
            .then(True)
            .when(albedo_expr < albedo_min_threshold)
            .then(False)
            .otherwise(None)
        )
        .otherwise(
            pl.when(albedo_expr >= albedo_max_threshold)
            .then(True)
            .when(albedo_expr < albedo_max_threshold)
            .then(False)
            .otherwise(None)
        )
    )
