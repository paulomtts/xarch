"""How each way a profile is looser than its bundled baseline is said in the enforcement section."""
import pytest

from xarch.modules.rules.domain.values import Loosened


@pytest.mark.parametrize("loosened, sentence", [
    pytest.param(Loosened("rules", "domain", "platform"), "domain may also import platform", id="a rule target added"),
    pytest.param(Loosened("libraries", "", ""), "outside packages are not checked", id="libraries switched off"),
    pytest.param(Loosened("libraries", "web", "requests"), "web may also import requests", id="a package added"),
    pytest.param(Loosened("forbidden", "domain", "time.time"), "domain no longer forbids time.time",
                 id="a forbidden name dropped"),
    pytest.param(Loosened("untested", "platform"), "platform is newly marked untested", id="a part marked untested"),
    pytest.param(Loosened("types_only", "rendering", "controller"), "the rendering tests may now call controller",
                 id="a types-only part dropped"),
    pytest.param(Loosened("tier_forbidden", "unit"),
                 "the unit tests are no longer held to their part's forbidden list", id="a tier's forbidden dropped"),
    pytest.param(Loosened("skips", "", "pytest.skip"), "pytest.skip is no longer counted as a skip", id="a skip dropped"),
    pytest.param(Loosened("pinned", "", "tests/test_rules.py"), "tests/test_rules.py is no longer pinned",
                 id="an init file unpinned"),
    pytest.param(Loosened("other", "", "x"), "other x", id="a key it does not know is said by its words"),
])
def test_sentence(loosened, sentence):
    assert loosened.sentence == sentence
