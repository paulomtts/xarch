"""The must-import check on hand-made source files: a file of a part that lists `must_import` imports one of the listed
parts or an outside package, or reaches one through a file of its own part, unless it is a package marker or holds no
code of its own."""
import pytest

from tests.modules.rules.builders import imp, profile, source
from xarch.kernel.logic.placement import Target
from xarch.modules.rules.application.logic.must_import import violations
from xarch.modules.rules.domain.values import Function

REQUIRED = profile(must_import={"adapters": (Target("platform"), Target("contract", "any"))})
CODE = (Function(3, "get", statements=2),)
DIR = "modules/docs/adapters"
MESSAGE = ("app/modules/docs/adapters/{name}.py: adapters/ of modules/docs imports nothing from platform/ or contract/ "
           "and no outside package, so it touches no technology (parts.adapters.must_import)")


def problems(*files, checked=REQUIRED) -> list[str]:
    return [str(v) for v in violations(list(files), checked, "app")]


def adapter(name: str, *imports, functions=CODE, **fields):
    return source(f"{DIR}/{name}.py", *imports, functions=functions, **fields)


@pytest.mark.parametrize("imports, expected", [
    pytest.param([imp(1, "app.platform.sql", "Engine")], [], id="an import from a part that must be imported"),
    pytest.param([imp(1, "app.platform", "sql")], [], id="a package of that part"),
    pytest.param([imp(1, "app.modules.mod.contract", "Clean")], [], id="a target of any instance"),
    pytest.param([imp(1, "sqlmodel", "Session")], [], id="an outside package"),
    pytest.param([imp(1, "sqlmodel.orm", "Session")], [], id="a package below an outside package"),
    pytest.param([imp(1, "app.modules.docs.application.ports.repo", "Repo")], ["{name}"],
                 id="only a part the profile does not list"),
    pytest.param([imp(1, "pathlib", "Path"), imp(2, "json")], ["{name}"], id="the standard library is no technology"),
    pytest.param([], ["{name}"], id="no import at all"),
    pytest.param([imp(1, "app.kernel.ids", "new_id")], ["{name}"], id="a part that may be imported but is not listed"),
    pytest.param([imp(1, "", "sql", level=3)], ["{name}"], id="a relative import of what is not listed"),
])
def test_a_file_of_the_part_imports_a_listed_part_or_an_outside_package(imports, expected):
    assert problems(adapter("db_repo", *imports)) == [MESSAGE.format(name="db_repo") for _ in expected]


def test_a_relative_import_of_a_listed_part_counts():
    assert problems(source("modules/docs/adapters/db_repo.py", imp(1, "platform", "sql", level=4), functions=CODE)) == []


@pytest.mark.parametrize("name, fields", [
    pytest.param("__init__", {}, id="a package marker"),
    pytest.param("shapes", {"functions": ()}, id="a file with no function holds types or constants only"),
    pytest.param("stubs", {"functions": (Function(3, "get"), Function(5, "put", statements=0))},
                 id="functions with no real statement"),
])
def test_a_file_with_no_code_of_its_own_is_exempt(name, fields):
    assert problems(adapter(name, **fields)) == []


def test_a_file_that_reaches_technology_through_a_file_of_its_own_part_is_satisfied():
    base = adapter("base", imp(1, "app.platform.sql", "Engine"))
    middle = adapter("middle", imp(1, "app.modules.docs.adapters.base", "Base"))
    top = adapter("top", imp(1, "app.modules.docs.adapters", "middle"))
    assert problems(top, middle, base) == []


def test_two_files_that_reach_only_each_other_are_both_reported():
    one = adapter("one", imp(1, "app.modules.docs.adapters.two", "Two"))
    two = adapter("two", imp(1, "app.modules.docs.adapters.one", "One"))
    assert problems(one, two) == [MESSAGE.format(name="one"), MESSAGE.format(name="two")]


def test_a_file_of_another_instance_is_no_way_to_technology():
    other = source("modules/mod/adapters/b.py", imp(1, "app.platform.sql", "Engine"), functions=CODE)
    mine = adapter("a", imp(1, "app.modules.mod.adapters.b", "B"))
    assert problems(mine, other) == [MESSAGE.format(name="a")]


def test_a_part_that_lists_nothing_and_a_file_in_no_part_are_not_checked():
    assert problems(adapter("db_repo"), checked=profile()) == []
    assert problems(source("modules/docs/domain/x.py", functions=CODE)) == []


def test_the_violation_is_for_the_whole_file_and_says_what_to_do():
    [found] = violations([adapter("db_repo")], REQUIRED, "app")
    assert (found.line, found.rule) == (0, "must-import")
    assert found.fix == ("import what it wraps from platform/ or contract/, or an outside package, or move its code to "
                         "a part that needs no technology")
