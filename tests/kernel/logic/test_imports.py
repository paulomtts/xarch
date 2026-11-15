"""How what a part may import is said in words: the phrase the docs' rules table and `xarch where` share."""
import pytest

from xarch.kernel.logic.imports import may_import
from xarch.kernel.logic.placement import EVERYTHING, Target

FOLDERS = {"domain": "domain/", "kernel": "kernel/", "contract": "contract/", "ports": "ports/", "platform": "platform/"}


@pytest.mark.parametrize("targets, expected", [
    pytest.param([], "nothing", id="no target means nothing"),
    pytest.param([Target(EVERYTHING)], "everything", id="everything"),
    pytest.param([Target("domain", "own"), Target("kernel")], "its own module's `domain/`, `kernel/`",
                 id="a scoped target and a plain one"),
    pytest.param([Target("ports", "own"), Target("domain", "own"), Target("kernel")],
                 "its own module's `ports/` and `domain/`, `kernel/`", id="neighbours of one scope share their phrase"),
    pytest.param([Target("platform"), Target("contract", "any")], "`platform/`, any module's `contract/`",
                 id="another scope starts a new phrase"),
    pytest.param([Target("domain", "own", ("values",))], "its own module's `domain/values`", id="a path below a part"),
])
def test_what_a_part_may_import_in_words(targets, expected):
    assert may_import(targets, FOLDERS, "module") == expected
