"""Type stubs for ``hydrometlib.cosmos``.

Auto-generated from the module's signatures by ``make stubs``.
"""

from typing import overload

import numpy as np
import pandas as pd
import polars as pl

@overload
def neutron_intensity_factor(crns_count: pl.Expr, ref_c0: float, gamma: float) -> pl.Expr: ...
@overload
def neutron_intensity_factor(crns_count: str, ref_c0: float, gamma: float) -> pl.Expr: ...
@overload
def neutron_intensity_factor(crns_count: pl.Series, ref_c0: float, gamma: float) -> pl.Series: ...
@overload
def neutron_intensity_factor(crns_count: pd.Series, ref_c0: float, gamma: float) -> pd.Series: ...
@overload
def neutron_intensity_factor(crns_count: np.ndarray, ref_c0: float, gamma: float) -> np.ndarray: ...
@overload
def absolute_humidity_factor(q: pl.Expr, ref_q0: float) -> pl.Expr: ...
@overload
def absolute_humidity_factor(q: str, ref_q0: float) -> pl.Expr: ...
@overload
def absolute_humidity_factor(q: pl.Series, ref_q0: float) -> pl.Series: ...
@overload
def absolute_humidity_factor(q: pd.Series, ref_q0: float) -> pd.Series: ...
@overload
def absolute_humidity_factor(q: np.ndarray, ref_q0: float) -> np.ndarray: ...
@overload
def atmospheric_pressure_factor(pa: pl.Expr, barometric_attenuation_length: float) -> pl.Expr: ...
@overload
def atmospheric_pressure_factor(pa: str, barometric_attenuation_length: float) -> pl.Expr: ...
@overload
def atmospheric_pressure_factor(pa: pl.Series, barometric_attenuation_length: float) -> pl.Series: ...
@overload
def atmospheric_pressure_factor(pa: pd.Series, barometric_attenuation_length: float) -> pd.Series: ...
@overload
def atmospheric_pressure_factor(pa: np.ndarray, barometric_attenuation_length: float) -> np.ndarray: ...
@overload
def correct_counts(cts_mod: pl.Expr, factor_inten: pl.Expr, factor_pa: pl.Expr, factor_q: pl.Expr) -> pl.Expr: ...
@overload
def correct_counts(cts_mod: str, factor_inten: str, factor_pa: str, factor_q: str) -> pl.Expr: ...
@overload
def correct_counts(
    cts_mod: pl.Series, factor_inten: pl.Series, factor_pa: pl.Series, factor_q: pl.Series
) -> pl.Series: ...
@overload
def correct_counts(
    cts_mod: pd.Series, factor_inten: pd.Series, factor_pa: pd.Series, factor_q: pd.Series
) -> pd.Series: ...
@overload
def correct_counts(
    cts_mod: np.ndarray, factor_inten: np.ndarray, factor_pa: np.ndarray, factor_q: np.ndarray
) -> np.ndarray: ...
@overload
def volumetric_water_content(
    cts_mod_corr: pl.Expr,
    ref_soc: float,
    ref_bulkdensity: float,
    ref_latticewater: float,
    n0_mod: float,
    n_min: float,
    n_max: float,
) -> pl.Expr: ...
@overload
def volumetric_water_content(
    cts_mod_corr: str,
    ref_soc: float,
    ref_bulkdensity: float,
    ref_latticewater: float,
    n0_mod: float,
    n_min: float,
    n_max: float,
) -> pl.Expr: ...
@overload
def volumetric_water_content(
    cts_mod_corr: pl.Series,
    ref_soc: float,
    ref_bulkdensity: float,
    ref_latticewater: float,
    n0_mod: float,
    n_min: float,
    n_max: float,
) -> pl.Series: ...
@overload
def volumetric_water_content(
    cts_mod_corr: pd.Series,
    ref_soc: float,
    ref_bulkdensity: float,
    ref_latticewater: float,
    n0_mod: float,
    n_min: float,
    n_max: float,
) -> pd.Series: ...
@overload
def volumetric_water_content(
    cts_mod_corr: np.ndarray,
    ref_soc: float,
    ref_bulkdensity: float,
    ref_latticewater: float,
    n0_mod: float,
    n_min: float,
    n_max: float,
) -> np.ndarray: ...
@overload
def snow_estimated_counts(cts_smo: pl.Expr, snow: pl.Expr, time: pl.Expr) -> pl.Expr: ...
@overload
def snow_estimated_counts(cts_smo: str, snow: str, time: str) -> pl.Expr: ...
@overload
def snow_estimated_counts(cts_smo: pl.Series, snow: pl.Series, time: pl.Series) -> pl.Series: ...
@overload
def snow_estimated_counts(cts_smo: pd.Series, snow: pd.Series, time: pd.Series) -> pd.Series: ...
@overload
def snow_estimated_counts(cts_smo: np.ndarray, snow: np.ndarray, time: np.ndarray) -> np.ndarray: ...
@overload
def snow_water_equivalence(cts_smo: pl.Expr, cts_est: pl.Expr, n0_mod: float) -> pl.Expr: ...
@overload
def snow_water_equivalence(cts_smo: str, cts_est: str, n0_mod: float) -> pl.Expr: ...
@overload
def snow_water_equivalence(cts_smo: pl.Series, cts_est: pl.Series, n0_mod: float) -> pl.Series: ...
@overload
def snow_water_equivalence(cts_smo: pd.Series, cts_est: pd.Series, n0_mod: float) -> pd.Series: ...
@overload
def snow_water_equivalence(cts_smo: np.ndarray, cts_est: np.ndarray, n0_mod: float) -> np.ndarray: ...
@overload
def snow_water_equivalence_snowfox(cts_smo: pl.Expr, cts_est: pl.Expr) -> pl.Expr: ...
@overload
def snow_water_equivalence_snowfox(cts_smo: str, cts_est: str) -> pl.Expr: ...
@overload
def snow_water_equivalence_snowfox(cts_smo: pl.Series, cts_est: pl.Series) -> pl.Series: ...
@overload
def snow_water_equivalence_snowfox(cts_smo: pd.Series, cts_est: pd.Series) -> pd.Series: ...
@overload
def snow_water_equivalence_snowfox(cts_smo: np.ndarray, cts_est: np.ndarray) -> np.ndarray: ...
@overload
def sigma_snow_water_equivalence(cts_smo: pl.Expr, cts_est: pl.Expr, n0_mod: float) -> pl.Expr: ...
@overload
def sigma_snow_water_equivalence(cts_smo: str, cts_est: str, n0_mod: float) -> pl.Expr: ...
@overload
def sigma_snow_water_equivalence(cts_smo: pl.Series, cts_est: pl.Series, n0_mod: float) -> pl.Series: ...
@overload
def sigma_snow_water_equivalence(cts_smo: pd.Series, cts_est: pd.Series, n0_mod: float) -> pd.Series: ...
@overload
def sigma_snow_water_equivalence(cts_smo: np.ndarray, cts_est: np.ndarray, n0_mod: float) -> np.ndarray: ...
@overload
def sigma_snow_water_equivalence_snowfox(cts_smo: pl.Expr, cts_est: pl.Expr) -> pl.Expr: ...
@overload
def sigma_snow_water_equivalence_snowfox(cts_smo: str, cts_est: str) -> pl.Expr: ...
@overload
def sigma_snow_water_equivalence_snowfox(cts_smo: pl.Series, cts_est: pl.Series) -> pl.Series: ...
@overload
def sigma_snow_water_equivalence_snowfox(cts_smo: pd.Series, cts_est: pd.Series) -> pd.Series: ...
@overload
def sigma_snow_water_equivalence_snowfox(cts_smo: np.ndarray, cts_est: np.ndarray) -> np.ndarray: ...
@overload
def soil_moisture_index(
    cosmos_vwc: pl.Expr, wilting_point: pl.Expr, field_capacity: pl.Expr, saturation: pl.Expr
) -> pl.Expr: ...
@overload
def soil_moisture_index(cosmos_vwc: str, wilting_point: str, field_capacity: str, saturation: str) -> pl.Expr: ...
@overload
def soil_moisture_index(
    cosmos_vwc: pl.Series, wilting_point: pl.Series, field_capacity: pl.Series, saturation: pl.Series
) -> pl.Series: ...
@overload
def soil_moisture_index(
    cosmos_vwc: pd.Series, wilting_point: pd.Series, field_capacity: pd.Series, saturation: pd.Series
) -> pd.Series: ...
@overload
def soil_moisture_index(
    cosmos_vwc: np.ndarray, wilting_point: np.ndarray, field_capacity: np.ndarray, saturation: np.ndarray
) -> np.ndarray: ...
@overload
def effective_depth(
    cosmos_vwc: pl.Expr, ref_soc: float, ref_bulkdensity: float, ref_latticewater: float
) -> pl.Expr: ...
@overload
def effective_depth(cosmos_vwc: str, ref_soc: float, ref_bulkdensity: float, ref_latticewater: float) -> pl.Expr: ...
@overload
def effective_depth(
    cosmos_vwc: pl.Series, ref_soc: float, ref_bulkdensity: float, ref_latticewater: float
) -> pl.Series: ...
@overload
def effective_depth(
    cosmos_vwc: pd.Series, ref_soc: float, ref_bulkdensity: float, ref_latticewater: float
) -> pd.Series: ...
@overload
def effective_depth(
    cosmos_vwc: np.ndarray, ref_soc: float, ref_bulkdensity: float, ref_latticewater: float
) -> np.ndarray: ...
@overload
def d86(
    cosmos_vwc: pl.Expr, pa: pl.Expr, ref_soc: float, ref_bulkdensity: float, ref_latticewater: float, distance: float
) -> pl.Expr: ...
@overload
def d86(
    cosmos_vwc: str, pa: str, ref_soc: float, ref_bulkdensity: float, ref_latticewater: float, distance: float
) -> pl.Expr: ...
@overload
def d86(
    cosmos_vwc: pl.Series,
    pa: pl.Series,
    ref_soc: float,
    ref_bulkdensity: float,
    ref_latticewater: float,
    distance: float,
) -> pl.Series: ...
@overload
def d86(
    cosmos_vwc: pd.Series,
    pa: pd.Series,
    ref_soc: float,
    ref_bulkdensity: float,
    ref_latticewater: float,
    distance: float,
) -> pd.Series: ...
@overload
def d86(
    cosmos_vwc: np.ndarray,
    pa: np.ndarray,
    ref_soc: float,
    ref_bulkdensity: float,
    ref_latticewater: float,
    distance: float,
) -> np.ndarray: ...
