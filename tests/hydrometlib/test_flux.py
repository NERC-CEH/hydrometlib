import pytest
from conftest import MODES, assert_allclose, run_case

from hydrometlib import flux


@pytest.mark.parametrize("mode", MODES)
def test_latent_heat_flux(mode: str) -> None:
    """Test the latent heat flux calculation."""
    got = run_case(
        flux.latent_heat_flux,
        {"rn": [300.0, 500.0], "shf": [50.0, 20.0], "h": [100.0, 180.0]},
        mode=mode,
    )
    assert_allclose(got, [150.0, 300.0])


@pytest.mark.parametrize("mode", MODES)
def test_latent_heat_flux_null_propagates(mode: str) -> None:
    """Test that a null in any input propagates through to a null latent heat flux."""
    got = run_case(
        flux.latent_heat_flux,
        {"rn": [None, 300.0], "shf": [50.0, 50.0], "h": [100.0, 100.0]},
        mode=mode,
    )
    assert_allclose(got, [None, 150.0])


@pytest.mark.parametrize("mode", MODES)
def test_evapotranspiration_from_latent_heat_flux(mode: str) -> None:
    """Test that latent heat flux converts to ET via the temperature-dependent latent heat of vaporization."""
    got = run_case(
        flux.evapotranspiration_from_latent_heat_flux,
        {"le": [150.0, 200.0], "ta": [20.0, 15.0]},
        mode=mode,
    )
    assert_allclose(got, [0.22006862, 0.29201993], atol=1e-7)


@pytest.mark.parametrize("mode", MODES)
def test_evapotranspiration_from_latent_heat_flux_fao56_equivalence(mode: str) -> None:
    """Test against FAO-56 Table 1: 2.45 MJ m-2 day-1 is 1 mm day-1 where lambda is 2.45 MJ kg-1."""
    ta_lambda_2_45 = (2.501 - 2.45) / 2.361e-3  # air temperature at which lambda = 2.45 MJ kg-1
    got = run_case(
        flux.evapotranspiration_from_latent_heat_flux,
        {"le": [2.45e6 / 86400], "ta": [ta_lambda_2_45]},
        mode=mode,
    )
    assert_allclose(got, [1 / 24], atol=1e-9)


@pytest.mark.parametrize("mode", MODES)
def test_evapotranspiration_from_latent_heat_flux_null_propagates(mode: str) -> None:
    """Test that a null in either input propagates through to a null ET."""
    got = run_case(
        flux.evapotranspiration_from_latent_heat_flux,
        {"le": [None, 150.0], "ta": [20.0, None]},
        mode=mode,
    )
    assert_allclose(got, [None, None])
