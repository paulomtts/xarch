"""Use case: read the pieces of a source text that is in no file (its functions, classes and their methods), with the
reader of the app's language, on an in-memory reader."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from xarch.kernel.source import Unparsable
from xarch.modules.rules.application.controller import ReaderController
from xarch.modules.rules.application.services.source_reading import SourceReadService
from xarch.modules.rules.contract import Piece
from xarch.modules.rules.domain.values import SourceFile

PIECES = (Piece("class", "Shelf", 1, 9), Piece("method", "count", 3, 9, "Shelf"))
READS = {"a class": SourceFile("", (), (), pieces=PIECES),
         "broken": SourceFile("", (), (), error=Unparsable(3, "invalid syntax"))}


@pytest.mark.parametrize("given, when, then", [
    pytest.param(READS, "a class", PIECES, id="the pieces of a text come back in order"),
    pytest.param(READS, "broken", Unparsable(3, "invalid syntax"),
                 id="a text that does not parse comes back as where and why"),
])
def test_read_pieces(given, when, then):
    tree = FakeSourceTree(Path("/src/app"), {}, parsed=given)
    assert ReaderController(SourceReadService(tree)).pieces(when) == then
