"""The rules spec's values keep about themselves: which location names a file rather than a bundled profile, and the
name a profile switches each guard on by."""
from pathlib import Path

import pytest

from xarch.modules.spec.domain.guards import GUARDS
from xarch.modules.spec.domain.values import (
    ArchitectureSource,
    ClosedTree,
    DeadCode,
    NoComments,
    NoDuplicates,
    NoTwins,
    PackageOnly,
    PassThrough,
    PrivateImports,
)
from xarch.profile_values.testing import ScenarioCoverage, StandIns


@pytest.mark.parametrize("location, file", [
    pytest.param("web", False, id="a bare name is bundled"),
    pytest.param("arch.yaml", True, id="a suffix makes a path"),
    pytest.param("profiles/arch", True, id="a folder makes a path"),
    pytest.param(Path("web"), True, id="a path given as one names a file whatever it is called"),
])
def test_a_location_names_a_file_when_it_is_a_path_or_has_a_folder_or_a_suffix(location, file):
    assert ArchitectureSource.names_a_file(location) is file


def test_each_guard_is_switched_on_by_the_name_the_format_lists_it_under():
    guards = (PackageOnly, ScenarioCoverage, NoComments, StandIns, ClosedTree, NoDuplicates, NoTwins, DeadCode,
              PassThrough, PrivateImports)
    assert sorted(guard.key for guard in guards) == sorted(GUARDS)
