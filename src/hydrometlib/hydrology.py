import polars as pl

from hydrometlib._dispatch import Attribute, flexible


@flexible
def distance_to_water_level_conversion(dist_to_water: pl.Expr, sensor_height: Attribute) -> pl.Expr:
    r"""Calculate water level from sensor height and distance measured between sensor and water surface.

    .. math::

        water_level = sensor_height - dist_to_water

    Args:
        dist_to_water: Distance between sensor and water surface [cm]
        sensor_height: Height above river bed that the sensor is installed [cm]

    Returns:
        Expression or Series to calculate water level
    """
    return sensor_height - dist_to_water
