import polars as pl

from hydrometlib._dispatch import flexible


@flexible
def neutron_intensity_factor(crns_count: pl.Expr, ref_c0: float, gamma: float) -> pl.Expr:
    r"""Calculate incoming neutron count intensity correction factor using a background reference station [unitless]

    .. math::

        f_{inten} = \frac{1}{\gamma \left( \dfrac{C}{C_0} - 1 \right) + 1}

    where :math:`C` is ``crns_count`` and :math:`C_0` is ``ref_c0``.

    References:
        - "COSMOS: the Cosmic-ray Soil Moisture Observing System" https://hess.copernicus.org/articles/16/4079/2012/
        - "Intensity correction factors for a cosmic ray neutron sensor": https://zenodo.org/records/4569062
        - COSMOS-UK supporting information: https://doi.org/10.5285/2dce161d-2fab-47bb-9fe6-38e7ed1ae18a

    Args:
        crns_count: Neutron counts from the reference neutron monitor, as a count rate over the same interval as
            ``ref_c0`` [e.g. counts h-1]. Only the ratio ``crns_count / ref_c0`` is used, so any count rate works
            provided ``ref_c0`` shares it.
        ref_c0: Site attribute - scaling reference for the neutron counts, on the same basis as
            ``crns_count`` [e.g. counts h-1]
        gamma: Site attribute - scaling factor to adjust for geomagnetic effects [unitless]

    Returns:
        Expression or Series for incoming neutron count intensity factor [unitless]
    """
    return 1 / (((crns_count / ref_c0) - 1) * gamma + 1)


@flexible
def absolute_humidity_factor(q: pl.Expr, ref_q0: float) -> pl.Expr:
    r"""Calculate absolute humidity correction factor to neutron counts [unitless]

    .. math::

        f_Q = 1 + 0.0054 \, (Q - Q_0)

    where :math:`Q` is the absolute humidity and :math:`Q_0` (``ref_q0``) the reference condition;
    0.0054 is the empirical structure constant.

    References:
        - Rosolem, R., W. J. Shuttleworth, M. Zreda, T. E. Franz, X. Zeng, and S. A. Kurc, 2013:
          The Effect of Atmospheric Water Vapor on Neutron Count in the Cosmic-Ray Soil Moisture Observing System.
          J. Hydrometeor., 14, 1659-1671, https://doi.org/10.1175/JHM-D-12-0120.1
        - M. Andreasen, K.H. Jensen, D. Desilets, T.E. Franz, M. Zreda, H.R. Bogena, and M.C. Looms. 2017:
          Status and perspectives on the cosmic-ray neutron method for soil moisture estimation
          and other environmental science applications.
          Vadose Zone J. 16(8). https://doi.org/10.2136/vzj2017.04.0086
        - Bogena et al. (2022): https://doi.org/10.5194/essd-14-1125-2022

    Empirical structure constant = 0.0054

    Args:
        q: Absolute humidity [g m-3] (grams per cubic meter)
        ref_q0: Site annotation for reference condition of absolute humidity [g m-3]

    Returns:
        Expression or Series for absolute humidity factor [unitless]
    """
    return 1 + 0.0054 * (q - ref_q0)


@flexible
def atmospheric_pressure_factor(pa: pl.Expr, barometric_attenuation_length: float) -> pl.Expr:
    r"""Calculate atmospheric pressure correction factor to neutron counts [unitless]

    .. math::

        f_p = \exp\!\left( \frac{p_a - 1000}{L} \right)

    where :math:`L` is the barometric attenuation length and 1000 hPa the reference pressure.

    References:
        - CRNPy correction factor, Desilets & Zreda, 2003: https://doi.org/10.1016/S0012-821X(02)01088-9
        - Zreda et al. (2012) HESS https://doi.org/10.5194/hess-16-4079-2012
        - Bogena et al. (2022): https://doi.org/10.5194/essd-14-1125-2022

    Args:
        pa: Atmospheric pressure [hPa]
        barometric_attenuation_length: Site attribute - barometric attenuation length, L [hPa].
            Must be in the same units as ``pa``, since the exponent is ``(pa - 1000) / L``.

    Returns:
        Expression or Series for atmospheric pressure factor [unitless]
    """
    p0 = 1000  # "Arbitrary reference pressure [hPa]: Zreda et al. (2012) HESS" - set to a constant of 1000.0
    return ((pa - p0) / barometric_attenuation_length).exp()


