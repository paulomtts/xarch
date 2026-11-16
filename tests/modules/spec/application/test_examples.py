"""Use case: the files placement is held to: every file of the docs' example projects lying in a part (the clean
ones), then those `evals.placement.examples` writes, each with the part its path lies in, its code and its imports as
the reader reads them; a profile that does not load is refused with why."""
import pytest

from tests.modules.spec.application.builders import BASE, spec_controller
from xarch.kernel.source import Import, Unparsable
from xarch.modules.spec.contract import ExampleFile, ExamplesRead, ProfileRefused

RULE = Import(1, ("app", "core", "rules"), ("rule",))
MINE = {**BASE, "name": "mine", "docs": {**BASE["docs"], "examples": ["ex"]},
        "evals": {"placement": {"examples": {"flagged": {"core/handler.py": "def handle(request): ...\n"},
                                             "clean": {"api/route.py": "from app.core.rules import rule\n"}}}}}
FILES = {"ex/core/rules.py": "def rule(): ...\n", "ex/tests/test_rules.py": "def test_rule(): ...\n",
         "ex/stray/x.py": "x = (\n"}


@pytest.mark.parametrize("given, when, then", [
    pytest.param(dict(files={"mine.yaml": MINE}, texts=FILES,
                      reads={"from app.core.rules import rule\n": (RULE,), "x = (\n": Unparsable(1, "bad")}),
                 "mine.yaml", ExamplesRead(
                     (ExampleFile("core/rules.py", "core", "def rule(): ...\n"),
                      ExampleFile("api/route.py", "api", "from app.core.rules import rule\n", (RULE,))),
                     (ExampleFile("core/handler.py", "core", "def handle(request): ...\n"),)),
                 id="the docs' examples in a part, then placement's own, each with its part, code and imports"),
    pytest.param(dict(files={"broken.yaml": {"xarch": 2, "name": "broken"}}), "broken.yaml",
                 ProfileRefused("broken.yaml: missing `parts`"), id="a profile that does not load is refused with why"),
])
def test_examples(given, when, then):
    spec, _ = spec_controller(**given)
    assert spec.examples(when) == then
