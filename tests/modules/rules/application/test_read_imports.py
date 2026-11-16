"""Use case: read what a source text that is in no file imports, with the reader of the app's language, on an
in-memory reader."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from xarch.kernel.source import Import, Unparsable
from xarch.modules.rules.application.controller import ReaderController
from xarch.modules.rules.application.services.source_reading import SourceReadService
from xarch.modules.rules.domain.values import SourceFile

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