@flexible
def correct_counts(cts_mod: pl.Expr, factor_inten: pl.Expr, factor_pa: pl.Expr, factor_q: pl.Expr) -> pl.Expr:
    r"""Calculate corrected neutron counts using correction factors [counts h-1]

    .. math::

        C_{corr} = C \cdot f_{inten} \cdot f_p \cdot f_Q

    Bogena et al. (2022): https://doi.org/10.5194/essd-14-1125-2022:
    "Variations of the incoming cosmic-ray intensity can have many causes, from galactic and solar disturbances to
    atmospheric and meteorological influences. Most of these anomalies are expected to change proportionally in
    every domain of the neutron energy spectrum and thus can be addressed by applying a set of correction factors."

    Args:
        cts_mod: Neutron counts to be corrected [counts h-1]
        factor_inten: Correction factor to neutron intensity counts [unitless]
        factor_pa: Atmospheric pressure correction factor to neutron counts [unitless]
        factor_q: Absolute humidity correction factor to neutron counts [unitless]

    Returns:
        Expression or Series of corrected mod counts [counts h-1].
    """
    return cts_mod * factor_inten * factor_pa * factor_q


@flexible
def volumetric_water_content(
    cts_mod_corr: pl.Expr,
    ref_soc: float,
    ref_bulkdensity: float,
    ref_latticewater: float,
    n0_mod: float,
    n_min: float,
    n_max: float,
) -> pl.Expr:
    r"""Calculate volumetric water content (VWC) from corrected neutron counts and site annotations [%]

    VWC is the total volume of water present in a given volume of soil, represented as a fraction of the
    soil volume occupied by water (the remainder of the fraction being solid particles and air pockets).

    .. math::

        \theta_v = 100 \, \rho_b \left(
            \frac{0.0808}{\dfrac{C_{corr}}{N_0} - 0.372} - 0.115 - \theta_{lw} - \theta_{soc}
        \right)

    where :math:`\rho_b` is ``ref_bulkdensity``, :math:`\theta_{lw}` is ``ref_latticewater`` and
    :math:`\theta_{soc}` is ``ref_soc``. :math:`C_{corr}` is first clipped to
    ``[n_min, n_max]`` and the result is clipped to ``[0, 100]``.

    References:
        - "COSMOS: the COsmic-ray Soil Moisture Observing System", Zreda et al., 2012
            https://doi.org/10.5194/hess-16-4079-2012
        - Desilets et al., 2010 https://doi.org/10.1029/2009WR008726

    Args:
        cts_mod_corr: Neutron counts, corrected for influences on cosmic-ray intensity
            [counts h-1]. Must be on the same counting interval as ``n0_mod``, ``n_min`` and
            ``n_max``, since only the ratio ``cts_mod_corr / n0_mod`` is used.
        ref_soc: Site attribute of reference soil organic carbon [g g-1]
        ref_bulkdensity: Site attribute of reference soil bulk density [g cm-3]
        ref_latticewater: Site attribute of reference lattice water content [g g-1]
        n0_mod: Site attribute of a calibration coefficient obtained from field calibration [counts h-1]
        n_min: Site attribute of minimum range for neutron counts [counts h-1]
        n_max: Site attribute of maximum range for neutron counts [counts h-1]

    Returns:
        Expression or Series for VWC [%], clipped to 0-100.
    """
    # From Desilets et al., 2010 https://doi.org/10.1029/2009WR008726
    a0 = 0.0808
    a1 = 0.372
    a2 = 0.115

    cts_mod_corr = cts_mod_corr.clip(n_min, n_max)

    vwc = 100 * ref_bulkdensity * (a0 / ((cts_mod_corr / n0_mod) - a1) - a2 - ref_latticewater - ref_soc)
    return vwc.clip(0.0, 100.0)


