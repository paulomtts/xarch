"""Use case: the files placement is held to: every file of the docs' example projects lying in a part (the clean
ones), then those `evals.placement.examples` writes, each with the part its path lies in, its code and its imports as
the reader reads them, and where its comments lie as the reader finds them; a profile that does not load is refused
with why."""
import pytest

from tests.modules.spec.application.builders import BASE, spec_controller
from xarch.kernel.source import CommentSpan, Import, Unparsable
from xarch.modules.spec.contract import ExampleFile, ExamplesRead, ProfileRefused

RULE = Import(1, ("app", "core", "rules"), ("rule",))
MINE = {**BASE, "name": "mine", "docs": {**BASE["docs"], "examples": ["ex"]},
        "evals": {"placement": {"examples": {"flagged": {"core/handler.py": "def handle(request): ...\n"},
                                             "clean": {"api/route.py": "from app.core.rules import rule\n"}}}}}
FILES = {"ex/core/rules.py": "def rule(): ...\n", "ex/tests/test_rules.py": "def test_rule(): ...\n",
         "ex/stray/x.py": "x = (\n"}


@pytest.mark.parametrize("given, when, then", [
    pytest.param(dict(files={"mine.yaml": MINE}, texts=FILES,
                      reads={"from app.core.rules import rule\n": (RULE,), "def handle(request): ...\n": Unparsable(1, "bad")}),
                 "mine.yaml", ExamplesRead(
                     (ExampleFile("core/rules.py", "core", "def rule(): ...\n"),
                      ExampleFile("api/route.py", "api", "from app.core.rules import rule\n", (RULE,))),
                     (ExampleFile("core/handler.py", "core", "def handle(request): ...\n"),)),
                 id="the docs' examples in a part, then placement's own, each with its part, code and imports"),
    pytest.param(dict(files={"broken.yaml": {"name": "broken"}}), "broken.yaml",
                 ProfileRefused("broken.yaml: missing `parts`"), id="a profile that does not load is refused with why"),
])
def test_examples(given, when, then):
    spec, _ = spec_controller(**given)
    assert spec.examples(when) == then


def test_each_example_comes_with_where_its_comments_lie_and_one_that_does_not_parse_with_none():
    spec, _ = spec_controller(files={"mine.yaml": MINE}, texts=FILES,
                              comments={"def rule(): ...\n": (CommentSpan(1, 16, 21),), "def handle(request): ...\n": Unparsable(1, "bad")})
    found = spec.examples("mine.yaml")
    assert isinstance(found, ExamplesRead)
    assert [(item.path, item.comments) for item in found.clean + found.flagged] == [
        ("core/rules.py", (CommentSpan(1, 16, 21),)), ("api/route.py", ()), ("core/handler.py", ())]
