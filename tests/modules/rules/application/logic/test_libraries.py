"""The outside-libraries check on hand-made source files: code in a part imports only the standard library, the app's
own package and the outside packages `libraries` lists for that part."""
import pytest

from tests.modules.rules.builders import PROFILE, imp, profile, source
from xarch.kernel.logic.placement import EVERYTHING
from xarch.modules.rules.application.logic.libraries import violations


def problems(path: str, *imports, checked=PROFILE) -> list[str]:
    return [str(v) for v in violations([source(path, *imports)], checked, "app")]


def message(path: str, line: int, label: str, part: str, package: str) -> str:
    return f"app/{path}:{line}: {label} may not import the outside package {package} (parts.{part}.libraries)"


def test_a_part_listed_as_everything_may_import_any_outside_package_while_another_part_still_may_not():
    checked = profile(libraries={**PROFILE.libraries, "bootstrap": (EVERYTHING,)})
    assert problems("bootstrap/app.py", imp(1, "anything", "x"), imp(2, "fastapi"), checked=checked) == []
    assert problems("platform/sql.py", imp(1, "anything", "x"), checked=checked) == [
        message("platform/sql.py", 1, "platform/", "platform", "anything")]


@pytest.mark.parametrize("path, imports, expected", [
    pytest.param("platform/sql.py", [imp(1, "sqlmodel", "SQLModel"), imp(2, "sqlmodel.orm")], [],
                 id="a package listed for the part, and what lies below it"),
    pytest.param("platform/sql.py", [imp(1, "json"), imp(2, "collections.abc", "Iterable"), imp(3, "__future__", "x")],
                 [], id="the standard library"),
    pytest.param("platform/sql.py", [imp(1, "app.kernel", "ids"), imp(2, "app")], [], id="the app's own package"),
    pytest.param("platform/sql.py", [imp(1, "", "x", up=0), imp(2, "yaml", "load", up=1)], [],
                 id="a relative import is the app's own"),
    pytest.param("platform/sql.py", [imp(3, "fastapi", "FastAPI")],
                 [message("platform/sql.py", 3, "platform/", "platform", "fastapi")],
                 id="a package listed for another part is reported"),
    pytest.param("platform/sql.py", [imp(3, "sqlmodelx")],
                 [message("platform/sql.py", 3, "platform/", "platform", "sqlmodelx")],
                 id="a package is matched by its whole top-level name"),
    pytest.param("modules/docs/domain/doc.py", [imp(2, "yaml"), imp(4, "yaml.parser", "Parser")],
                 [message("modules/docs/domain/doc.py", 2, "domain/ of modules/docs", "domain", "yaml"),
                  message("modules/docs/domain/doc.py", 4, "domain/ of modules/docs", "domain", "yaml")],
                 id="a part libraries does not list may import no outside package, each import reported"),
    pytest.param("kernel/ids.py", [imp(2, "yaml"), imp(2, "yaml.parser"), imp(2, "attr")],
                 [message("kernel/ids.py", 2, "kernel/", "kernel", "yaml"),
                  message("kernel/ids.py", 2, "kernel/", "kernel", "attr")],
                 id="a package imported twice on one line is reported once"),
    pytest.param("modules/docs/__init__.py", [imp(1, "yaml")], [],
                 id="a package file of the structure is not checked"),
    pytest.param("modules/docs/application/__init__.py", [imp(1, "yaml")], [],
                 id="nor is one deeper in the structure"),
    pytest.param("scripts/seed.py", [imp(1, "yaml")], [], id="an ungoverned file is not checked"),
])
def test_libraries(path, imports, expected):
    assert problems(path, *imports) == expected


def test_without_libraries_in_the_profile_nothing_is_checked():
    assert problems("kernel/ids.py", imp(1, "yaml"), checked=profile(libraries=None)) == []


def test_the_apps_package_is_the_root_it_is_given():
    assert [str(v) for v in violations([source("kernel/ids.py", imp(1, "app.kernel", "x"))], PROFILE, "shop")] == [
        "app/kernel/ids.py:1: kernel/ may not import the outside package app (parts.kernel.libraries)"]


def test_a_violation_names_its_rule():
    assert [v.rule for v in violations([source("kernel/ids.py", imp(1, "yaml"))], PROFILE, "app")] == ["libraries"]


@pytest.mark.parametrize("path, imports, fix", [
    pytest.param("platform/sql.py", [imp(3, "fastapi", "FastAPI")],
                 "move the code that needs fastapi to web/, bootstrap/, which may import it (parts.web.libraries)",
                 id="a package listed for another part names that part"),
    pytest.param("web/routes.py", [imp(3, "sqlmodel", "SQLModel")],
                 "move the code that needs sqlmodel to platform/, adapters/, bootstrap/, which may import it "
                 "(parts.platform.libraries)", id="a package listed for several parts names them all"),
    pytest.param("platform/sql.py", [imp(3, "requests")],
                 "use the standard library or a package listed in parts.platform.libraries, since requests is listed for "
                 "no part", id="a package no part lists"),
])
def test_a_violation_says_what_to_do(path, imports, fix):
    assert [(v.rule, v.fix) for v in violations([source(path, *imports)], PROFILE, "app")] == [("libraries", fix)]


RESERVING = profile(libraries={**PROFILE.libraries, "adapters": ("sqlmodel", "ast")},
                    reserved={"ast": "only the reader parses the language", "tokenize": "the reader's"})


@pytest.mark.parametrize("path, imports, expected", [
    pytest.param("modules/docs/adapters/reader.py", [imp(1, "ast"), imp(2, "json")], [],
                 id="a reserved module the part lists, and another standard module"),
    pytest.param("modules/docs/application/logic/rule.py", [imp(1, "ast"), imp(2, "ast", "parse"), imp(3, "json")],
                 ["app/modules/docs/application/logic/rule.py:1: logic/ of modules/docs may not import ast, which the "
                  "profile reserves: only the reader parses the language (reserved.ast; parts.logic.libraries)",
                  "app/modules/docs/application/logic/rule.py:2: logic/ of modules/docs may not import ast, which the "
                  "profile reserves: only the reader parses the language (reserved.ast; parts.logic.libraries)"],
                 id="a reserved module a part does not list is reported at each import"),
    pytest.param("modules/docs/application/logic/rule.py", [imp(1, "ast.nodes")],
                 ["app/modules/docs/application/logic/rule.py:1: logic/ of modules/docs may not import ast, which the "
                  "profile reserves: only the reader parses the language (reserved.ast; parts.logic.libraries)"],
                 id="what lies below a reserved module is it"),
])
def test_a_reserved_module_of_the_standard_library_is_imported_only_by_the_parts_that_list_it(path, imports, expected):
    assert problems(path, *imports, checked=RESERVING) == expected


def test_a_reserved_module_says_where_its_code_belongs_or_that_no_part_may_import_it():
    listed = violations([source("kernel/x.py", imp(1, "ast"))], RESERVING, "app")[0]
    unlisted = violations([source("kernel/x.py", imp(1, "tokenize"))], RESERVING, "app")[0]
    assert (listed.rule, listed.fix) == ("libraries", "move the code that needs ast to adapters/, which may import it "
                                                      "(parts.adapters.libraries)")
    assert unlisted.fix == ("list tokenize in the libraries of the part it is reserved for, and keep the code that "
                            "needs it there")
