"""The version an installed package records in its metadata. Knows no module."""
from __future__ import annotations

from importlib import metadata


def installed_version(package: str) -> str:
    """The version of the installed package; raises importlib.metadata.PackageNotFoundError if none is installed."""
    return metadata.version(package)
