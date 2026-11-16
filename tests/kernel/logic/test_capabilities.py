"""What a check reads of the source: a key falls short of a language by the facts it needs that the language grades
partial or does not grade."""
import pytest

from xarch.kernel.logic.capabilities import shortfalls
from xarch.profile_values.capabilities import EXACT, Shortfall, Supply

SUPPLIES = {"import": Supply("import", EXACT), "class": Supply("class", "partial", "nested classes are not read")}


@pytest.mark.parametrize("needs, short", [
    pytest.param(("import",), [], id="a key whose facts are all supplied exactly falls short of nothing"),
    pytest.param(("class",), [Shortfall("parts.x.names", "class", "nested classes are not read")],
                 id="a fact supplied partly is a shortfall with the reader's note"),
    pytest.param(("call", "import"), [Shortfall("parts.x.names", "call", None)],
                 id="a fact the language does not grade is a shortfall with no note"),
])
def test_shortfalls(needs, short):
    assert shortfalls("parts.x.names", needs, SUPPLIES) == short
