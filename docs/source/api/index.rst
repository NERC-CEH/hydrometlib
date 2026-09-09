.. _api-index:

==================
All calculations
==================

.. rst-class:: lead

    Every hydrometeorological calculation in the library, grouped by the module it lives in.

Each calculation is a single function. Click on a name for its equation, the paper or standard it comes from, its
units, and the meaning of every argument. The rules for what you can pass in and what comes back are the same for
all of them, and are set out in :ref:`flexible-inputs`.

meteorology
===========

Radiation balance and atmospheric-state variables. Full page: :doc:`meteorology`.

.. currentmodule:: hydrometlib.meteorology

.. autosummary::
    :nosignatures:

    absolute_humidity
    albedo
    is_snow_day
    mean_sea_level_pressure
    mean_soil_heat_flux
    net_radiation
    solar_zenith

evapotranspiration
==================

The FAO-56 Penman-Monteith calculation and the intermediate variables it is built from. Full page:
:doc:`evapotranspiration`.

.. currentmodule:: hydrometlib.evapotranspiration

.. autosummary::
    :nosignatures:

    actual_vapour_pressure
    latent_heat_of_vaporization
    potential_evapotranspiration_30min
    psychrometric_constant
    saturation_vapour_pressure
    vapour_pressure_curve_slope
    wind_speed_height_correction

cosmos (soil moisture)
======================

Cosmic-ray neutron sensor corrections, soil moisture, and snow water equivalent. Full page:
:doc:`cosmos_soil_moisture`.

.. currentmodule:: hydrometlib.cosmos

.. autosummary::
    :nosignatures:

    absolute_humidity_factor
    atmospheric_pressure_factor
    correct_counts
    d86
    effective_depth
    neutron_intensity_factor
    sigma_snow_water_equivalence
    sigma_snow_water_equivalence_snowfox
    snow_estimated_counts
    snow_water_equivalence
    snow_water_equivalence_snowfox
    soil_moisture_index
    volumetric_water_content

flux
====

Energy-balance fluxes and evapotranspiration from eddy-covariance data. Full page: :doc:`flux`.

.. currentmodule:: hydrometlib.flux

.. autosummary::
    :nosignatures:

    evapotranspiration_from_latent_heat_flux
    latent_heat_flux
