"""The outside-libraries check on hand-made source files: code in a part imports only the standard library, the app's
own package and the outside packages `libraries` lists for that part."""
import pytest

from tests.modules.rules.builders import PROFILE, imp, profile, source
from xarch.modules.rules.application.logic.libraries import violations


def problems(path: str, *imports, checked=PROFILE) -> list[str]:
    return [str(v) for v in violations([source(path, *imports)], checked, "app")]


def message(path: str, line: int, label: str, part: str, package: str) -> str:
    return f"app/{path}:{line}: {label} may not import the outside package {package} (libraries.{part})"


@pytest.mark.parametrize("path, imports, expected", [
    pytest.param("platform/sql.py", [imp(1, "sqlmodel", "SQLModel"), imp(2, "sqlmodel.orm")], [],
                 id="a package listed for the part, and what lies below it"),
    pytest.param("platform/sql.py", [imp(1, "json"), imp(2, "collections.abc", "Iterable"), imp(3, "__future__", "x")],
                 [], id="the standard library"),
    pytest.param("platform/sql.py", [imp(1, "app.kernel", "ids"), imp(2, "app")], [], id="the app's own package"),
    pytest.param("platform/sql.py", [imp(1, "", "x", level=1), imp(2, "yaml", "load", level=2)], [],
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
        "app/kernel/ids.py:1: kernel/ may not import the outside package app (libraries.kernel)"]


def test_a_violation_names_its_rule():
    assert [v.rule for v in violations([source("kernel/ids.py", imp(1, "yaml"))], PROFILE, "app")] == ["libraries"]
