"""Top-level package for Hydrometeorology Calculation Library."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("hydrometlib")
except PackageNotFoundError:
    __version__ = "unknown"