@flexible
def snow_estimated_counts(cts_smo: pl.Expr, snow: pl.Expr, time: pl.Expr) -> pl.Expr:
    r"""Calculate CRNS count estimates when there is snow [counts h-1]

    This derivation reconstructs CRNS counts as if there had been no snow, because snow suppresses the counts.
    During a snow event, the estimated count is set to the value of the counts just before the snow started.
    If the counts increase, so should the estimate.

    .. math::

        \hat{C}_t =
        \begin{cases}
        C_t & \text{if } C_t > \hat{C}^{\,init} \\
        \hat{C}^{\,init} & \text{otherwise}
        \end{cases}

    where :math:`\hat{C}^{\,init}` is the smoothed count at the start of the current snow period,
    carried forward. :math:`\hat{C}_t` is null outside snow periods. Snow periods are identified from
    ``snow`` using 24- and 48-hour offsets (see the source for the event-detection logic).

    Reference: Wallbank JR, Cole SJ, Moore RJ, Anderson SR, Mellor EJ.
            Estimating snow water equivalent using cosmic-ray neutron sensors from the COSMOS-UK network.
            Hydrological Processes. 2021;35:e14048. https://doi.org/10.1002/hyp.14048

    Args:
        cts_smo: Smoothed neutron counts, already corrected for influences on cosmic-ray intensity [counts h-1]
        snow: Boolean values indicating if snow is present on that day [unitless]
        time: Hourly timestamps corresponding to cts_smo values [datetime]

    Returns:
        Expression or Series for estimated counts during snow periods [counts h-1]. Null when not in a snow period.

    Note:
        Order-dependent: rows must be sorted by time on a regular hourly grid, as the calculation
        shifts by 24- and 48-hour offsets.
    """
    hours_in_a_day = 24

    snow_prev1 = snow.shift(hours_in_a_day)
    snow_prev2 = snow.shift(2 * hours_in_a_day)

    event_start = snow & (~snow_prev1) & (~snow_prev2) & (time.dt.hour() == 0)
    event_end = (~snow) & (~snow_prev1) & snow_prev2 & (time.dt.hour() == 0)
    period_boundary = pl.when(event_start).then(True).when(event_end.shift(-hours_in_a_day)).then(False).otherwise(None)

    # The event_end is identified when there has been two consecutive days of no snow,
    # but the actual end of the snow period is when the snow stops, i.e. the first day of no snow,
    # so the event_end is shifted back by 24 hours to denote the true end of the snow period.
    # This shift means the last 24 hours in period_boundary are not defined, and become null.
    # If there is snow in the last 24 hours, we know this is in a snow period,
    # so we fill the nulls as True in this case.
    in_snow_period = period_boundary.forward_fill().fill_null(snow)

    # Counts during snow period are initialised by the counts from the end of previous day.
    init_cts_est = pl.when(in_snow_period).then(pl.when(event_start).then(cts_smo.shift(1)).forward_fill())
    return pl.when(cts_smo > init_cts_est).then(cts_smo).otherwise(init_cts_est)


@flexible
def snow_water_equivalence(cts_smo: pl.Expr, cts_est: pl.Expr, n0_mod: float) -> pl.Expr:
    r"""Calculate snow water equivalence (SWE) for an above ground COSMOS sensor [mm water equivalent]

    .. math::

        SWE = -\Lambda \, \ln\!\left( \frac{C_{smo} - N_{wat}}{C_{est} - N_{wat}} \right),
        \qquad \Lambda = 48, \quad N_{wat} = 0.38 \, N_0

    where :math:`N_0` is ``n0_mod``.

    References:
        - Wallbank J. R., Cole S. J., Moore R. J., Anderson S. R., Mellor E. J. (2020),
            Estimating snow water equivalent using cosmic-ray neutron sensors from the COSMOS-UK network,
            Hydrological Processes, 35(5), e14048. https://doi.org/10.1002/hyp.14048
        - Desilets, D. (2017). Calibrating a non-invasive cosmic ray soil moisture probe for snow water equivalent.
            Hydroinnova Technical Document 17-01.

    Args:
        cts_smo: Smoothed neutron counts, corrected for influences on cosmic-ray intensity [counts h-1]
        cts_est: Estimated counts during snow periods [counts h-1]
        n0_mod: Site attribute of a calibration coefficient obtained from field calibration [counts h-1]

    Returns:
        Expression or Series for SWE [mm water equivalent]
    """
    # Wallbank et al. 2020, eq. 8
    nwat_fac = 0.38
    n_wat = n0_mod * nwat_fac

    # Wallbank et al. 2020, eq. 1
    lambda_ = 48  # [mm water equivalent]; in Wallbank et al. 2020, cited as from Desilets, 2017
    return -lambda_ * ((cts_smo - n_wat) / (cts_est - n_wat)).log()


