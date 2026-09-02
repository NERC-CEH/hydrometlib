"""Type stubs for ``hydrometlib.evapotranspiration``."""

from typing import overload

import numpy as np
import pandas as pd
import polars as pl

@overload
def actual_vapour_pressure(es: pl.Expr, rh: pl.Expr) -> pl.Expr: ...
@overload
def actual_vapour_pressure(es: str, rh: str) -> pl.Expr: ...
@overload
def actual_vapour_pressure(es: pl.Series, rh: pl.Series) -> pl.Series: ...
@overload
def actual_vapour_pressure(es: pd.Series, rh: pd.Series) -> pd.Series: ...
@overload
def actual_vapour_pressure(es: np.ndarray, rh: np.ndarray) -> np.ndarray: ...
@overload
def latent_heat_of_vaporization(ta: pl.Expr) -> pl.Expr: ...
@overload
def latent_heat_of_vaporization(ta: str) -> pl.Expr: ...
@overload
def latent_heat_of_vaporization(ta: pl.Series) -> pl.Series: ...
@overload
def latent_heat_of_vaporization(ta: pd.Series) -> pd.Series: ...
@overload
def latent_heat_of_vaporization(ta: np.ndarray) -> np.ndarray: ...
@overload
def potential_evapotranspiration_30min(
    rn: pl.Expr,
    g: pl.Expr,
    ta: pl.Expr,
    rh: pl.Expr,
    ws: pl.Expr,
    pa: pl.Expr,
    wind_height: pl.Expr,
) -> pl.Expr: ...
@overload
def potential_evapotranspiration_30min(
    rn: str,
    g: str,
    ta: str,
    rh: str,
    ws: str,
    pa: str,
    wind_height: str,
) -> pl.Expr: ...
@overload
def potential_evapotranspiration_30min(
    rn: pl.Series,
    g: pl.Series,
    ta: pl.Series,
    rh: pl.Series,
    ws: pl.Series,
    pa: pl.Series,
    wind_height: pl.Series,
) -> pl.Series: ...
@overload
def potential_evapotranspiration_30min(
    rn: pd.Series,
    g: pd.Series,
    ta: pd.Series,
    rh: pd.Series,
    ws: pd.Series,
    pa: pd.Series,
    wind_height: pd.Series,
) -> pd.Series: ...
@overload
def potential_evapotranspiration_30min(
    rn: np.ndarray,
    g: np.ndarray,
    ta: np.ndarray,
    rh: np.ndarray,
    ws: np.ndarray,
    pa: np.ndarray,
    wind_height: np.ndarray,
) -> np.ndarray: ...
@overload
def psychrometric_constant(pa: pl.Expr, lv: pl.Expr) -> pl.Expr: ...
@overload
def psychrometric_constant(pa: str, lv: str) -> pl.Expr: ...
@overload
def psychrometric_constant(pa: pl.Series, lv: pl.Series) -> pl.Series: ...
@overload
def psychrometric_constant(pa: pd.Series, lv: pd.Series) -> pd.Series: ...
@overload
def psychrometric_constant(pa: np.ndarray, lv: np.ndarray) -> np.ndarray: ...
@overload
def saturation_vapour_pressure(ta: pl.Expr) -> pl.Expr: ...
@overload
def saturation_vapour_pressure(ta: str) -> pl.Expr: ...
@overload
def saturation_vapour_pressure(ta: pl.Series) -> pl.Series: ...
@overload
def saturation_vapour_pressure(ta: pd.Series) -> pd.Series: ...
@overload
def saturation_vapour_pressure(ta: np.ndarray) -> np.ndarray: ...
@overload
def vapour_pressure_curve_slope(es: pl.Expr, ta: pl.Expr) -> pl.Expr: ...
@overload
def vapour_pressure_curve_slope(es: str, ta: str) -> pl.Expr: ...
@overload
def vapour_pressure_curve_slope(es: pl.Series, ta: pl.Series) -> pl.Series: ...
@overload
def vapour_pressure_curve_slope(es: pd.Series, ta: pd.Series) -> pd.Series: ...
@overload
def vapour_pressure_curve_slope(es: np.ndarray, ta: np.ndarray) -> np.ndarray: ...
@overload
def wind_speed_height_correction(ws: pl.Expr, measured_height: pl.Expr) -> pl.Expr: ...
@overload
def wind_speed_height_correction(ws: str, measured_height: str) -> pl.Expr: ...
@overload
def wind_speed_height_correction(ws: pl.Series, measured_height: pl.Series) -> pl.Series: ...
@overload
def wind_speed_height_correction(ws: pd.Series, measured_height: pd.Series) -> pd.Series: ...
@overload
def wind_speed_height_correction(ws: np.ndarray, measured_height: np.ndarray) -> np.ndarray: ...
