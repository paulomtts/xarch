"""Review's Code read from rules' contract: the files rules reads at the paths, each as it was read with its pieces, in
order; a refusal of rules raises Refused with its reason."""
from pathlib import Path

import pytest

from xarch.kernel.source import CommentSpan, Import, Unparsable
from xarch.modules.review.adapters.rules_code import RulesCode
from xarch.modules.review.domain import published as review
from xarch.modules.review.domain.errors import Refused
from xarch.modules.review.domain.published import LeftOut
from xarch.modules.review.domain.values import CodeFile, Found, Read, Reads, Span
from xarch.modules.rules.contract import (
    EXCLUDED,
    IN_NO_PART,
    IN_PART,
    IN_PROJECT,
    IN_TESTS,
    LINKED_OUT,
    NOT_SOURCE,
    NOT_THERE,
    AskHolds,
    CheckRefused,
    ChecksCannotRun,
    FactKept,
    FactsKept,
    FileKept,
    HoldsAsked,
    HoldsOf,
    HoldsResult,
    KeepFacts,
    KeptResult,
    Outside,
    Piece,
    ReadSources,
    SourceRead,
    SourcesRead,
    SourcesResult,
)

IDS = Import(1, ("app", "kernel", "ids"), ("Id",), written="app.kernel.ids")
PIECES = (Piece("class", "Id", 1, 4), Piece("method", "new", 2, 4, "Id"))
READ = SourcesRead((SourceRead("app/kernel/ids.py", IN_PART, "kernel", "class Id: ...\n", (IDS,), Unparsable(3, "bad"),
                               PIECES),
                    SourceRead("README.md", NOT_SOURCE), SourceRead("app/gone.py", NOT_THERE),
                    SourceRead("tests/test_a.py", IN_TESTS), SourceRead("scripts/run.py", IN_PROJECT),
                    SourceRead("app/examples/a.py", EXCLUDED), SourceRead("app/stray.py", IN_NO_PART),
                    SourceRead("app/kernel/out.py", LINKED_OUT),
                    SourceRead("app/kernel/alias.py", IN_PART, "kernel", "x = 1\n", target="app/kernel/ids.py")))


class Rules:
    """Rules' controller as review's adapter uses it, answering from a fixed result and keeping what it was asked."""

    def __init__(self, result: SourcesResult, kept: KeptResult = FactsKept(()), held: HoldsResult = HoldsAsked(())):
        self._result, self._kept, self._held, self.asked = result, kept, held, []

    def sources(self, cmd: ReadSources) -> SourcesResult:
        self.asked.append(cmd)
        return self._result

    def kept(self, cmd: KeepFacts) -> KeptResult:
        self.asked.append(cmd)
        return self._kept

    def holds(self, cmd: AskHolds) -> HoldsResult:
        self.asked.append(cmd)
        return self._held


def test_a_file_in_a_part_is_handed_on_as_it_was_read_and_any_other_left_out_with_why_in_review_s_words():
    rules = Rules(READ)
    files = RulesCode(rules).files((Path("app/kernel"),), Path("/src"), Path("/src/app"), "p", None)
    assert files == Found((CodeFile("app/kernel/ids.py", "kernel", "class Id: ...\n", (IDS,), Unparsable(3, "bad"),
                                    (Span("class", "Id", "", (1, 4)), Span("method", "new", "Id", (2, 4)))),
                           CodeFile("app/kernel/alias.py", "kernel", "x = 1\n", target="app/kernel/ids.py")),
                          (LeftOut("README.md", review.NOT_SOURCE), LeftOut("app/gone.py", review.MISSING),
                           LeftOut("tests/test_a.py", review.A_TEST), LeftOut("scripts/run.py", review.OUTSIDE),
                           LeftOut("app/examples/a.py", review.EXCLUDED), LeftOut("app/stray.py", review.UNPLACED),
                           LeftOut("app/kernel/out.py", review.LINK)))
    assert rules.asked == [ReadSources((Path("app/kernel"),), Path("/src"), Path("/src/app"), "p", None)]