@flexible
def snow_water_equivalence_snowfox(cts_smo: pl.Expr, cts_est: pl.Expr) -> pl.Expr:
    r"""Calculate snow water equivalence (SWE) for a below ground (SnowFox) COSMOS sensor [mm water equivalent]

    .. math::

        \begin{aligned}
        N^{*} &= \frac{C_{smo}}{C_{est}} \\[4pt]
        \Lambda &= \frac{1}{\Lambda_{max}}
            - \left( \frac{1}{\Lambda_{max}} - \frac{1}{\Lambda_{min}} \right)
            \left( 1 + e^{(a_1 - N^{*}) / a_2} \right)^{-a_3} \\[4pt]
        SWE &= -\,\frac{10 \, \ln N^{*}}{\Lambda}
        \end{aligned}

    with :math:`a_1 = 0.3133`, :math:`a_2 = 0.08268`, :math:`a_3 = 1.117`,
    :math:`\Lambda_{max} = 114.4` and :math:`\Lambda_{min} = 14.11` (Howat et al. 2018). The factor
    of 10 converts cm to mm.

    References:
        - Wallbank J. R., Cole S. J., Moore R. J., Anderson S. R., Mellor E. J. (2020),
            Estimating snow water equivalent using cosmic-ray neutron sensors from the COSMOS-UK network,
            Hydrological Processes, 35(5), e14048. https://doi.org/10.1002/hyp.14048
        - Howat, I. M., de la Peña, S., Desilets, D., & Womack, G. (2018).
            Autonomous ice sheet surface mass balance measurements from cosmic rays.
            The Cryosphere, 12, 2099-2108. https://doi.org/10.5194/tc-12-2099-2018

    Args:
        cts_smo: Smoothed neutron counts from snowfox sensor, corrected for influences on
            cosmic-ray intensity [counts h-1]
        cts_est: Estimated counts during snow periods from snowfox sensor [counts h-1]

    Returns:
        Expression or Series for SWE [mm water equivalent]
    """
    # Wallbank et al. 2020, eq. 10
    n_star = cts_smo / cts_est

    # Howat et al. 2018, table 1
    a1 = 0.3133
    a2 = 0.08268
    a3 = 1.117
    amax = 114.4
    amin = 14.11

    # Howat et al. 2018, eq. 5
    lambda_ = (1 / amax) - ((1 / amax) - (1 / amin)) * (1 + ((a1 - n_star) / a2).exp()) ** (-a3)

    # Howat et al. 2018, eq. 4 - multiply by 10 to convert cm to mm
    return -lambda_.pow(-1) * n_star.log() * 10


