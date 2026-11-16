"""Which files review judges, and why each other one is left out."""
from pathlib import Path

import pytest

from tests.modules.review.builders import BROKEN, found
from xarch.kernel.source import Unparsable
from xarch.modules.review.application.logic.selection import chosen, judged, left_out, ways, within_cap
from xarch.modules.review.domain.errors import AllWithOthers, NoSelection, OverCap
from xarch.modules.review.domain.published import BY_ALL, BY_LIST, BY_PATHS, MIN_CHARS, MISSING, SMALL, UNPARSABLE, LeftOut
from xarch.modules.review.domain.values import Found

APP = Path("/src/app")
A, B = Path("app/a.py"), Path("app/b.py")


@pytest.mark.parametrize("paths, listed, every, then", [
    pytest.param((A,), (B,), False, (A, B), id="paths and those listed, in that order"),
    pytest.param((), (B,), False, (B,), id="a list alone"),
    pytest.param((), (), True, (APP,), id="every file of the app is the app folder"),
])
def test_the_paths_to_read(paths, listed, every, then):
    assert chosen(paths, listed, every, APP) == then


@pytest.mark.parametrize("paths, listed, every, error", [
    pytest.param((), (), False, NoSelection, id="nothing chosen"),
    pytest.param((A,), (), True, AllWithOthers, id="every file with paths"),
    pytest.param((), (B,), True, AllWithOthers, id="every file with a list"),
])
def test_a_choice_that_cannot_be_read_is_refused(paths, listed, every, error):
    with pytest.raises(error):
        chosen(paths, listed, every, APP)


@pytest.mark.parametrize("paths, listed, every, then", [
    pytest.param((A,), (B,), False, (BY_PATHS, BY_LIST), id="paths and a list"),
    pytest.param((), (), True, (BY_ALL,), id="every file"),
])
def test_how_the_files_were_chosen(paths, listed, every, then):
    assert ways(paths, listed, every) == then


@pytest.mark.parametrize("file, why", [
    pytest.param(BROKEN, UNPARSABLE, id="a file that does not parse"),
    pytest.param(found(text="x" * (MIN_CHARS - 1)), SMALL, id="under the smallest size judged"),
    pytest.param(found(text="x" * (MIN_CHARS - 1), error=Unparsable(1, "bad")), UNPARSABLE,
                 id="a file that does not parse, whatever its size"),
])
def test_why_a_file_read_is_left_out(file, why):
    assert (judged(Found((file,))), left_out(Found((file,)))) == ((), (LeftOut(file.file, why, len(file.text)),))


@pytest.mark.parametrize("file", [
    pytest.param(found(), id="a file read that parses and is big enough"),
    pytest.param(found(text="x" * MIN_CHARS), id="a file of exactly the smallest size judged"),
])
def test_a_file_is_judged(file):
    assert (judged(Found((file,))), left_out(Found((file,)))) == ((file,), ())


def test_the_files_not_read_come_first_then_those_read_not_judged_each_in_order():
    small = found("app/modules/documents/domain/small.py", text="x = 1\n")
    missing = LeftOut("app/gone.py", MISSING)
    files = Found((found(), small, BROKEN), (missing,))
    assert (judged(files), left_out(files)) == ((found(),), (missing, LeftOut(small.file, SMALL, 6),
                                                             LeftOut(BROKEN.file, UNPARSABLE, len(BROKEN.text))))


def test_no_more_files_than_one_run_judges():
    files = (found(), found("app/x.py"))
    assert within_cap(files, 2) == files
    with pytest.raises(OverCap) as refused:
        within_cap(files, 1)
    assert (refused.value.chosen, refused.value.cap) == (2, 1)
