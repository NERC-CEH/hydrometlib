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
    assert_allclose(got, [0.06113017, 0.08111665], atol=1e-5)