@flexible
def sigma_snow_water_equivalence(cts_smo: pl.Expr, cts_est: pl.Expr, n0_mod: float) -> pl.Expr:
    r"""Calculate **uncertainty** in a snow water equivalence (SWE) calculation for the
    above ground COSMOS sensor [mm water equivalent]

    .. math::

        \sigma_{SWE} = \sqrt{
            \left( \frac{-\Lambda}{C_{smo} - N_{wat}} \right)^2 \frac{C_{smo}}{24}
            + \left( \frac{\Lambda}{C_{est} - N_{wat}} \right)^2 \sigma_{N_0}^2
        }

    with :math:`\Lambda = 48`, :math:`N_{wat} = 0.38 \, N_0` and :math:`\sigma_{N_0} = 12`. The two
    terms are the propagated Poisson counting error and the calibration error.

    References:
        - Wallbank J. R., Cole S. J., Moore R. J., Anderson S. R., Mellor E. J. (2020),
            Estimating snow water equivalent using cosmic-ray neutron sensors from the COSMOS-UK network,
            Hydrological Processes, 35(5), e14048. https://doi.org/10.1002/hyp.14048
        - Desilets, D. (2017). Calibrating a non-invasive cosmic ray soil moisture probe for snow water equivalent.
            Hydroinnova Technical Document 17-01.

    Args:
        cts_smo: Smoothed neutron counts, corrected for influences on cosmic-ray intensity [counts h-1]
        cts_est: Estimated counts during snow periods [counts h-1]
        n0_mod: Site attribute of a calibration coefficient obtained from field calibration [counts h-1]

    Returns:
        Expression or Series for SWE uncertainty [mm water equivalent]
    """
    # Wallbank et al. 2020, eq. 8
    nwat_fac = 0.38
    n_wat = n0_mod * nwat_fac
    lambda_ = 48  # In Wallbank et al. 2020, cited as from Desilets, 2017

    # Wallbank et al. 2020, section 5.4
    sigma_n = (cts_smo / 24).sqrt()
    sigma_n_theta = 12  # empirical uncertainty in N0(t), Wallbank et al. (2020) Section 6.1

    # Wallbank et al. 2020, eq. 15
    dswe_d_n = -lambda_ / (cts_smo - n_wat)
    dswe_d_n_theta = lambda_ / (cts_est - n_wat)

    # Wallbank et al. 2020, eq. 14
    sigma_swe_n = dswe_d_n * sigma_n
    sigma_swe_n_theta = dswe_d_n_theta * sigma_n_theta
    return (sigma_swe_n.pow(2) + sigma_swe_n_theta.pow(2)).sqrt()


@flexible
def sigma_snow_water_equivalence_snowfox(cts_smo: pl.Expr, cts_est: pl.Expr) -> pl.Expr:
    r"""Calculate **uncertainty** in a snow water equivalence (SWE) calculation for a below ground (SnowFox) COSMOS
    sensor [mm water equivalent]

    .. math::

        \sigma_{SWE} = \sqrt{
            \left( \frac{c}{C_{est}} \right)^2 \frac{C_{smo}}{24}
            + \left( \frac{-c \, C_{smo}}{C_{est}^2} \right)^2 \sigma_{N_0}^2
        }

    with :math:`c = -157` (estimated from the 0-30 mm portion of the Howat et al. 2018 attenuation
    curve) and :math:`\sigma_{N_0} = 16`.

    References:
        - Wallbank J. R., Cole S. J., Moore R. J., Anderson S. R., Mellor E. J. (2020),
            Estimating snow water equivalent using cosmic-ray neutron sensors from the COSMOS-UK network,
            Hydrological Processes, 35(5), e14048. https://doi.org/10.1002/hyp.14048
        - Howat, I. M., de la Peña, S., Desilets, D., & Womack, G. (2018).
            Autonomous ice sheet surface mass balance measurements from cosmic rays.
            The Cryosphere, 12, 2099-2108. https://doi.org/10.5194/tc-12-2099-2018

    Args:
        cts_smo: Smoothed neutron counts from snowfox sensor, corrected for influences on
            cosmic-ray intensity [counts h-1]
        cts_est: Estimated counts during snow periods from snowfox sensor [counts h-1]

    Returns:
        Expression or Series for SWE uncertainty [mm water equivalent]
    """
    # Wallbank et al. 2020, eq. 16
    # estimated from the 0-30 mm portion of the attenuation curve in Howat et al. 2018
    c_howat = -157

    # Wallbank et al. 2020, section 5.4
    sigma_n = (cts_smo / 24).sqrt()
    sigma_n_theta = 16  # empirical uncertainty in N0(t), Wallbank et al. (2020) Section 6.1

    # Wallbank et al. 2020, eq. 16
    dswe_d_n = c_howat / cts_est
    dswe_d_n_theta = (-c_howat * cts_smo) / cts_est.pow(2)

    # Wallbank et al. 2020, eq. 14
    sigma_swe_n = dswe_d_n * sigma_n
    sigma_swe_n_theta = dswe_d_n_theta * sigma_n_theta
    return (sigma_swe_n.pow(2) + sigma_swe_n_theta.pow(2)).sqrt()


