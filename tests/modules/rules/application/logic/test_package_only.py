"""The package-only guard on hand-made source files: contract/ is imported as a package, never by its files, from
anywhere outside its own instance's contract/, the app and the tests alike."""
import pytest

from tests.modules.rules.builders import PROFILE, imp, in_tests, profile, source
from xarch.modules.rules.application.logic.package_only import violations

CONTRACTS = [source("modules/docs/contract/__init__.py"), source("modules/docs/contract/results.py"),
             source("modules/other/contract/__init__.py"), source("modules/other/contract/results.py")]


def message(line: int, instance: str, imported: str) -> str:
    return (f"{line}: contract/ of modules/{instance} is imported only as a package, never by its files "
            f"({imported}) (package-only)")


def problems(path: str, *imports, in_app: bool = True, checked=PROFILE) -> list[str]:
    file = source(path, *imports) if in_app else in_tests(path, *imports)
    app, tests = ([file, *CONTRACTS], []) if in_app else (CONTRACTS, [file])
    return [str(v).removeprefix(f"{file.name}:") for v in violations(app, tests, checked, "app")]


@pytest.mark.parametrize("path, imports, expected", [
    pytest.param("web/routes.py", [imp(1, "app.modules.docs.contract", "Published")], [],
                 id="the package itself is fine"),
    pytest.param("web/routes.py", [imp(1, "app.modules.docs.contract.results", "Published")],
                 [message(1, "docs", "app.modules.docs.contract.results")], id="a file of it is reported"),
    pytest.param("web/routes.py", [imp(1, "app.modules.docs.contract", "results")],
                 [message(1, "docs", "app.modules.docs.contract.results")],
                 id="a file imported as a name of the package is a file too"),
    pytest.param("web/routes.py", [imp(1, "app.modules.docs.contract.results")],
                 [message(1, "docs", "app.modules.docs.contract.results")], id="a plain import of a file is reported"),
    pytest.param("modules/docs/contract/__init__.py", [imp(1, "", "Published", level=1),
                                                       imp(2, "app.modules.docs.contract.results", "Missing")], [],
                 id="its own instance's contract imports its files"),
    pytest.param("modules/docs/contract/__init__.py", [imp(1, "app.modules.other.contract.results", "Published")],
                 [message(1, "other", "app.modules.other.contract.results")],
                 id="another instance's contract imports them by package only"),
    pytest.param("modules/docs/adapters/peer.py", [imp(1, "other.contract", "results", level=3)],
                 [message(1, "other", "app.modules.other.contract.results")],
                 id="a relative import in the app is resolved and checked"),
    pytest.param("scripts/seed.py", [imp(1, "app.modules.docs.contract.results", "Published")],
                 [message(1, "docs", "app.modules.docs.contract.results")], id="an ungoverned file is checked too"),
    pytest.param("web/routes.py", [imp(1, "app.modules.docs.domain.doc", "Document"), imp(2, "yaml")], [],
                 id="a part the guard does not name is not its business"),
])
def test_package_only_in_the_app(path, imports, expected):
    assert problems(path, *imports) == expected


@pytest.mark.parametrize("imports, expected", [
    pytest.param([imp(1, "app.modules.docs.contract", "Published")], [], id="a test imports the package"),
    pytest.param([imp(1, "app.modules.docs.contract.results", "Published")],
                 [message(1, "docs", "app.modules.docs.contract.results")], id="a test importing a file is reported"),
    pytest.param([imp(1, "results", "Published", level=1)], [],
                 id="a relative import in a test is test code, not the app's"),
])
def test_package_only_in_the_tests(imports, expected):
    assert problems("modules/docs/contract/test_results.py", *imports, in_app=False) == expected


def test_without_the_guard_nothing_is_checked():
    assert problems("web/routes.py", imp(1, "app.modules.docs.contract.results", "Published"),
                    checked=profile(package_only=())) == []


def test_a_violation_names_its_rule_and_its_fix():
    found = violations([source("web/routes.py", imp(1, "app.modules.docs.contract.results", "P")), *CONTRACTS], [],
                       PROFILE, "app")[0]
    assert (found.rule, found.fix) == ("package-only", "import from app.modules.docs.contract")
