"""Where a profile comes from: a bare name is a bundled profile, anything else a path to a file, and a bare name that
is no bundled profile is refused with the ones there are."""
from pathlib import Path

import pytest

from xarch.modules.spec.application.logic.profile_file import source_of
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import ArchitectureSource


@pytest.mark.parametrize("location, found", [
    pytest.param("cli", ArchitectureSource("cli", bundled=True), id="a bare name is a bundled profile"),
    pytest.param("mine.yaml", ArchitectureSource("mine.yaml", bundled=False), id="a name with a suffix is a file"),
    pytest.param("arch/cli", ArchitectureSource("arch/cli", bundled=False), id="a name with a folder is a file"),
    pytest.param(Path("cli"), ArchitectureSource("cli", bundled=False), id="a path is a file"),
])
def test_a_bare_name_is_a_bundled_profile_and_anything_else_a_file(location, found):
    assert source_of(location, ("cli", "web")) == found


def test_a_bare_name_that_is_no_bundled_profile_is_refused_with_the_ones_there_are():
    with pytest.raises(InvalidArchitecture) as caught:
        source_of("nope", ("cli", "web"))
    assert caught.value.problems == (
        "nope: no bundled architecture 'nope': use one of cli, web, or a path to a .yaml or .json file",)
