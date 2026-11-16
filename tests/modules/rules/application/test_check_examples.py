"""Use case: the checks a profile writes itself held to their examples, each a small project read as the app's (or,
below tests/, as the tests'): a check must find something in its flagged code and nothing in its clean code; a
profile whose checks cannot be made comes back with their problems."""
from pathlib import Path

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import profile
from xarch.modules.rules.contract import CheckExamples, ChecksCannotRun, ChecksHeld
from xarch.modules.rules.domain.values import Class, SourceFile
from xarch.profile_values.checks import APP, Quantified, Saying, Scope, WrittenCheck, WrittenTarget

PARSED = {"manager": SourceFile("", (), (), classes=(Class(1, "Manager"),)), "nothing": SourceFile("", (), ())}


def held(flagged: str, clean: str, path: str = "modules/docs/domain/x.py") -> ChecksHeld:
    own = WrittenCheck(("class",), Scope(APP, "domain"), Quantified("may_not", (WrittenTarget("exist"),)),
                       (Saying("{name}", "rename it"),), flagged=((path, flagged),), clean=((path, clean),))
    profiles = FakeProfiles({"mine": profile(written={"no-managers": own})}, refused={"broken": ("checks.x.read: no kind",)})
    tree = FakeSourceTree(Path("/src/app"), {}, parsed=PARSED)
    return controller(tree, profiles).check_examples(CheckExamples("mine", "app"))


def test_a_check_that_finds_something_in_its_flagged_code_and_nothing_in_its_clean_code_has_no_problem():
    assert held("manager", "nothing") == ChecksHeld((), 1)


def test_a_check_that_finds_nothing_in_its_flagged_code_or_something_in_its_clean_code_says_so_at_its_address():
    assert held("nothing", "manager") == ChecksHeld((
        "checks.no-managers.examples.flagged: the check finds nothing in it: make the code hold what the check is "
        "written to find, or correct the check",
        "checks.no-managers.examples.clean: the check finds 1 in it, the first app/modules/docs/domain/x.py:1: Manager: "
        "make the code clean, or correct the check"), 1)


def test_an_example_outside_the_scope_of_its_check_finds_nothing():
    assert held("manager", "nothing", "modules/docs/application/x.py").problems[0].startswith(
        "checks.no-managers.examples.flagged: the check finds nothing in it")


def test_a_profile_whose_checks_cannot_be_made_has_their_problems():
    profiles = FakeProfiles({}, refused={"broken": ("checks.x.read: names no kind of fact",)})
    found = controller(FakeSourceTree(Path("/src/app"), {}), profiles).check_examples(CheckExamples("broken", "app"))
    assert found == ChecksCannotRun(("checks.x.read: names no kind of fact",))
