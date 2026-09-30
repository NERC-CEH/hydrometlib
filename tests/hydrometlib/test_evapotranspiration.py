import pytest
from conftest import MODES, assert_allclose, run_case

from hydrometlib import evapotranspiration as et


@pytest.mark.parametrize("mode", MODES)
def test_saturation_vapour_pressure(mode: str) -> None:
    """Test the saturation vapour pressure calculation."""
    # Taken from FAO56 EXAMPLE 3 https://www.fao.org/4/x0490e/x0490e07.htm
    got = run_case(et.saturation_vapour_pressure, {"ta": [15.0, 24.5]}, mode=mode)
    assert_allclose(got, [1.705, 3.075], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_actual_vapour_pressure(mode: str) -> None:
    """Test the actual vapour pressure calculation."""
    # Taken from FAO56 EXAMPLE 19 https://www.fao.org/4/x0490e/x0490e08.htm
    got = run_case(et.actual_vapour_pressure, {"es": [3.78, 6.625], "rh": [90, 52]}, mode=mode)
    assert_allclose(got, [3.402, 3.445], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_vapour_pressure_curve_slope(mode: str) -> None:
    """Test the saturation vapour pressure curve calculation."""
    # Taken from FAO56 EXAMPLES 18, 19 and 20 https://www.fao.org/4/x0490e/x0490e08.htm
    got = run_case(
        et.vapour_pressure_curve_slope,
        {"es": [1.997, 2.58, 3.78, 6.625], "ta": [16.9, 20.7, 28, 38]},
        mode=mode,
    )
    assert_allclose(got, [0.122, 0.15, 0.22, 0.358], atol=0.01)


@pytest.mark.parametrize("mode", MODES)
def test_latent_heat_of_vaporization(mode: str) -> None:
    """Test the latent heat of vaporization calculation."""
    got = run_case(et.latent_heat_of_vaporization, {"ta": [-20.0, 0.0, 20.0, 100.0]}, mode=mode)
    assert_allclose(got, [2.54, 2.501, 2.45, 2.26], atol=0.01)


@pytest.mark.parametrize("mode", MODES)
def test_psychrometric_constant(mode: str) -> None:
    """Test the psychrometric constant calculation."""
    # Taken from FAO56 EXAMPLE 2 https://www.fao.org/4/x0490e/x0490e07.htm#psychrometric%20constant%20(g)
    # and FAO56 EXAMPLE 18 https://www.fao.org/4/x0490e/x0490e08.htm
    got = run_case(
        et.psychrometric_constant,
        {"pa": [1001.0, 818.0], "lv": [2.45, 2.46]},
        mode=mode,
    )
    assert_allclose(got, [0.066, 0.054], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_wind_speed_height_correction(mode: str) -> None:
    """Test that wind speed measured at 10 m is corrected down to the 2 m reference height."""
    # Taken from FAO56 EXAMPLE 14 https://www.fao.org/4/x0490e/x0490e07.htm#wind%20profile%20relationship
    got = run_case(
        et.wind_speed_height_correction,
        {"ws": [3.2], "measured_height": [10.0]},
        mode=mode,
    )
    assert_allclose(got, [2.4], atol=0.01)


@pytest.mark.parametrize("mode", MODES)
def test_potential_evapotranspiration_30min(mode: str) -> None:
    """Test that end-to-end 30-minute Penman-Monteith PET matches observed COSMOS-UK values."""
    # Reference values from published COSMOS-UK 30-minute Level 3 data:
    #   Site: CHOBH,
    #   Dates: [2015-03-14 04:30:00, 2017-05-30 16:30:00, 2022-01-18 09:30:00, 2023-08-21 11:00:00]
    got = run_case(
        et.potential_evapotranspiration_30min,
        {
            "rn": [-68.181, 302.85, 116.2, 364.6],
            "g": [-29.6453, 32.23711, -23.7416, 16.64824],
            "ta": [1.977, 19.62, -2.144, 20.54],
            "rh": [72.5, 57.62, 95.6, 65.41],
            "ws": [2.89954, 3.204, 0.214, 2.048],
            "pa": [1024.0, 1011.365, 1033.649, 1020.695],
            "wind_height": [2.6, 2.6, 2.6, 2.6],
        },
        mode=mode,
    )
    assert_allclose(got, [0.00573, 0.14733, 0.03617, 0.17283], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_potential_evapotranspiration_30min_wind_height_optional(mode: str) -> None:
    """Test that omitting wind_height skips the height correction and uses ws directly at 2 m."""
    got = run_case(
        et.potential_evapotranspiration_30min,
        {
            "rn": [-68.181, 302.85, 116.2, 364.6],
            "g": [-29.6453, 32.23711, -23.7416, 16.64824],
            "ta": [1.977, 19.62, -2.144, 20.54],
            "rh": [72.5, 57.62, 95.6, 65.41],
            "ws": [2.89954, 3.204, 0.214, 2.048],
            "pa": [1024.0, 1011.365, 1033.649, 1020.695],
        },
        mode=mode,
    )
    assert_allclose(got, [0.00637, 0.14784, 0.03610, 0.17271], atol=0.001)


@pytest.mark.parametrize("mode", MODES)
def test_latent_heat_flux(mode: str) -> None:
    """Test the latent heat flux calculation."""
    got = run_case(
        et.latent_heat_flux,
        {"rn": [300.0, 500.0], "g": [50.0, 20.0], "h": [100.0, 180.0]},
        mode=mode,
    )
    assert_allclose(got, [150.0, 300.0])


@pytest.mark.parametrize("mode", MODES)
def test_latent_heat_flux_null_propagates(mode: str) -> None:
    """Test that a null in any input propagates through to a null latent heat et."""
    got = run_case(
        et.latent_heat_flux,
        {"rn": [None, 300.0], "g": [50.0, 50.0], "h": [100.0, 100.0]},
        mode=mode,
    )
    assert_allclose(got, [None, 150.0])


@pytest.mark.parametrize("mode", MODES)
def test_evapotranspiration_from_latent_heat_flux(mode: str) -> None:
    """Test that latent heat flux converts to ET via the temperature-dependent latent heat of vaporization."""
    got = run_case(
        et.evapotranspiration_from_latent_heat_flux,
        {"le": [150.0, 200.0], "ta": [20.0, 15.0]},
        mode=mode,
    )
    assert_allclose(got, [0.22006862, 0.29201993], atol=1e-7)


@pytest.mark.parametrize("mode", MODES)
def test_evapotranspiration_from_latent_heat_flux_fao56_equivalence(mode: str) -> None:
    """Test against FAO-56 Table 1: 2.45 MJ m-2 day-1 is 1 mm day-1 where lambda is 2.45 MJ kg-1."""
    ta_lambda_2_45 = (2.501 - 2.45) / 2.361e-3  # air temperature at which lambda = 2.45 MJ kg-1
    got = run_case(
        et.evapotranspiration_from_latent_heat_flux,
        {"le": [2.45e6 / 86400], "ta": [ta_lambda_2_45]},
        mode=mode,
    )
    assert_allclose(got, [1 / 24], atol=1e-9)


@pytest.mark.parametrize("mode", MODES)
def test_evapotranspiration_from_latent_heat_flux_null_propagates(mode: str) -> None:
    """Test that a null in either input propagates through to a null ET."""
    got = run_case(
        et.evapotranspiration_from_latent_heat_flux,
        {"le": [None, 150.0], "ta": [20.0, None]},
        mode=mode,
    )
    assert_allclose(got, [None, None])
