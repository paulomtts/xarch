"""How each way a profile is looser than its bundled baseline is said in the enforcement section."""
import pytest

from xarch.modules.rules.domain.values import Loosened


@pytest.mark.parametrize("loosened, sentence", [
    pytest.param(Loosened("may_import", "domain", "platform"),
                 "domain may also import platform (parts.domain.may_import)", id="a rule target added"),
    pytest.param(Loosened("libraries", "", ""), "outside packages are not checked", id="libraries switched off"),
    pytest.param(Loosened("libraries", "web", "requests"), "web may also import requests (parts.web.libraries)",
                 id="a package added"),
    pytest.param(Loosened("libraries", "web", "*"), "web may import any outside package (parts.web.libraries)",
                 id="a part left unchecked"),
    pytest.param(Loosened("forbidden", "domain", "time.time"),
                 "domain no longer forbids time.time (parts.domain.forbidden)", id="a forbidden name dropped"),
    pytest.param(Loosened("untested", "platform"), "platform is newly marked untested (parts.platform.untested)",
                 id="a part marked untested"),
    pytest.param(Loosened("types_only", "rendering", "controller"),
                 "the rendering tests may now call controller (tiers.rendering.types_only)",
                 id="a types-only part dropped"),
    pytest.param(Loosened("apply_forbidden", "unit"),
                 "the unit tests are no longer held to their part's forbidden list (tiers.unit.apply_forbidden)",
                 id="a tier's forbidden dropped"),
    pytest.param(Loosened("testing.skips", "", "pytest.skip"),
                 "pytest.skip is no longer counted as a skip (testing.skips)", id="a skip dropped"),
    pytest.param(Loosened("files.pinned", "", "tests/test_rules.py"),
                 "tests/test_rules.py is no longer pinned (files.tests/test_rules.py.pinned)",
                 id="an init file unpinned"),
    pytest.param(Loosened("other", "", "x"), "other x", id="a key it does not know is said by its words"),
])
def test_sentence(loosened, sentence):
    assert loosened.sentence == sentence