@pytest.mark.parametrize("result, reason", [
    pytest.param(Outside("/x lies outside the project"), "/x lies outside the project", id="a path outside the project"),
    pytest.param(CheckRefused("gone: no such file"), "gone: no such file", id="a profile that cannot be used"),
    pytest.param(ChecksCannotRun(("checks.a: one", "checks.b: two")), "checks.a: one; checks.b: two",
                 id="a profile whose own checks cannot run, with every problem"),
])
def test_a_refusal_of_rules_is_refused_with_its_reason(result, reason):
    with pytest.raises(Refused, match=reason):
        RulesCode(Rules(result)).files((Path("x"),), Path("/src"), Path("/src/app"), "p", None)


def test_what_an_eval_reads_is_handed_on_file_by_file_with_each_thing_s_lines_and_name():
    kept = FactsKept((FileKept("kernel/ids.py", (IDS,), (FactKept(2, 4, "Id.new"),)), FileKept("kernel/x.py", (), ())))
    rules = Rules(READ, kept)
    files = (("kernel/ids.py", "class Id: ...\n"), ("kernel/x.py", "x = 1\n"))
    assert RulesCode(rules).reads("p", "app", "rule", files) == (
        Reads(CodeFile("kernel/ids.py", "", "class Id: ...\n", (IDS,)), (Read((2, 4), "Id.new"),)),
        Reads(CodeFile("kernel/x.py", "", "x = 1\n"), ()))
    assert rules.asked == [KeepFacts("p", "app", "rule", files)]


@pytest.mark.parametrize("result, reason", [
    pytest.param(CheckRefused("gone: no such file"), "gone: no such file", id="a profile that cannot be used"),
    pytest.param(ChecksCannotRun(("evals.rule.keep: one", "evals.rule.in: two")), "evals.rule.keep: one; evals.rule.in: two",
                 id="an eval that cannot be read, with every problem"),
])
def test_a_refusal_of_rules_to_say_what_an_eval_reads_is_refused_with_its_reason(result, reason):
    with pytest.raises(Refused, match=reason):
        RulesCode(Rules(READ, result)).reads("p", "app", "rule", ())


def test_where_the_comments_of_a_file_and_of_a_file_an_eval_reads_lie_is_handed_on_as_rules_found_it():
    comments = (CommentSpan(1, 14, 20), CommentSpan(2, 4, 9))
    read = SourcesRead((SourceRead("app/kernel/ids.py", IN_PART, "kernel", "class Id: ...\n", comments=comments),))
    kept = FactsKept((FileKept("kernel/ids.py", (), (FactKept(0, 0, ""),), comments),))
    code = RulesCode(Rules(read, kept))
    assert code.files((Path("app/kernel"),), Path("/src"), Path("/src/app"), "p", None).read[0].comments == comments
    assert code.reads("p", "app", "rule", (("kernel/ids.py", "class Id: ...\n"),))[0].file.comments == comments


def test_the_parts_whose_holds_each_file_would_break_are_handed_on_in_the_order_given():
    rules = Rules(READ, held=HoldsAsked((HoldsOf("kernel/ids.py", ("logic",)), HoldsOf("kernel/x.py"))))
    files = (("kernel/ids.py", "class Id: ...\n"), ("kernel/x.py", "x = 1\n"))
    assert RulesCode(rules).breaks("p", "app", files, Path("/src/app")) == (("logic",), ())
    assert rules.asked == [AskHolds("p", "app", files, Path("/src/app"))]


@pytest.mark.parametrize("result, reason", [
    pytest.param(CheckRefused("gone: no such file"), "gone: no such file", id="a profile that cannot be used"),
    pytest.param(ChecksCannotRun(("checks.a: one", "checks.b: two")), "checks.a: one; checks.b: two",
                 id="a profile whose own checks cannot run, with every problem"),
])
def test_a_refusal_of_rules_to_say_where_else_files_could_lie_is_refused_with_its_reason(result, reason):
    with pytest.raises(Refused, match=reason):
        RulesCode(Rules(READ, held=result)).breaks("p", "app", ())
