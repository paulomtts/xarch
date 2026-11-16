"""Use case: find what an eval of the profile's own reads in files given as text, each a small project read as the
app's: each fact of the kind it reads, in its scope, passing the filters it keeps, with its first line and its name;
an eval the profile does not write, or one whose filters are no words of the vocabulary, is refused with every
problem, and so is a profile that cannot be used."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import profile
from xarch.modules.rules.contract import CheckRefused, ChecksCannotRun, FactKept, FactsKept, KeepFacts
from xarch.modules.rules.domain.errors import ProfileUnusable
from xarch.modules.rules.domain.values import Asked, Class, Function, SourceFile
from xarch.profile_values.checks import APP, Condition, Scope

PARSED = {"service": SourceFile("", (), (), functions=(Function(3, "__init__", owner="Publishing"),
                                                      Function(6, "publish", owner="Publishing"),
                                                      Function(12, "helper")),
                                classes=(Class(1, "Publishing"),))}
DOMAIN, SERVICES = "modules/docs/domain/x.py", "modules/docs/application/x.py"
FUNCTIONS = Asked("function", Scope(APP, "domain"), (Condition("public"),))
FILES = Asked("file", Scope(APP, "domain"))


def kept(asked: dict[str, Asked], command: KeepFacts, refused: ProfileUnusable | None = None):
    profiles = FakeProfiles({"mine": profile(asked=asked)}, unusable={"gone": str(refused)} if refused else None)
    return controller(FakeSourceTree(Path("/src/app"), {}, parsed=PARSED), profiles).kept(command)


@pytest.mark.parametrize("given, when, then", [
    pytest.param({"rule": FUNCTIONS}, KeepFacts("mine", "app", "rule", ((DOMAIN, "service"),)),
                 FactsKept((FactKept(DOMAIN, 6, "Publishing.publish"), FactKept(DOMAIN, 12, "helper"))),
                 id="each function in its scope that passes keep, a method by its class and its name"),
    pytest.param({"rule": FUNCTIONS}, KeepFacts("mine", "app", "rule", ((SERVICES, "service"),)), FactsKept(()),
                 id="a file outside the scope holds nothing the eval reads"),
    pytest.param({"rule": FILES}, KeepFacts("mine", "app", "rule", ((DOMAIN, "service"), (SERVICES, "service"))),
                 FactsKept((FactKept(DOMAIN, 0, ""),)), id="an eval that reads files reads each file of its scope whole"),
    pytest.param({}, KeepFacts("mine", "app", "rule", ((DOMAIN, "service"),)),
                 ChecksCannotRun(("evals.rule: the profile writes no eval of its own of this id",)),
                 id="an eval the profile does not write is refused"),
    pytest.param({"rule": Asked("function", Scope(APP, "domain"), (Condition("publc"),))},
                 KeepFacts("mine", "app", "rule", ((DOMAIN, "service"),)),
                 ChecksCannotRun(("evals.rule.keep: no filter is named 'publc': did you mean public or placed?",)),
                 id="an eval whose filter is no word of the vocabulary is refused at its address"),
    pytest.param({}, KeepFacts("gone", "app", "rule", ()), CheckRefused("gone: cannot read the file"),
                 id="a profile that cannot be used is refused with why"),
])
def test_kept(given, when, then):
    assert kept(given, when, ProfileUnusable("gone: cannot read the file")) == then
