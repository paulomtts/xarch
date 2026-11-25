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
from xarch.kernel.source import CommentSpan, Import
from xarch.modules.rules.contract import CheckRefused, ChecksCannotRun, FactKept, FactsKept, FileKept, KeepFacts, Piece
from xarch.modules.rules.domain.errors import ProfileUnusable
from xarch.modules.rules.domain.parsed import Class, Comment, Function, SourceFile
from xarch.modules.rules.domain.profile import Asked
from xarch.profile_values.checks import APP, Condition, Scope

CLOCK = Import(1, ("app", "kernel", "time"), ("Clock",))
PARSED = {"service": SourceFile("", (), (CLOCK,), functions=(Function(3, "__init__", owner="Publishing", public=False),
                                                            Function(6, "publish", owner="Publishing"),
                                                            Function(12, "helper")),
                                classes=(Class(2, "Publishing"),),
                                pieces=(Piece("class", "Publishing", 2, 10), Piece("method", "publish", 5, 10, "Publishing"))),
          "bare": SourceFile("", (), (), functions=(Function(1, "run"),))}
DOMAIN, SERVICES = "modules/docs/domain/x.py", "modules/docs/application/x.py"
FUNCTIONS = Asked("function", Scope(APP, "domain"), (Condition("public"),))
FILES = Asked("file", Scope(APP, "domain"))


def kept(asked: dict[str, Asked], command: KeepFacts, refused: ProfileUnusable | None = None):
    profiles = FakeProfiles({"mine": profile(asked=asked)}, unusable={"gone": str(refused)} if refused else None)
    return controller(FakeSourceTree(Path("/src/app"), {}, parsed=PARSED), profiles).kept(command)


@pytest.mark.parametrize("given, when, then", [
    pytest.param({"rule": FUNCTIONS}, KeepFacts("mine", "app", "rule", ((DOMAIN, "service"),)),
                 FactsKept((FileKept(DOMAIN, (CLOCK,), (FactKept(5, 10, "Publishing.publish"),
                                                        FactKept(12, 12, "helper"))),)),
                 id="each function in its scope that passes keep, a method by its class and its name, with the lines "
                    "of its piece, or its own line where the reader cuts none, and the file's imports"),
    pytest.param({"rule": FUNCTIONS}, KeepFacts("mine", "app", "rule", ((SERVICES, "service"),)),
                 FactsKept((FileKept(SERVICES, (CLOCK,), ()),)),
                 id="a file outside the scope holds nothing the eval reads"),
    pytest.param({"rule": FILES}, KeepFacts("mine", "app", "rule", ((DOMAIN, "bare"), (SERVICES, "service"))),
                 FactsKept((FileKept(DOMAIN, (), (FactKept(0, 0, ""),)), FileKept(SERVICES, (CLOCK,), ()))),
                 id="an eval that reads files reads each file of its scope whole"),
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


def test_each_file_given_comes_back_with_where_its_comments_lie_as_its_reader_finds_them():
    parsed = {"noted": SourceFile("", (), (), comments=(Comment(1, "# why", 7, 12), Comment(2, "# how", 0, 5)),
                                  functions=(Function(3, "run"),))}
    profiles = FakeProfiles({"mine": profile(asked={"rule": FILES})})
    found = controller(FakeSourceTree(Path("/src/app"), {}, parsed=parsed), profiles).kept(
        KeepFacts("mine", "app", "rule", ((DOMAIN, "noted"),)))
    assert found == FactsKept((FileKept(DOMAIN, (), (FactKept(0, 0, ""),), (CommentSpan(1, 7, 12), CommentSpan(2, 0, 5))),))
