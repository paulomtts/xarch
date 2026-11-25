"""Which violations a check of some paths shows: those of a file at or below a path given, a test's read from the
tests folder's place; the others are counted, not shown."""
from pathlib import PurePosixPath

import pytest

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.chosen import chosen

HOME = PurePosixPath("/src")
TESTS = PurePosixPath("/elsewhere/tests")


def found(file: str) -> Violation:
    return Violation(file, 1, "a problem", "may-import", "do this")


ALL = [found("app/kernel/a.py"), found("app/kernel/logic/b.py"), found("app/modules"), found("tests/test_a.py")]


@pytest.mark.parametrize("paths, shown, elsewhere", [
    pytest.param(["/src/app/kernel/a.py"], ["app/kernel/a.py"], 3, id="a file given shows its own"),
    pytest.param(["/src/app/kernel"], ["app/kernel/a.py", "app/kernel/logic/b.py"], 2,
                 id="a folder given shows those of every file below it"),
    pytest.param(["/src/app/modules"], ["app/modules"], 3, id="a folder's own violation is the folder's"),
    pytest.param(["/elsewhere/tests/test_a.py"], ["tests/test_a.py"], 3,
                 id="a test's file is read below the tests folder, wherever it lies"),
    pytest.param(["/src/tests/test_a.py"], [], 4, id="a path beside the app is not the tests folder's file"),
    pytest.param(["/src/app/kernel/a.py", "/src/app/kernel/a.py"], ["app/kernel/a.py"], 3,
                 id="a path given twice shows its violations once"),
    pytest.param(["/src/app/kern"], [], 4, id="a path is a whole step, not the start of one"),
    pytest.param([], [], 4, id="no path shows nothing"),
])
def test_chosen(paths, shown, elsewhere):
    kept, others = chosen(ALL, [PurePosixPath(p) for p in paths], HOME, TESTS)
    assert ([v.file for v in kept], others) == (shown, elsewhere)


def test_with_no_tests_folder_every_file_is_read_below_the_app_s_home():
    kept, others = chosen(ALL, [PurePosixPath("/src/tests/test_a.py")], HOME, None)
    assert ([v.file for v in kept], others) == (["tests/test_a.py"], 3)
