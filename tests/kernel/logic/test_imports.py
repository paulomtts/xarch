"""How what a part may import is said in words: the phrase the docs' rules table and `xarch where` share."""
import pytest

from xarch.kernel.logic.imports import may_import
from xarch.kernel.placement import EVERYTHING
from xarch.profile_values.placement import Target

FOLDERS = {"domain": "domain/", "kernel": "kernel/", "contract": "contract/", "ports": "ports/", "platform": "platform/",
           "hooks": "hooks/"}
WORDS = {"domain": "module", "contract": "module", "ports": "module", "hooks": "plugin"}


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
    pytest.param([Target("contract", "any"), Target("hooks", "any"), Target("domain", "any")],
                 "any module's `contract/`, any plugin's `hooks/`, any module's `domain/`",
                 id="each repeating folder is named by its own word"),
    pytest.param([Target("hooks", "any"), Target("domain", "any")], "any plugin's `hooks/`, any module's `domain/`",
                 id="neighbours of one scope in two repeating folders do not share their phrase"),
])
def test_what_a_part_may_import_in_words(targets, expected):
    assert may_import(targets, FOLDERS, WORDS) == expected
