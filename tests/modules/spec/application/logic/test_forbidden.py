"""The `forbidden` key of a profile of format 2: named lists of the calls and modules a part may not use, and the
tiers whose tests are held to the list of the part they mirror."""
import pytest

from tests.modules.spec.profiles_v2 import covered, parsed, problems
from xarch.modules.spec.application.logic.docs_template import fill

DOTTED = "is not a dotted name such as datetime.datetime.now, nor an import name such as socket"
METHOD = f"{DOTTED}, nor a method such as .absolute()"


def with_list(names, **changes) -> dict:
    """The covered profile with a list `pure` of the names, which the service part refers to."""
    document = covered(forbidden={"pure": names}, **changes)
    document["parts"]["service"]["forbidden"] = "pure"
    return document


@pytest.mark.parametrize("name, problem", [
    pytest.param("datetime..now", f"forbidden.pure: 'datetime..now' {METHOD}", id="a dotted name with an empty step"),
    pytest.param("2fast", f"forbidden.pure: '2fast' {METHOD}", id="a name that starts with a digit"),
    pytest.param(3, f"forbidden.pure: 3 {METHOD}", id="a name that is no text"),
])
def test_a_bad_forbidden_name_is_refused_saying_what_to_write(name, problem):
    assert problems(with_list([name])) == [f"layered.yaml: {problem}"]


@pytest.mark.parametrize("name, problem", [
    pytest.param("open", "forbidden.pure: 'open' is a Python builtin, which a bare name does not ban: write "
                         "builtins.open", id="a bare builtin is rejected with the name to write instead"),
    pytest.param("print", "forbidden.pure: 'print' is a Python builtin, which a bare name does not ban: write "
                          "builtins.print", id="another bare builtin is rejected"),
    pytest.param("__import__", "forbidden.pure: '__import__' is a Python builtin, which a bare name does not ban: "
                               "write builtins.__import__", id="a dunder builtin is rejected"),
])
def test_a_builtin_named_bare_bans_nothing_so_it_is_rejected(name, problem):
    assert problems(with_list([name])) == [f"layered.yaml: {problem}"]


@pytest.mark.parametrize("name", [
    pytest.param("builtins.open", id="a builtin written as builtins.<name> is a dotted name"),
    pytest.param("socket", id="a module that is no builtin stays an import name"),
    pytest.param("time", id="a module whose name only resembles a builtin's stays an import name"),
    pytest.param("open.read", id="a dotted name starting with a builtin's is not a bare name"),
    pytest.param("Open", id="a name that differs from a builtin by case is no builtin"),
])
def test_a_name_that_is_no_bare_builtin_is_kept(name):
    assert parsed(with_list([name])).forbidden == {"service": (tuple(name.split(".")),)}


def test_a_method_written_with_a_leading_dot_and_parentheses_is_kept_as_written():
    assert parsed(with_list([".absolute()", "pathlib.Path.cwd"])).forbidden == {
        "service": (("", "absolute()"), ("pathlib", "Path", "cwd"))}


@pytest.mark.parametrize("name, problem", [
    pytest.param(".absolute", "forbidden.pure: '.absolute' is neither a dotted name nor a method: write .absolute() for "
                              "a method called on anything", id="a method without its parentheses"),
    pytest.param("path.absolute()", f"forbidden.pure: 'path.absolute()' {METHOD}", id="a dotted name with parentheses"),
    pytest.param(".a.b()", f"forbidden.pure: '.a.b()' {METHOD}", id="a method of more than one step"),
    pytest.param(".__init__()", "forbidden.pure: '.__init__()' is a special method, which no code calls by name",
                 id="a special method of the language"),
])
def test_a_bad_method_is_refused_saying_what_to_write(name, problem):
    assert problems(with_list([name])) == [f"layered.yaml: {problem}"]


def test_the_guards_section_shows_a_method_as_written_and_says_what_it_does_not_see():
    document = with_list([".resolve()", "os.getcwd"])
    lines = fill("{{guards}}", parsed(document), "layered.md").splitlines()
    assert lines[3] == (
        "- `forbidden`: a part neither imports nor uses by name what is listed for it (`service/`: `.resolve()`, "
        "`os.getcwd`). It catches what is written in the part's own files, through their imports and aliases, and a "
        "method written `.name()` called on anything but the object itself and what it holds; not a name reached "
        "through a variable or `getattr`, nor I/O done on the part's behalf elsewhere.")


def test_a_tier_may_hold_its_tests_to_the_list_of_the_part_they_mirror():
    document = with_list(["socket"])
    document["tiers"]["unit"]["apply_forbidden"] = True
    assert [tier.forbidden for tier in parsed(document).tiers] == [True, False]


def test_the_guards_section_lists_the_names_each_part_may_not_use_and_says_what_it_does_not_see():
    document = covered(forbidden={"clock": ["time.time", "socket"], "printing": ["builtins.print"]})
    document["parts"]["service"]["forbidden"] = "clock"
    document["parts"]["store"]["forbidden"] = "clock"
    document["parts"]["api"]["forbidden"] = "printing"
    document["tiers"]["unit"]["apply_forbidden"] = True
    lines = fill("{{guards}}", parsed(document), "layered.md").splitlines()
    assert lines[3] == (
        "- `forbidden`: a part neither imports nor uses by name what is listed for it (`api/`: `builtins.print`; "
        "`service/` and `store/`: `time.time`, `socket`), and neither do the "
        "unit tests of those parts. It catches what is written in the part's own files, through their imports and "
        "aliases, not a name reached through a variable or `getattr`, nor I/O done on the part's behalf elsewhere.")
