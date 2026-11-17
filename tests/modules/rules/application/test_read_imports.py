"""Use case: read what a source text that is in no file imports, and where its comments lie, with the reader of the
app's language, on an in-memory reader."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from xarch.kernel.source import CommentSpan, Import, Unparsable
from xarch.modules.rules.application.controller import ReaderController
from xarch.modules.rules.application.services.source_reading import SourceReadService
from xarch.modules.rules.domain.parsed import Comment, SourceFile

IMPORTS = [Import(1, ("app", "kernel"), ("ids",)), Import(2, ("x",), ("y",), relative=True, up=1)]
READS = {"two imports": IMPORTS, "broken": SourceFile("", (), (), error=Unparsable(3, "invalid syntax"))}


@pytest.mark.parametrize("given, when, then", [
    pytest.param(READS, "two imports", tuple(IMPORTS), id="the imports of a text come back in order"),
    pytest.param(READS, "broken", Unparsable(3, "invalid syntax"),
                 id="a text that does not parse comes back as where and why"),
])
def test_read_imports(given, when, then):
    tree = FakeSourceTree(Path("/src/app"), {}, parsed=given)
    assert ReaderController(SourceReadService(tree)).imports(when) == then


def test_where_the_comments_of_a_text_lie_come_back_in_order_or_where_and_why_it_does_not_parse():
    noted = SourceFile("", (), (), comments=(Comment(1, "# why", 7, 12), Comment(3, "# how", 4, 9)))
    tree = FakeSourceTree(Path("/src/app"), {}, parsed={"noted": noted, **READS})
    reader = ReaderController(SourceReadService(tree))
    assert reader.comments("noted") == (CommentSpan(1, 7, 12), CommentSpan(3, 4, 9))
    assert reader.comments("broken") == Unparsable(3, "invalid syntax")
