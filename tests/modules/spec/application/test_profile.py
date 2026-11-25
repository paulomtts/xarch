"""Use case: a profile as the checks read it, which the rules module checks code against."""
import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.modules.spec.application.helpers import controller
from tests.modules.spec.languages import PYTHON
from xarch.modules.spec.contract import GuardsView, PartView, ProfileRefused, ProfileView

LAYERED = {"name": "layered", "parts": {"src/": {"role": "code"}}}
SPEC = controller(FakeArchitectureFiles({"cli": LAYERED, "broken": {"name": "broken"}}))


@pytest.mark.parametrize("given, when, then", [
    pytest.param(SPEC, "cli", ProfileView((PartView("src", ("src",), (), "code", shown="src/"),), ((), ("src",)),
                                          imports_libraries={"src": ()}, language=PYTHON.checked),
                 id="a profile that loads is given as the checks read it"),
    pytest.param(SPEC, "broken", ProfileRefused("broken: missing `parts`"),
                 id="a profile that does not load is refused with why"),
])
def test_profile(given, when, then):
    assert given.profile(when) == then


def test_the_public_names_a_profile_accepts_as_only_the_tests_reach_the_checks_as_written():
    dead = {**LAYERED, "fakes": {"folder": "fakes", "for": ["src"]},
            "guards": {"dead-code": {"tests_only": True, "known": ["src/wiring.py:build", "src/rules.py:Rule"]}}}
    view = controller(FakeArchitectureFiles({"dead": dead})).profile("dead")
    assert isinstance(view, ProfileView)
    assert view.guards == GuardsView(dead_code=True, tests_only=True,
                                     tests_only_known=("src/wiring.py:build", "src/rules.py:Rule"))


def test_the_parts_the_guard_no_callbacks_lists_reach_the_checks_and_no_part_carries_the_key():
    listed = {**LAYERED, "guards": {"no-callbacks": {"parts": ["src"]}}}
    view = controller(FakeArchitectureFiles({"listed": listed})).profile("listed")
    assert isinstance(view, ProfileView)
    assert view.guards == GuardsView(no_callbacks=("src",))
    assert not hasattr(view.parts[0], "no_callbacks")