@flexible
def soil_moisture_index(
    cosmos_vwc: pl.Expr, wilting_point: pl.Expr, field_capacity: pl.Expr, saturation: pl.Expr
) -> pl.Expr:
    r"""Calculate soil moisture index (SMI) [unitless, 0-2]

    SMI is a normalised measure of soil wetness relative to the wilting point, field capacity and
    saturation of the soil:

    - 0, when VWC is at or below the wilting point
    - between 0 and 1, when VWC is between the wilting point and field capacity
    - between 1 and 2, when VWC is between field capacity and saturation
    - 2, when VWC is at or above saturation

    .. math::

        SMI =
        \begin{cases}
        0 & \theta_v \le \theta_{wp} \\[2pt]
        \dfrac{\theta_v - \theta_{wp}}{\theta_{fc} - \theta_{wp}} & \theta_{wp} < \theta_v \le \theta_{fc} \\[6pt]
        1 + \dfrac{\theta_v - \theta_{fc}}{\theta_{sat} - \theta_{fc}} & \theta_{fc} < \theta_v \le \theta_{sat} \\[6pt]
        2 & \theta_v > \theta_{sat}
        \end{cases}

    where :math:`\theta_{wp}` is ``wilting_point``, :math:`\theta_{fc}` is ``field_capacity`` and
    :math:`\theta_{sat}` is ``saturation``. A null :math:`\theta_v` gives a null result.

    Reference:
        COSMOS-UK User Guide; Appendix H Soil Moisture Index
            https://cosmos.ceh.ac.uk/sites/default/files/2024-12/COSMOS-UK_User_guide_v3_08_0.pdf

    Args:
        cosmos_vwc: Volumetric Water Content (soil moisture) [%]
        wilting_point: The volumetric water content at the wilting point of the soil [%]
        field_capacity: The volumetric water content at field capacity [%]
        saturation: The volumetric water content when the soil is fully saturated [%]

    Returns:
        Expression or Series calculating soil moisture index [unitless, 0-2]
    """
    return (
        pl.when(cosmos_vwc.is_null())
        .then(None)
        .when(cosmos_vwc <= wilting_point)
        .then(0.0)
        .when(cosmos_vwc <= field_capacity)
        .then((cosmos_vwc - wilting_point) / (field_capacity - wilting_point))
        .when(cosmos_vwc <= saturation)
        .then((cosmos_vwc - field_capacity) / (saturation - field_capacity) + 1)
        .otherwise(2.0)
    )


@flexible
def effective_depth(cosmos_vwc: pl.Expr, ref_soc: float, ref_bulkdensity: float, ref_latticewater: float) -> pl.Expr:
    r"""Original effective depth calculation from SIMPLE VWC method [cm]

    .. math::

        d = \frac{5.8}{\rho_b \, (\theta_{lw} + \theta_{soc}) + \dfrac{\theta_v}{100} + 0.0829}

    where :math:`\rho_b` is ``ref_bulkdensity``, :math:`\theta_{lw}` is ``ref_latticewater``,
    :math:`\theta_{soc}` is ``ref_soc`` and :math:`\theta_v` is the VWC in percent.

    References:
        - Franz TE, Zreda M, Rosolem R, Ferre TPA. (2013) A universal calibration function for
          determination of soil moisture with cosmic-ray neutrons. Hydrology and Earth System
          Sciences 17: 453-460. DOI:10.5194/hess-17-453-2013
        - COSMOS-UK User Guide; Section 7.4 The CRNS footprint (compares this effective depth
          calculation against the D86 footprint depths now used operationally):
          https://cosmos.ceh.ac.uk/sites/default/files/2024-12/COSMOS-UK_User_guide_v3_08_0.pdf

    Args:
        cosmos_vwc: Volumetric Water Content (soil moisture) [%]
        ref_soc: Site attribute of reference soil organic carbon [g g-1]
        ref_bulkdensity: Site attribute of reference soil bulk density [g cm-3]
        ref_latticewater: Site attribute of reference lattice water content [g g-1]

    Returns:
        Expression or Series calculating effective depth [cm]
    """
    return 5.8 / (ref_bulkdensity * (ref_latticewater + ref_soc) + cosmos_vwc / 100.0 + 0.0829)


