"""The files a check reads, as a scope: the part it names is the part written, and none for any part or the
structure."""
import pytest

from xarch.profile_values.checks import ANY, STRUCTURE, Scope


@pytest.mark.parametrize("part, named", [
    pytest.param("domain", "domain", id="a part is named"),
    pytest.param(ANY, "", id="any part names none"),
    pytest.param(STRUCTURE, "", id="the structure names none"),
])
def test_a_scope_names_the_part_it_is_written_for_and_none_for_any_part_or_the_structure(part, named):
    assert Scope(part=part).named_part == named
