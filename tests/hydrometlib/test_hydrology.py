import pytest
from conftest import MODES, assert_allclose, run_case

from hydrometlib import hydrology as hy


@pytest.mark.parametrize("mode", MODES)
def test_distance_to_water_level_conversion(mode: str) -> None:
    """Test the saturation vapour pressure calculation."""
    got = run_case(
        hy.distance_to_water_level_conversion,
        {"dist_to_water": [11.1, 10.5, 0.5], "sensor_height": [1.0, 400.0, 1000.5]},
        mode=mode,
    )
    assert_allclose(got, [-10.1, 389.5, 1000.0], atol=0.001)
