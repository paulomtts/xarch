"""How a profile writes a target, read against the parts by their paths and the part that writes it, and written back
as it is read."""
import pytest

from xarch.kernel.logic.targets import target, target_written
from xarch.profile_values.placement import Target

PARTS = {"domain": ("modules", "*", "domain"), "services": ("modules", "*", "services"), "kernel": ("kernel",)}
SERVICES = ("services", PARTS["services"])


READ = [
    pytest.param("domain", SERVICES, Target("domain", "own"), id="a bare name in the importer's repeating folder is its own instance"),
    pytest.param("domain@any/values", SERVICES, Target("domain", "any", ("values",)), id="any instance, and a path below"),
    pytest.param("kernel:*Id", SERVICES, Target("kernel", "none", (), "*Id"), id="a part outside, narrowed by a name pattern"),
    pytest.param("domain@any", None, Target("domain", "any"), id="a scope of no part reaches an instance only by @any"),
]


@pytest.mark.parametrize("written, owner, found", READ)
def test_a_target_is_read_from_its_written_form(written, owner, found):
    problems: list[str] = []
    assert (target(written, owner, PARTS, PARTS, "at", problems, patterns=True), problems) == (found, [])


@pytest.mark.parametrize("written, owner, found", READ)
def test_a_target_is_written_as_it_is_read_and_reads_back_as_itself(written, owner, found):
    assert (target_written(found), target(target_written(found), owner, PARTS, PARTS, "at", [], patterns=True)) == (
        written, found)


@pytest.mark.parametrize("written, owner, problem", [
    pytest.param("nowhere", SERVICES, "at: 'nowhere' names no part 'nowhere'", id="a part the profile has not"),
    pytest.param("domain", None, "at: 'domain' lies in the repeating folder, which a tier's folder is not in: say "
                                 "domain@any", id="an instance asked for from outside the repeating folder"),
    pytest.param("services", SERVICES, "at: 'services' is implied: a part may always import itself, its own instance "
                                       "of the repeating folder; remove it (services@any, another instance's too, stays "
                                       "allowed)", id="the part itself"),
    pytest.param("kernel:*Id", SERVICES, "at: 'kernel:*Id' has a name pattern: only a part's `may_import` narrows what "
                                         "may be imported by name", id="a name pattern where none is allowed"),
])
def test_a_target_that_is_not_one_is_none_with_its_problem(written, owner, problem):
    problems: list[str] = []
    assert (target(written, owner, PARTS, PARTS, "at", problems), problems) == (None, [problem])