@flexible
def d86(
    cosmos_vwc: pl.Expr,
    pa: pl.Expr,
    ref_soc: float,
    ref_bulkdensity: float,
    ref_latticewater: float,
    distance: float,
) -> pl.Expr:
    r"""Calculate D86 value [cm]

    D86 is defined as the depth to which 86% of the detected cosmic ray neutrons had contact with constituents
    of the soil. It can be calculated at given distances from the Cosmic Ray Neutron Sensor (CRNS).

    .. math::

        \begin{aligned}
        \theta_{twe} &= \frac{\theta_v}{100} + \rho_b \, (\theta_{lw} + \theta_{soc}) \\[4pt]
        F_p &= \frac{0.4922}{0.86 - e^{-p_a / 1013}} \\[4pt]
        r^{*} &= \frac{r}{F_p} \\[4pt]
        D_{86} &= \frac{1}{\rho_b} \left[ 8.321 + 0.14249 \left( 0.96655 + e^{-0.01 \, r^{*}} \right)
            \frac{20 + \theta_{twe}}{0.0429 + \theta_{twe}} \right]
        \end{aligned}

    where :math:`\theta_{twe}` is the total water-equivalent content, :math:`r` is ``distance``,
    :math:`\rho_b` is ``ref_bulkdensity``, :math:`\theta_{lw}` is ``ref_latticewater`` and
    :math:`\theta_{soc}` is ``ref_soc``. The vegetation factor is fixed at 1.

    Reference:
        Schrön, M., Köhli, M., Scheiffele, L., Iwema, J., Bogena, H. R., Lv, L., Martini, E., Baroni, G.,
        Rosolem, R., Weimar, J., Mai, J., Cuntz, M., Rebmann, C., Oswald, S. E., Dietrich, P., Schmidt, U.,
        and Zacharias, S.
        Improving calibration and validation of cosmic-ray neutron sensors in the light of spatial sensitivity,
        Hydrol. Earth Syst. Sci., 21, 5009-5030, https://doi.org/10.5194/hess-21-5009-2017, 2017

    Args:
        cosmos_vwc: Volumetric Water Content (soil moisture) [%]
        pa: Atmospheric Pressure [hPa]
        ref_soc: Site attribute of reference soil organic carbon [g g-1]
        ref_bulkdensity: Site attribute of reference soil bulk density [g cm-3]
        ref_latticewater: Site attribute of reference lattice water content [g g-1]
        distance: Distance away from the CRNS the calculation is valid for [m]

    Returns:
        Expression or Series calculating d86 [cm]
    """
    # Constants used in the d86 calculation - from Schrön et al. (2017); Appendix A: Table A1
    p0 = 8.321
    p1 = 0.14249
    p2 = 0.96655
    p3 = 0.01
    p4 = 20.0
    p5 = 0.0429

    # Convert VWC from % to cm-3/cm-3
    cosmos_vwc = cosmos_vwc / 100.0
    # Reconstructs total water-equivalent content (free soil water [the current cosmos_vwc] + water bound in
    #   lattice/organic matter), for use in the footprint depth equation
    total_water_equivalent = cosmos_vwc + ref_bulkdensity * (ref_latticewater + ref_soc)

    # Calculate adjusted distance r_star
    fp = _parameter_function_fp(pa)
    # NOTE: There is a Fveg function in Schrön et al. (2017) that can adjust the D86 based on vegetation height.
    #   This would need a wider metadata update that is out of scope as of [08/2026]
    fveg = 1.0
    r_star = distance / fp / fveg

    # D86 equation from Schrön et al. (2017); Appendix A
    p2_term = p2 + (-p3 * r_star).exp()
    p4_term = p4 + total_water_equivalent
    p5_term = p5 + total_water_equivalent
    return (1 / ref_bulkdensity) * (p0 + (p1 * p2_term * (p4_term / p5_term)))


def _parameter_function_fp(pa: pl.Expr) -> pl.Expr:
    r"""Parameter function 'Fp' for use in the D86 calculation [unitless]

    .. math::

        F_p = \frac{0.4922}{0.86 - e^{-p_a / 1013}}

    Steps taken from Schrön et al. (2017); Appendix A: The revised weighting functions

    Args:
        pa: Atmospheric pressure [hPa]

    Returns:
        Expression or Series to calculate Fp [unitless]
    """
    # Constants used in the fp calculation - from Schrön et al. (2017); Appendix A: Table A1
    p0 = 0.4922
    p1 = 0.86
    return p0 / (p1 - ((-pa / 1013.0).exp()))
