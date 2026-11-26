"""How a stale entry of an accepted list is fixed when it writes its path with the app folder's name first: the fix
says to write it below the app, when the path is there once that name is taken off; else the fix it has stays."""
import pytest

from xarch.kernel.logic.accepted_paths import stale_fix

THERE = {("core", "ports.py"), ("modules", "docs")}
FIX = "drop the entry of app/core/ports.py from checks.x.accepted"


@pytest.mark.parametrize("written, fix", [
    pytest.param("app/core/ports.py", "write the path relative to the app: core/ports.py, not app/core/ports.py",
                 id="a path there once the app folder's name is taken off"),
    pytest.param("app/modules/docs/", "write the path relative to the app: modules/docs/, not app/modules/docs/",
                 id="a folder, its trailing slash kept"),
    pytest.param("app/core/gone.py", FIX, id="a path not there either way keeps its fix"),
    pytest.param("core/ports.py", FIX, id="a path that does not start with the app folder's name keeps its fix"),
    pytest.param("application/core/ports.py", FIX, id="a first step that only starts with the name keeps its fix"),
    pytest.param("app", FIX, id="the app folder's name alone keeps its fix"),
])
def test_a_path_written_with_the_app_folder_first_is_fixed_to_its_path_below_the_app(written, fix):
    assert stale_fix(written, "app", lambda steps: steps in THERE, FIX) == fix
