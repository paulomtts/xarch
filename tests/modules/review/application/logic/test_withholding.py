"""Which files review never sends: those a path of `review.never` matches, step by step, below the app; each is left
out with the path that matched, and the others are kept in order."""
import pytest

from tests.modules.review.builders import found
from xarch.modules.review.application.logic.withholding import held_back
from xarch.modules.review.domain.published import MISSING, NEVER, LeftOut
from xarch.modules.review.domain.values import Found

FILE = "app/modules/documents/adapters/legal_archive.py"


@pytest.mark.parametrize("pattern", [
    pytest.param("modules/documents/adapters/legal_archive.py", id="the file's own path"),
    pytest.param("modules/documents/adapters", id="a folder above the file"),
    pytest.param("modules", id="the first folder below the app"),
    pytest.param("modules/*/adapters", id="a star stands for one step"),
    pytest.param("modules/documents/adapters/legal_*.py", id="a star stands for any text inside a step"),
    pytest.param("**/legal_archive.py", id="two stars stand for any number of folders"),
    pytest.param("modules/**/legal_archive.py", id="two stars between steps"),
    pytest.param("modules/documents/adapters/**/legal_archive.py", id="two stars stand for no folder too"),
    pytest.param("**/adapters", id="two stars then a folder above the file"),
])
def test_a_path_holds_back_a_file_it_matches_step_by_step_below_the_app(pattern):
    file = found(FILE)
    assert held_back(Found((file,)), (pattern,)) == Found((), (LeftOut(FILE, NEVER, len(file.text), pattern),))


@pytest.mark.parametrize("pattern", [
    pytest.param("modules/*/legal_archive.py", id="a star stands for one step, never two"),
    pytest.param("documents/adapters", id="a path is read from the app folder, not from anywhere"),
    pytest.param("app/modules", id="the app folder's own name is no step of the path"),
    pytest.param("modules/documents/adapters/legal", id="a step matches whole, never a start of it"),
    pytest.param("Modules", id="case counts"),
    pytest.param("modules/documents/adapters/legal_archive.py/x", id="a path longer than the file's"),
])
def test_a_path_that_does_not_match_the_file_keeps_it(pattern):
    file = found(FILE)
    assert held_back(Found((file,)), (pattern,)) == Found((file,))


def test_the_first_path_that_matches_is_the_one_said_and_files_already_left_out_come_first():
    held, other = found(FILE), found("app/modules/documents/domain/document.py")
    gone = LeftOut("app/modules/documents/domain/gone.py", MISSING)
    assert held_back(Found((held, other), (gone,)), ("**/domain/gone.py", "**/adapters", "modules/*/adapters")) == Found(
        (other,), (gone, LeftOut(FILE, NEVER, len(held.text), "**/adapters")))
    assert held_back(Found((held, other)), ()) == Found((held, other))
