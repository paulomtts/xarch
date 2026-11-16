"""The version an installed package records: read from its metadata, and none for a package that is not installed."""
from importlib import metadata

from xarch.platform.package_version import installed_version


def test_the_version_is_the_one_the_installed_package_records():
    assert installed_version("xarch") == metadata.version("xarch")
    assert installed_version("pytest") == metadata.version("pytest")


def test_a_package_that_is_not_installed_has_no_version():
    assert installed_version("xarch-no-such-package") is None
