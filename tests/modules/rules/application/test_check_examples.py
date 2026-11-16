"""Use case: the checks a profile writes itself held to their examples, each a small project read as the app's (or,
below tests/, as the tests'): a check must find something in its flagged code and nothing in its clean code; a
profile whose checks cannot be made comes back with their problems, and one that cannot be used with why."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import profile
from xarch.modules.rules.contract import CheckExamples, CheckRefused, ChecksCannotRun, ChecksHeld
from xarch.modules.rules.domain.values import Class, SourceFile
from xarch.profile_values.checks import APP, Quantified, Saying, Scope, WrittenCheck, WrittenTarget

PARSED = {"manager": SourceFile("", (), (), classes=(Class(1, "Manager"),)), "nothing": SourceFile("", (), ())}
DOMAIN, SERVICES = "modules/docs/domain/x.py", "modules/docs/application/x.py"


def written(flagged: str, clean: str, path: str = DOMAIN) -> dict[str, WrittenCheck]:
    return {"no-managers": WrittenCheck(("class",), Scope(APP, "domain"), Quantified("may_not", (WrittenTarget("exist"),)),
                                        (Saying("{name}", "rename it"),), flagged=((path, flagged),),
                                        clean=((path, clean),))}


@pytest.mark.parametrize("given, when, then", [
    pytest.param({"mine": written("manager", "nothing")}, CheckExamples("mine", "app"), ChecksHeld((), 1),
                 id="a check that finds something in its flagged code and nothing in its clean code has no problem"),
    pytest.param({"mine": written("nothing", "manager")}, CheckExamples("mine", "app"), ChecksHeld((
        "checks.no-managers.examples.flagged: the check finds nothing in it: make the code hold what the check is "
        "written to find, or correct the check",
        "checks.no-managers.examples.clean: the check finds 1 in it, the first app/modules/docs/domain/x.py:1: Manager: "
        "make the code clean, or correct the check"), 1),
                 id="a check that finds nothing in its flagged code or something in its clean code says so at its address"),
    pytest.param({"mine": written("manager", "nothing", SERVICES)}, CheckExamples("mine", "app"), ChecksHeld((
        "checks.no-managers.examples.flagged: the check finds nothing in it: make the code hold what the check is "
        "written to find, or correct the check",), 1),
                 id="an example outside the scope of its check finds nothing"),
    pytest.param({}, CheckExamples("broken", "app"), ChecksCannotRun(("checks.x.read: names no kind of fact",)),
                 id="a profile whose checks cannot be made comes back with their problems"),
    pytest.param({}, CheckExamples("gone", "app"), CheckRefused("no such profile"),
                 id="a profile that cannot be used is refused with why"),
])
def test_check_examples(given, when, then):
    profiles = FakeProfiles({name: profile(written=checks) for name, checks in given.items()},
                            refused={"broken": ("checks.x.read: names no kind of fact",)},
                            unusable={"gone": "no such profile"})
    tree = FakeSourceTree(Path("/src/app"), {}, parsed=PARSED)
    assert controller(tree, profiles).check_examples(when) == then
