"""Use case: find, for each file given as text, the parts whose `holds` it would break were it to lie there, by the rule
`check` runs in each: read as a small project of the files given, or with the other files of the app read from its
folder too, so that a class reads as an exception through a class of another file as `check` reads it; a profile whose
own checks cannot run, or that cannot be used, is refused."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import imp, profile
from xarch.modules.rules.contract import AskHolds, CheckRefused, ChecksCannotRun, HoldsAsked, HoldsOf
from xarch.modules.rules.domain.errors import ProfileUnusable
from xarch.modules.rules.domain.parsed import Class, Function, Method, SourceFile

ROOT = Path("/src/app")
BASE = imp(1, "app.kernel.errors", "DomainError")
PARSED = {
    "functions": SourceFile("", (), (), functions=(Function(1, "validate"), Function(4, "_helper"))),
    "classes": SourceFile("", (), (), classes=(Class(1, "Document", methods=(Method(2, "title", None),)),)),
    "errors": SourceFile("", (), (BASE,), classes=(Class(3, "NoDocument", (("app", "kernel", "errors", "DomainError"),)),)),
    "record": SourceFile("", (), (), classes=(Class(1, "Found"),),
                         functions=(Function(3, "found", returns_named=frozenset({"Found"})),)),
}
APP = {"kernel/errors.py": SourceFile("", (), (), classes=(Class(1, "DomainError", exception=True),)),
       "modules/docs/domain/document.py": SourceFile("", (), (), classes=(Class(1, "Document"),))}
DOMAIN, LOGIC, INIT = "modules/docs/domain/x.py", "modules/docs/application/logic/x.py", "modules/docs/domain/__init__.py"
HOLDS = {"domain": "classes", "logic": "functions"}


def holds(command: AskHolds):
    profiles = FakeProfiles({"mine": profile(holds=HOLDS)}, refused={"broken": ("checks.mine.read: names no kind",)},
                            unusable={"gone": str(ProfileUnusable("gone: cannot read the file"))})
    return controller(FakeSourceTree(ROOT, APP, parsed=PARSED), profiles).holds(command)


@pytest.mark.parametrize("given, when, then", [
    pytest.param(HOLDS, AskHolds("mine", "app", ((LOGIC, "functions"), (DOMAIN, "classes"))),
                 HoldsAsked((HoldsOf(LOGIC, ("domain",)), HoldsOf(DOMAIN, ("logic",)))),
                 id="a file of public functions breaks a part of classes, a file of classes one of functions, each "
                    "wherever it lies"),
    pytest.param(HOLDS, AskHolds("mine", "app", ((DOMAIN, "functions"),)), HoldsAsked((HoldsOf(DOMAIN, ("domain",)),)),
                 id="a file that breaks the holds of its own part says so too"),
    pytest.param(HOLDS, AskHolds("mine", "app", ((LOGIC, "record"),)), HoldsAsked((HoldsOf(LOGIC, ("domain",)),)),
                 id="a record a function of the file returns breaks no part of functions"),
    pytest.param(HOLDS, AskHolds("mine", "app", ((INIT, "functions"),)), HoldsAsked((HoldsOf(INIT),)),
                 id="a package file breaks no part's holds"),
    pytest.param(HOLDS, AskHolds("mine", "app", ((DOMAIN, "errors"),)), HoldsAsked((HoldsOf(DOMAIN, ("logic",)),)),
                 id="alone, a class whose base is a class of a file not given is no exception"),
    pytest.param(HOLDS, AskHolds("mine", "app", ((DOMAIN, "errors"),), ROOT), HoldsAsked((HoldsOf(DOMAIN),)),
                 id="with the app's folder, a class that derives from an exception of another file of it is one, and "
                    "breaks no part of functions"),
    pytest.param(HOLDS, AskHolds("broken", "app", ((DOMAIN, "errors"),)),
                 ChecksCannotRun(("checks.mine.read: names no kind",)),
                 id="a profile whose own checks cannot run is refused with every problem"),
    pytest.param(HOLDS, AskHolds("gone", "app", ()), CheckRefused("gone: cannot read the file"),
                 id="a profile that cannot be used is refused with why"),
])
def test_holds(given, when, then):
    assert holds(when) == then


def test_a_file_given_stands_in_place_of_the_file_of_the_app_at_its_path():
    found = holds(AskHolds("mine", "app", (("modules/docs/domain/document.py", "functions"),), ROOT))
    assert found == HoldsAsked((HoldsOf("modules/docs/domain/document.py", ("domain",)),))
