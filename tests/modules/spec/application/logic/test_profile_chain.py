"""Where a based_on path is read from, the folder of the file that writes it, and the loop a chain of profile files
may close, said from the file the loop comes back to."""
import pytest

from xarch.modules.spec.application.logic.profile_chain import based_on_a_file, refuse_loop, resolved, unloaded
from xarch.modules.spec.domain.errors import InvalidArchitecture


@pytest.mark.parametrize("based_on, file", [
    pytest.param("../team.yaml", True, id="a folder step and a suffix"),
    pytest.param("team.yaml", True, id="a suffix"),
    pytest.param("base/team", True, id="a folder step"),
    pytest.param("cli", False, id="a bare name is a bundled profile"),
    pytest.param("", False, id="no based_on names nothing"),
])
def test_a_based_on_names_a_profile_file_when_it_has_a_folder_step_or_a_suffix(based_on, file):
    assert based_on_a_file(based_on) is file


@pytest.mark.parametrize("writer, based_on, found", [
    pytest.param("sub/mine.yaml", "../team.yaml", "team.yaml", id="from the folder of the file that writes it"),
    pytest.param("/abs/p/mine.yaml", "team.yaml", "/abs/p/team.yaml", id="an absolute writer keeps its folder"),
    pytest.param("mine.yaml", "../a.yaml", "../a.yaml", id="a writer in the working folder"),
    pytest.param("sub/mine.yaml", "./x/../team.yaml", "sub/team.yaml", id="dot steps are collapsed as text"),
    pytest.param("sub/mine.yaml", "../team", "team", id="a single step with no suffix is left as it is"),
])
def test_a_based_on_path_is_read_from_the_folder_of_the_file_that_writes_it(writer, based_on, found):
    assert resolved(writer, based_on) == found


@pytest.mark.parametrize("links, target, reason", [
    pytest.param([("mine.yaml", "mine.yaml")], "mine.yaml",
                 "mine.yaml: based_on: mine.yaml is based on this profile", id="a profile based on itself"),
    pytest.param([("mine.yaml", "a.yaml"), ("a.yaml", "mine.yaml")], "mine.yaml",
                 "mine.yaml: based_on: a.yaml is based on this profile", id="two files say no file between"),
    pytest.param([("p/q/mine.yaml", "../a.yaml"), ("p/a.yaml", "../b.yaml"), ("b.yaml", "p/q/mine.yaml")],
                 "p/q/mine.yaml", "p/q/mine.yaml: based_on: ../a.yaml is based on this profile, through ../b.yaml",
                 id="three files name the based_on of the one between"),
    pytest.param([("mine.yaml", "a.yaml"), ("a.yaml", "b.yaml"), ("b.yaml", "a.yaml")], "a.yaml",
                 "a.yaml: based_on: b.yaml is based on this profile",
                 id="a loop the profile in force is not in is said from the file it comes back to"),
    pytest.param([("./mine.yaml", "mine.yaml")], "mine.yaml",
                 "./mine.yaml: based_on: mine.yaml is based on this profile",
                 id="locations are compared once normalized and said as given"),
])
def test_a_link_back_to_a_file_of_the_chain_is_refused(links, target, reason):
    with pytest.raises(InvalidArchitecture) as caught:
        refuse_loop(links, target)
    assert caught.value.reason == reason


def test_a_link_to_a_file_not_yet_in_the_chain_passes():
    assert refuse_loop([("sub/mine.yaml", "../team.yaml")], "team.yaml") is None


def test_a_file_of_the_chain_that_does_not_load_is_said_with_its_first_problem_and_how_many_more():
    assert unloaded("../team.yaml", ("team.yaml: missing `parts`",)) == (
        "based_on: ../team.yaml does not load: team.yaml: missing `parts`")
    assert unloaded("../team.yaml", ("team.yaml: a", "team.yaml: b", "team.yaml: c")) == (
        "based_on: ../team.yaml does not load: team.yaml: a (and 2 more)")
