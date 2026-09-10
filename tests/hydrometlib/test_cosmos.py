from datetime import datetime, timedelta

import polars as pl
import pytest
from conftest import MODES, assert_allclose, run_case

from hydrometlib import cosmos as c

# cosmos-holln site parameters, reused across several calculations
HOLLN = {
    "n0_mod": 2710.16689,
    "ref_bulkdensity": 1.06,
    "ref_latticewater": 0.025,
    "ref_soc": 0.032,
    "n_min": 1204.50827,
    "n_max": 2281.33025,
}


@pytest.mark.parametrize("mode", MODES)
def test_neutron_intensity_factor(mode: str) -> None:
    """Test the incoming neutron intensity correction factor calculation."""
    # ref_c0 and gamma are cosmos-holln site annotations.
    got = run_case(
        c.neutron_intensity_factor,
        {"crns_count": [150.1, 151.2, 153.3, 154.4]},
        {"ref_c0": 152.03496, "gamma": 1.29291},
        mode=mode,
    )
    assert_allclose(got, [1.016, 1.007, 0.989, 0.980], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_absolute_humidity_factor(mode: str) -> None:
    """Test the absolute humidity correction factor calculation."""
    # ref_q0 [g m-3] is the cosmos-holln site annotation.
    got = run_case(
        c.absolute_humidity_factor,
        {"q": [4.025, 9.736, 3.994, 11.664]},
        {"ref_q0": 8.27},
        mode=mode,
    )
    assert_allclose(got, [0.97707, 1.00791, 0.97690, 1.01832], atol=1e-5)


@pytest.mark.parametrize("mode", MODES)
def test_atmospheric_pressure_factor(mode: str) -> None:
    """Test the atmospheric pressure correction factor calculation."""
    # the attenuation length [m] is a cosmos-holln site annotation.
    got = run_case(
        c.atmospheric_pressure_factor,
        {"pa": [1024.0, 1011.365, 1033.649, 1020.695]},
        {"barometric_attenuation_length": 137.04156},
        mode=mode,
    )
    assert_allclose(got, [1.1914, 1.08646, 1.27831, 1.16301], atol=1e-5)


@pytest.mark.parametrize("mode", MODES)
def test_correct_counts(mode: str) -> None:
    """Test the corrected counts calculation."""
    # cts_mod values from cosmos-holln on 2016-07-27. Factor values are the holln expected
    # outputs of the three factor tests above.
    got = run_case(
        c.correct_counts,
        {
            "cts_mod": [749.0, 746.0, 793.0, 734.0],
            "factor_inten": [1.016, 1.007, 0.989, 0.980],
            "factor_pa": [1.1914, 1.08646, 1.27831, 1.16301],
            "factor_q": [0.97707, 1.00791, 0.97690, 1.01832],
        },
        mode=mode,
    )
    assert_allclose(got, [885.847, 822.629, 979.390, 851.902], atol=0.01)


@pytest.mark.parametrize("mode", MODES)
def test_volumetric_water_content(mode: str) -> None:
    """Test the volumetric water content calculation."""
    got = run_case(
        c.volumetric_water_content,
        {"cts_mod_corr": [0.0, 885.847, 822.629, 979.390, 851.902, 1300.0, 1500.0, 1800.0, 2000.0]},
        HOLLN,
        mode=mode,
    )
    assert_allclose(got, [100.0, 100.0, 100.0, 100.0, 100.0, 61.311, 28.964, 11.083, 5.172], atol=0.1)


@pytest.mark.parametrize("mode", MODES)
def test_snow_water_equivalence_theoretical(mode: str) -> None:
    """Test that SWE is ~0 when smoothed counts match the estimate, and grows as counts are suppressed."""
    got = run_case(
        c.snow_water_equivalence,
        {
            "cts_smo": [1500.0, 1600.0, 1500.0, 1750.0],
            "cts_est": [1500.0, 1800.0, 2000.0, 1750.0],
        },
        {"n0_mod": 2710.16689},
        mode=mode,
    )
    assert_allclose(got, [0.0, 14.4332, 34.7719, 0.0], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_snow_water_equivalence_real_data(mode: str) -> None:
    """Test that SWE matches real COSMOS-UK values."""
    # Reference values from published COSMOS-UK daily Level 3 data:
    #   Site: BALRD,
    #   Dates: [2018-03-04 00:00:00, 2015-11-29 00:00:00, 2021-02-09 00:00:00]
    # n0_mod 2966.89129 is the published BALRD field calibration (method 4).
    got = run_case(
        c.snow_water_equivalence,
        {
            "cts_smo": [1404.65, 1674.98, 1485.63],
            "cts_est": [1679.48307, 1680.79596, 1633.42392],
        },
        {"n0_mod": 2966.89129},
        mode=mode,
    )
    assert_allclose(got, [33.06285, 0.50709, 16.57987], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_snow_water_equivalence_snowfox(mode: str) -> None:
    """Test that snowfox SWE is ~0 without count suppression, and grows as counts are suppressed."""
    got = run_case(
        c.snow_water_equivalence_snowfox,
        {
            "cts_smo": [1500.0, 1600.0, 1500.0, 1750.0],
            "cts_est": [1500.0, 1800.0, 2000.0, 1750.0],
        },
        mode=mode,
    )
    assert_allclose(got, [0.0, 16.634605, 40.793911, 0.0], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_sigma_snow_water_equivalence(mode: str) -> None:
    """Test that SWE uncertainty stays positive even where SWE itself is ~0."""
    got = run_case(
        c.sigma_snow_water_equivalence,
        {
            "cts_smo": [1500.0, 1600.0, 1500.0, 1750.0],
            "cts_est": [1500.0, 1800.0, 2000.0, 1750.0],
        },
        {"n0_mod": 2710.16689},
        mode=mode,
    )
    assert_allclose(got, [1.467, 1.0158, 1.002, 0.981], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_sigma_snow_water_equivalence_snowfox(mode: str) -> None:
    """Test that snowfox SWE uncertainty stays positive even where SWE itself is ~0."""
    got = run_case(
        c.sigma_snow_water_equivalence_snowfox,
        {
            "cts_smo": [1500.0, 1600.0, 1500.0, 1750.0],
            "cts_est": [1500.0, 1800.0, 2000.0, 1750.0],
        },
        mode=mode,
    )
    assert_allclose(got, [1.8679, 1.4304, 1.128, 1.627], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize(
    ("vwc", "expected"),
    [
        ([5.0, 10.0], [0.0, 0.0]),
        ([20.0, 30.0], [0.5, 1.0]),
        ([40.0, 50.0], [1.5, 2.0]),
        ([60.0, 45.0], [2.0, 1.75]),
        ([None, 20.0], [None, 0.5]),
    ],
)
def test_soil_moisture_index(mode: str, vwc: list[float | None], expected: list[float | None]) -> None:
    """Test that the soil moisture index is correct at each breakpoint from wilting point to saturation."""
    n = len(vwc)
    got = run_case(
        c.soil_moisture_index,
        {
            "cosmos_vwc": vwc,
            "wilting_point": [10.0] * n,
            "field_capacity": [30.0] * n,
            "saturation": [50.0] * n,
        },
        mode=mode,
    )
    assert_allclose(got, expected)


@pytest.mark.parametrize("mode", MODES)
def test_effective_depth(mode: str) -> None:
    """Test the effective measurement depth calculation."""
    # Reference soil attributes are cosmos-holln site annotations.
    got = run_case(
        c.effective_depth,
        {"cosmos_vwc": [0.0, 10.0, 28.964, 61.311, 100.0]},
        {"ref_bulkdensity": 1.06, "ref_latticewater": 0.025, "ref_soc": 0.032},
        mode=mode,
    )
    assert_allclose(got, [40.469, 23.837, 13.396, 7.668, 5.073], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize(
    ("distance", "expected"),
    [
        (1.0, [23.2, 16.7, 19.3, 17]),
        (5.0, [22.9, 16.5, 19, 16.9]),
        (25.0, [21.6, 15.7, 18, 16]),
        (75.0, [19.2, 14.4, 16.3, 14.6]),
        (150.0, [17.2, 13.2, 14.8, 13.4]),
        (200.0, [16.5, 12.8, 14.3, 13]),
    ],
)
def test_d86(mode: str, distance: float, expected: list[float]) -> None:
    """Test the d86 calculation."""
    # Reference values from published COSMOS-UK daily Level 3 data:
    #   Site: HOLLN,
    #   Dates: [2015-03-14, 2017-05-30, 2022-01-18, 2026-08-01]
    got = run_case(
        c.d86,
        {
            "cosmos_vwc": [24.4, 50.7, 36.7, 48.5],
            "pa": [1010.2, 1024.7, 1002.6, 1025.1],
        },
        {"ref_bulkdensity": 1.06, "ref_latticewater": 0.025, "ref_soc": 0.032, "distance": distance},
        mode=mode,
    )
    assert_allclose(got, expected, atol=0.1)


def _broadcast_hourly(daily: list) -> list:
    return [value for day in daily for value in [day] * 24]


@pytest.mark.parametrize("mode", MODES)
def test_snow_estimated_counts(mode: str) -> None:
    """Test that snow-period counts are estimated from the smoothed counts just before the snow period."""
    # Fictional data, constructed so that snow suppresses the counts.
    daily_cts = [995.0, 1000, 1002, 995, 996, 1003, 997, 1001, 1002, 1003, 995]
    daily_snow = [True, False, False, True, True, False, True, False, False, True, True]
    daily_expected = [None, None, None, 1002.0, 1002.0, 1003.0, 1002.0, None, None, 1003.0, 1002.0]

    cts = _broadcast_hourly(daily_cts)
    time = [datetime(2025, 1, 1) + timedelta(hours=h) for h in range(len(cts))]

    got = run_case(
        c.snow_estimated_counts,
        {"cts_smo": cts, "snow": _broadcast_hourly(daily_snow), "time": time},
        mode=mode,
    )
    assert_allclose(got, _broadcast_hourly(daily_expected), atol=0.1)


@pytest.mark.parametrize("mode", MODES)
def test_snow_estimated_counts_all_snow_gives_no_estimate(mode: str) -> None:
    """Test that no counts are estimated when the whole record consists of snow days."""
    # Fictional data: with no pre-snow period, there is no baseline to estimate from.
    daily_cts = [995.0, 996, 997, 998]
    cts = _broadcast_hourly(daily_cts)
    time = [datetime(2025, 1, 1) + timedelta(hours=h) for h in range(len(cts))]

    got = run_case(
        c.snow_estimated_counts,
        {"cts_smo": cts, "snow": _broadcast_hourly([True, True, True, True]), "time": time},
        mode=mode,
    )
    assert_allclose(got, [None] * len(cts), atol=0.1)


def test_site_attributes_can_come_from_a_column() -> None:
    """Test a multi-site frame: n0_mod joined on as a column matches calling each site with its number."""
    counts = [1600.0, 1750.0]
    n0 = [2000.0, 2200.0]
    joined = c.volumetric_water_content(pl.Series("cts", counts), 0.01, 1.4, 0.02, pl.Series("n0", n0), 500.0, 4000.0)
    per_site = [
        c.volumetric_water_content(pl.Series("cts", [count]), 0.01, 1.4, 0.02, n0_mod, 500.0, 4000.0).to_list()[0]
        for count, n0_mod in zip(counts, n0, strict=True)
    ]
    assert_allclose(joined.to_list(), per_site)
