"""The version an installed package records: read from its metadata, and a missing package raises."""
from importlib import metadata

import pytest

from xarch.platform.package_version import installed_version


def test_the_version_is_the_one_the_installed_package_records():
    assert installed_version("xarch") == metadata.version("xarch")
    assert installed_version("pytest") == metadata.version("pytest")


def test_a_package_that_is_not_installed_raises():
    with pytest.raises(metadata.PackageNotFoundError):
        installed_version("xarch-no-such-package")
