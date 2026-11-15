"""What a check reads of the source: each check's facts are facts of the vocabulary, and a key falls short of a
language by the facts it needs that the language grades partial or does not grade."""
import pytest

from xarch.kernel.logic.capabilities import EXACT, FACTS, NEEDS, PARTIAL, Shortfall, Supply, shortfalls
from xarch.kernel.violations import RULES

SUPPLIES = {"import": Supply("import", EXACT), "class": Supply("class", PARTIAL, "nested classes are not read")}


def test_every_check_names_the_facts_it_reads_from_the_vocabulary():
    assert set(NEEDS) == set(RULES)
    assert {fact for needs in NEEDS.values() for fact in needs} <= set(FACTS)


@pytest.mark.parametrize("needs, short", [
    pytest.param(("import",), [], id="a key whose facts are all supplied exactly falls short of nothing"),
    pytest.param(("class",), [Shortfall("parts.x.names", "class", "nested classes are not read")],
                 id="a fact supplied partly is a shortfall with the reader's note"),
    pytest.param(("call", "import"), [Shortfall("parts.x.names", "call", None)],
                 id="a fact the language does not grade is a shortfall with no note"),
])
def test_shortfalls(needs, short):
    assert shortfalls("parts.x.names", needs, SUPPLIES) == short
