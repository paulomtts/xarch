"""Use case: check a profile without an app: what spec's check of it finds (its example problems, its files, how it
resembles the bundled profiles), and the checks it writes itself held to their examples, each a small project read as
the app's (or, below tests/, as the tests'): a check must find something in its flagged code and nothing in its clean
code; a check that cannot be made has its problems instead, in the profile's order, while the others are held all the
same and every check is counted. A profile that does not load comes back with the loader's problems, none chosen with
the profiles known, and one that cannot be used is refused with why."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import profile
from xarch.modules.rules.contract import (
    CheckProfile,
    CheckRefused,
    ChecksHeld,
    Loosened,
    NoProfileChosen,
    ProfileHeld,
    ProfileUnloaded,
    Resemblance,
    Reviewed,
)
from xarch.modules.rules.domain.errors import NoProfile, ProfileUnusable, Unloaded
from xarch.modules.rules.domain.values import Asked, Class, SourceFile
from xarch.profile_values.checks import APP, Condition, Quantified, Saying, Scope, WrittenCheck, WrittenTarget

PARSED = {"manager": SourceFile("", (), (), classes=(Class(1, "Manager"),)), "nothing": SourceFile("", (), ())}
DOMAIN, SERVICES = "modules/docs/domain/x.py", "modules/docs/application/x.py"
APP_FOLDER = Path("/p/app")
MINE = Reviewed("mine", (), 2, Resemblance(False, "cli"))


def written(flagged: str, clean: str, path: str = DOMAIN, name: str = "no-managers") -> dict[str, WrittenCheck]:
    return {name: WrittenCheck(("class",), Scope(APP, "domain"), Quantified("may_not", (WrittenTarget("exist"),)),
                               (Saying("{name}", "rename it"),), flagged=((path, flagged),), clean=((path, clean),))}


BADLY = {"misspelt": WrittenCheck(("class",), Scope(APP, "domain"), Quantified("may_not", (WrittenTarget("exist"),)),
                                  (Saying("{name}", "rename it"),), keep=(Condition("publc"),))}
MISSPELT = "checks.misspelt.keep: no filter is named 'publc': did you mean public or placed?"
FINDS_NOTHING = ("checks.no-managers.examples.flagged: the check finds nothing in it: make the code hold what the check "
                 "is written to find, or correct the check")
FINDS_ONE = ("checks.no-managers.examples.clean: the check finds 1 in it, the first app/modules/docs/domain/x.py:1: "
             "Manager: make the code clean, or correct the check")
LOOSER = Reviewed("mine", ("example (core/rule.py): imports app.api which core may not import (parts.core.may_import)",),
                  3, Resemblance(False, "cli", (Loosened("may_import", "core", "api", "core may also import api"),)))

UNLOADED = ("mine: unknown key 'colour'", "mine: parts.core: missing `role`")


@pytest.mark.parametrize("given, when, then", [
    pytest.param((written("manager", "nothing"), MINE), CheckProfile(APP_FOLDER, "mine"),
                 ProfileHeld(MINE, ChecksHeld((), 1)),
                 id="a check that finds something in its flagged code and nothing in its clean code has no problem"),
    pytest.param((written("nothing", "manager"), MINE), CheckProfile(APP_FOLDER, "mine"),
                 ProfileHeld(MINE, ChecksHeld((FINDS_NOTHING, FINDS_ONE), 1)),
                 id="a check that finds nothing in its flagged code or something in its clean code says so at its address"),
    pytest.param((written("manager", "nothing", SERVICES), MINE), CheckProfile(APP_FOLDER, "mine"),
                 ProfileHeld(MINE, ChecksHeld((FINDS_NOTHING,), 1)),
                 id="an example outside the scope of its check finds nothing"),
    pytest.param(({**BADLY, **written("manager", "nothing")}, MINE), CheckProfile(APP_FOLDER, "mine"),
                 ProfileHeld(MINE, ChecksHeld((MISSPELT,), 2)),
                 id="a check that cannot be made has its problems, and every check is counted"),
    pytest.param(({**BADLY, **written("nothing", "nothing")}, MINE), CheckProfile(APP_FOLDER, "mine"),
                 ProfileHeld(MINE, ChecksHeld((MISSPELT, FINDS_NOTHING), 2)),
                 id="a check that cannot be made does not stop the others being held to their examples"),
    pytest.param(({**written("nothing", "nothing"), **BADLY}, MINE), CheckProfile(APP_FOLDER, "mine"),
                 ProfileHeld(MINE, ChecksHeld((FINDS_NOTHING, MISSPELT), 2)),
                 id="each check's problems are at its place in the profile's order"),
    pytest.param((written("nothing", "nothing"), LOOSER), CheckProfile(APP_FOLDER, "mine"),
                 ProfileHeld(LOOSER, ChecksHeld((FINDS_NOTHING,), 1)),
                 id="what spec's check finds and what the checks the profile writes itself find are one result"),
    pytest.param(({}, MINE), CheckProfile(APP_FOLDER, "mine"),
                 ProfileHeld(MINE, ChecksHeld((), 0)),
                 id="a profile that writes no check of its own holds none"),
    pytest.param(({}, Unloaded("mine", UNLOADED)), CheckProfile(APP_FOLDER, "mine"), ProfileUnloaded("mine", UNLOADED),
                 id="a profile that does not load comes back with every problem the loader found"),
    pytest.param(({}, NoProfile(("cli", "web"))), CheckProfile(APP_FOLDER, None),
                 NoProfileChosen(("cli", "web")),
                 id="with no profile named and none configured nothing is chosen, and the profiles known are said"),
    pytest.param(({}, ProfileUnusable("no such profile")), CheckProfile(APP_FOLDER, "mine"),
                 CheckRefused("no such profile"),
                 id="a profile that cannot be used is refused with why"),
])
def test_check_profile(given, when, then):
    checks, reviewed = given
    profiles = FakeProfiles({"mine": profile(written=checks)}, reviewed={when.target: reviewed})
    tree = FakeSourceTree(Path("/src/app"), {}, parsed=PARSED)
    assert controller(tree, profiles).check_profile(when) == then


def asked(flagged: str, clean: str, keep: tuple[Condition, ...] = ()) -> dict[str, Asked]:
    return {"rule": Asked("class", Scope(APP, "domain"), keep, ((DOMAIN, flagged), (SERVICES, flagged)),
                          ((DOMAIN, clean),))}


@pytest.mark.parametrize("evals, problems", [
    pytest.param(asked("manager", "manager"), ("evals.rule.examples.flagged.modules/docs/application/x.py: holds no "
                                               "class the eval reads (in its scope, passing keep): give it one",),
                 id="an example file in which the eval reads nothing is refused at its address"),
    pytest.param(asked("manager", "nothing"), (
        "evals.rule.examples.flagged.modules/docs/application/x.py: holds no class the eval reads (in its scope, "
        "passing keep): give it one",
        "evals.rule.examples.clean.modules/docs/domain/x.py: holds no class the eval reads (in its scope, passing "
        "keep): give it one"), id="a clean example must hold something the eval reads too"),
    pytest.param(asked("manager", "manager", (Condition("publc"),)),
                 ("evals.rule.keep: no filter is named 'publc': did you mean public or placed?",),
                 id="an eval whose filter is no word of the vocabulary is refused at its address, as a check is"),
])
def test_the_evals_a_profile_writes_itself_are_held_to_their_examples_statically(evals, problems):
    profiles = FakeProfiles({"mine": profile(asked=evals)}, reviewed={"mine": MINE})
    tree = FakeSourceTree(Path("/src/app"), {}, parsed=PARSED)
    assert controller(tree, profiles).check_profile(CheckProfile(APP_FOLDER, "mine")) == ProfileHeld(
        MINE, ChecksHeld((), 0, problems, 1))
