"""Which profile is in force: one given wins over one configured, a path is read from the file that configures it, and a
bare name must be bundled."""
from pathlib import Path

import pytest

from xarch.modules.spec.application.logic.profile_in_force import choose, is_path
from xarch.modules.spec.domain.errors import NoProfile, UnknownProfile
from xarch.modules.spec.domain.values import Configured

BUNDLED = ("cli", "web")
CONFIGURED = Configured("profiles/arch.yaml", Path("/src/pyproject.toml"))


@pytest.mark.parametrize("location, path", [
    pytest.param("web", False, id="a bare name is bundled"),
    pytest.param("arch.yaml", True, id="a suffix makes a path"),
    pytest.param("profiles/arch", True, id="a folder makes a path"),
])
def test_is_path(location, path):
    assert is_path(location) == path


@pytest.mark.parametrize("override, configured, chosen", [
    pytest.param("web", CONFIGURED, "web", id="a profile given wins over the configured one"),
    pytest.param("my/arch.yaml", None, "my/arch.yaml", id="a path given is kept as written"),
    pytest.param(None, CONFIGURED, "/src/profiles/arch.yaml", id="a configured path is read from its file's folder"),
    pytest.param(None, Configured("cli", Path("/src/pyproject.toml")), "cli", id="a configured bundled name is kept"),
])
def test_choose(override, configured, chosen):
    assert choose(override, configured, BUNDLED) == chosen


def test_choose_refuses_a_bare_name_that_is_not_bundled_saying_where_it_was_configured():
    with pytest.raises(UnknownProfile) as raised:
        choose(None, Configured("rest", Path("/src/pyproject.toml")), BUNDLED)
    assert str(raised.value) == "unknown profile 'rest' in /src/pyproject.toml: use one of cli, web"


def test_choose_refuses_when_no_profile_is_given_or_configured():
    with pytest.raises(NoProfile):
        choose(None, None, BUNDLED)
