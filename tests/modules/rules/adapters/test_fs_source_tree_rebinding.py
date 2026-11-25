"""FsSourceTree on real files: a name bound once in its scope by a plain assignment of another bare name, `x = y`, reaches
what that name reaches; nothing cleverer is followed. A call's callee also records what its first argument reaches
through an import, its subject."""
import sys
from pathlib import Path

import pytest

from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.modules.rules.domain.parsed import SourceFile
from xarch.platform.filesystem import FileSystem

NOW = ("datetime", "datetime", "now")


def parsed(tmp_path: Path, text: str) -> SourceFile:
    (tmp_path / "x.py").write_text(text)
    return FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], standard=frozenset(sys.stdlib_module_names),
                                           private="_", special=r"(?=__)\w*(?<=__)")[0]


def uses_of(tmp_path: Path, text: str, name: tuple[str, ...]) -> list[int]:
    return [u.line for u in parsed(tmp_path, text).uses if u.name == name]


@pytest.mark.parametrize("text, lines", [
    pytest.param("from datetime import datetime as D\nclock = D\nclock.now()\n", [3],
                 id="a name bound to an imported name at module level"),
    pytest.param("from datetime import datetime as D\n\n\ndef f():\n    clock = D\n    return clock.now()\n", [6],
                 id="in a function, to a name of the module"),
    pytest.param("from datetime import datetime\nclock = datetime\nagain = clock\nagain.now()\n", [4],
                 id="through two plain rebindings"),
    pytest.param("from datetime import datetime as D\nclock = D\nclock = object\nclock.now()\n", [],
                 id="not a name bound twice, differently"),
    pytest.param("from datetime import datetime as D\nclock = D if True else None\nclock.now()\n", [],
                 id="not an expression"),
    pytest.param("from datetime import datetime as D\nclock, other = D, D\nclock.now()\n", [],
                 id="not an unpacking"),
    pytest.param("from datetime import datetime as D\nclock: type = D\nclock.now()\n", [],
                 id="not an annotated assignment"),
    pytest.param("from datetime import datetime as D\n\n\ndef f(clock=D):\n    return clock.now()\n", [],
                 id="not a default of a parameter"),
])
def test_a_plain_rebinding_is_followed_and_nothing_cleverer(tmp_path, text, lines):
    assert uses_of(tmp_path, text, NOW) == lines


def test_a_call_through_a_rebinding_names_its_callee_by_the_import(tmp_path):
    found = parsed(tmp_path, "from datetime import datetime as D\nclock = D\nclock.now()\n")
    assert [(c.line, c.func) for c in found.calls] == [(3, NOW)]


def test_names_that_rebind_each_other_reach_nothing(tmp_path):
    assert [u.name for u in parsed(tmp_path, "a = b\nb = a\na.x()\n").uses if u.line == 3] == []


@pytest.mark.parametrize("text, subject", [
    pytest.param('import time as t\ngetattr(t, "time")()\n', ("time",), id="the module an import binds"),
    pytest.param('from os import path\ngetattr(path, name)\n', ("os", "path"), id="by a name worked out at run time"),
    pytest.param('def f(o):\n    return getattr(o, "x")\n', None, id="a parameter is no import"),
    pytest.param('getattr("text", "upper")\n', None, id="nor is a literal"),
])
def test_a_callee_records_what_its_first_argument_reaches_through_an_import(tmp_path, text, subject):
    callee = [u for u in parsed(tmp_path, text).uses if u.name == ("builtins", "getattr")]
    assert [u.subject for u in callee] == [subject]
