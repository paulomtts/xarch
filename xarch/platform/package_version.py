"""The version an installed package records in its metadata, if it is installed. Knows no module."""
from __future__ import annotations

from importlib import metadata


def installed_version(package: str) -> str | None:
    """The version of the installed package; None when no metadata of it is found, as when its source is run without
    being installed."""
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return None
