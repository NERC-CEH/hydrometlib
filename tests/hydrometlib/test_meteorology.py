from datetime import datetime, timedelta

import pytest
from conftest import MODES, assert_allclose, run_case

from hydrometlib import meteorology as m

HOURLY_24 = [datetime(2025, 1, 1) + timedelta(hours=h) for h in range(24)]

SOLAR_ZENITH_24 = [
    2.599, 2.564, 2.472, 2.343, 2.198, 2.045, 1.893, 1.749, 1.618, 1.506, 1.419, 1.365,
    1.346, 1.365, 1.419, 1.506, 1.617, 1.749, 1.893, 2.045, 2.197, 2.344, 2.472, 2.564,
]  # fmt: skip


@pytest.mark.parametrize("mode", MODES)
def test_net_radiation(mode: str) -> None:
    """Test the net radiation calculation."""
    got = run_case(
        m.net_radiation,
        {
            "swin": [22.9, 19.3, 14, 25.1],
            "swout": [4.9, 4.2, 3, 5.5],
            "lwin": [24.1, 26, 26.2, 23.1],
            "lwout": [31.2, 31.9, 30.9, 30.8],
        },
        mode=mode,
    )
    assert_allclose(got, [10.9, 9.2, 6.3, 11.9], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_mean_soil_heat_flux(mode: str) -> None:
    """Test the mean soil heat flux calculation."""
    got = run_case(
        m.mean_soil_heat_flux,
        {"g1": [1.5, 10.9, 123.4], "g2": [-7.9, 0.01, 985.36]},
        mode=mode,
    )
    assert_allclose(got, [-3.2, 5.455, 554.38], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_mean_sea_level_pressure(mode: str) -> None:
    """Test the mean sea level pressure calculation."""
    got = run_case(
        m.mean_sea_level_pressure,
        {
            "pa": [1024.0, 1011.365, 1033.649, 1020.695],
            "ta": [1.977, 19.62, -2.144, 20.54],
        },
        {"altitude": 74},
        mode=mode,
    )
    assert_allclose(got, [1033.446, 1020.131, 1043.330, 1029.514], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_absolute_humidity(mode: str) -> None:
    """Test the absolute humidity calculation."""
    got = run_case(
        m.absolute_humidity,
        {"ta": [1.977, 19.62, -2.144, 20.54], "rh": [72.5, 57.62, 95.6, 65.41]},
        mode=mode,
    )
    assert_allclose(got, [4.025, 9.736, 3.994, 11.664], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_solar_zenith(mode: str) -> None:
    """Test the solar zenith angle calculation, over both daytime and nighttime."""
    got = run_case(m.solar_zenith, {"time": HOURLY_24}, {"latitude": 54.110665}, mode=mode)
    assert_allclose(got, SOLAR_ZENITH_24, atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_albedo(mode: str) -> None:
    """Test the albedo calculation, over both daytime and nighttime."""
    got = run_case(
        m.albedo,
        {
            "swin": [
                22.9,
                17.7,
                21.0,
                26.0,
                15.5,
                18.5,
                22.0,
                24.2,
                20.6,
                20.2,
                24.6,
                16.6,
                26.9,
                17.1,
                23.1,
                17.2,
                13.9,
                21.1,
                25.5,
                20.9,
                15.0,
                16.6,
                21.2,
                18.0,
            ],
            "swout": [
                2.6,
                4.0,
                5.6,
                3.0,
                5.9,
                2.8,
                4.0,
                5.4,
                3.8,
                3.7,
                4.2,
                3.8,
                5.0,
                4.7,
                5.7,
                3.0,
                2.6,
                5.4,
                3.0,
                4.5,
                3.3,
                5.7,
                5.5,
                4.3,
            ],
            "solar_zenith_angle": SOLAR_ZENITH_24,
        },
        mode=mode,
    )
    expected = [None] * 9 + [0.183, 0.171, 0.229, 0.186, 0.275, 0.247, 0.174] + [None] * 8
    assert_allclose(got, expected, atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_is_snow_day(mode: str) -> None:
    """Test the snow day calculation, over every combination of albedo values and nulls."""
    got = run_case(
        m.is_snow_day,
        {
            "albedo_expr": [
                None,
                0.20,
                None,
                0.40,
                None,
                0.60,
                0.10,
                None,
                0.10,
                0.20,
                0.10,
                0.40,
                0.10,
                0.60,
                0.45,
                None,
                0.45,
                0.20,
                0.45,
                0.40,
                0.45,
                0.60,
                0.65,
                None,
                0.65,
                0.20,
                0.65,
                0.40,
                0.65,
                0.60,
            ]
        },
        {"albedo_min_threshold": 0.35, "albedo_max_threshold": 0.5},
        mode=mode,
    )
    expected = [
        None, False, None, None, None, True, False, None, False, False, False, False, False, True, True,
        None, None, False, False, False, False, True, True, None, True, False, True, True, True, True
    ]  # fmt: skip
    assert_allclose(got, expected)
