from importlib.metadata import PackageNotFoundError, version

from hydrometlib import cosmos, evapotranspiration, flux, meteorology

try:
    __version__ = version("hydrometlib")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["cosmos", "evapotranspiration", "flux", "meteorology"]
