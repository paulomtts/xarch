"""The structure rule on plain values: what must exist below the root, and what is missing."""
import pytest

from tests.modules.layout.builders import PYTHON_NAMING
from xarch.modules.layout.application.logic.requirements import anchors, missing, requirements
from xarch.modules.layout.domain.structure import Repeated, Requirement

PARTS = [(("domain",), True), (("application", "controller.py"), False)]


MODULES = Requirement("app", ("modules",), True, "modules/")


def parts_of(name: str) -> list[Requirement]:
    """What PARTS requires of the instance name of modules/."""
    return [Requirement(f"app/modules/{name}", ("modules", name, "domain"), True, "domain/"),
            Requirement(f"app/modules/{name}", ("modules", name, "application", "controller.py"), False,
                        "application/controller.py")]


@pytest.mark.parametrize("name, required", [
    pytest.param("docs", [MODULES, *parts_of("docs")], id="an identifier is an instance"),
    pytest.param("doc_store2", [MODULES, *parts_of("doc_store2")],
                 id="an identifier with an underscore and a digit is an instance"),
    pytest.param("_private", [MODULES], id="a name starting with an underscore is private"),
    pytest.param("__pycache__", [MODULES], id="a cache folder is not an instance"),
    pytest.param("not-a-module", [MODULES], id="a name that is no identifier is not an instance"),
    pytest.param("2docs", [MODULES], id="a name starting with a digit is not an instance"),
])
def test_a_folder_of_a_repeating_folder_is_an_instance_when_its_name_is_a_public_name_of_the_language(name, required):
    assert requirements("app", [("modules",)], [Repeated(("modules",), PARTS, [name])], (), PYTHON_NAMING) == required


@pytest.mark.parametrize("repeated, required", [
    pytest.param([], [Requirement("app", ("kernel",), True, "kernel/"),
                                  Requirement("app", ("modules",), True, "modules/")],
                 id="without an each folder only the top level is required"),
    pytest.param([Repeated(("modules",), PARTS, [])], [Requirement("app", ("kernel",), True, "kernel/"),
                                    Requirement("app", ("modules",), True, "modules/")],
                 id="with no instance only the top level is required"),
    pytest.param([Repeated(("modules",), PARTS, ["users", "_cache", "docs"])], [
        Requirement("app", ("kernel",), True, "kernel/"), Requirement("app", ("modules",), True, "modules/"),
        Requirement("app/modules/docs", ("modules", "docs", "domain"), True, "domain/"),
        Requirement("app/modules/docs", ("modules", "docs", "application", "controller.py"), False,
                    "application/controller.py"),
        Requirement("app/modules/users", ("modules", "users", "domain"), True, "domain/"),
        Requirement("app/modules/users", ("modules", "users", "application", "controller.py"), False,
                    "application/controller.py")],
                 id="every part of every instance is required, instances by name, a private folder left out"),
    pytest.param([Repeated(("src", "features"), PARTS, ["docs"])], [
        Requirement("app", ("kernel",), True, "kernel/"), Requirement("app", ("modules",), True, "modules/"),
        Requirement("app/src/features/docs", ("src", "features", "docs", "domain"), True, "domain/"),
        Requirement("app/src/features/docs", ("src", "features", "docs", "application", "controller.py"), False,
                    "application/controller.py")],
                 id="an each folder below the top level is owned by its full path"),
])
def test_requirements(repeated, required):
    assert requirements("app", [("kernel",), ("modules",)], repeated, (), PYTHON_NAMING) == required


def test_every_repeating_folder_requires_its_own_parts_of_its_own_instances():
    repeated = [Repeated(("modules",), [(("domain",), True)], ["docs"]),
                Repeated(("plugins",), [(("hooks",), True), (("manifest.py",), False)], ["seo", "_cache"])]
    assert requirements("app", [("kernel",)], repeated, (), PYTHON_NAMING) == [
        Requirement("app", ("kernel",), True, "kernel/"),
        Requirement("app/modules/docs", ("modules", "docs", "domain"), True, "domain/"),
        Requirement("app/plugins/seo", ("plugins", "seo", "hooks"), True, "hooks/"),
        Requirement("app/plugins/seo", ("plugins", "seo", "manifest.py"), False, "manifest.py")]


def test_a_file_declared_at_the_top_level_is_required_as_a_file_after_the_folders():
    assert requirements("app", [("kernel",)], [], [("__main__.py",)], PYTHON_NAMING) == [
        Requirement("app", ("kernel",), True, "kernel/"), Requirement("app", ("__main__.py",), False, "__main__.py")]


def test_a_folder_or_file_below_a_top_level_folder_is_required_as_its_path_shows_it():
    assert requirements("app", [("kernel",), ("kernel", "logic")], [], [("web", "app.py")], PYTHON_NAMING) == [
        Requirement("app", ("kernel",), True, "kernel/"), Requirement("app", ("kernel", "logic"), True, "kernel/logic/"),
        Requirement("app", ("web", "app.py"), False, "web/app.py")]


def test_missing_reports_what_is_not_present_with_its_owner_and_fix():
    kernel, domain = Requirement("app", ("kernel",), True, "kernel/"), Requirement("app/modules/docs", (
        "modules", "docs", "domain"), True, "domain/")
    found = missing([kernel, domain], [kernel])
    assert [(str(v), v.rule, v.fix) for v in found] == [
        ("app/modules/docs: missing domain/", "structure", "create app/modules/docs/domain/")]


def test_what_lies_in_an_optional_part_is_required_only_where_that_part_is_there():
    when = {("api", "routes.py"): ("api",)}
    repeated = [Repeated(("modules",), [(("hooks", "run.py"), False)], ["docs"], {("hooks", "run.py"): ("hooks",)})]
    required = requirements("app", [("kernel",)], repeated, [("api", "routes.py")], PYTHON_NAMING, when)
    assert required == [
        Requirement("app", ("kernel",), True, "kernel/"),
        Requirement("app", ("api", "routes.py"), False, "api/routes.py", ("api",)),
        Requirement("app/modules/docs", ("modules", "docs", "hooks", "run.py"), False, "hooks/run.py",
                    ("modules", "docs", "hooks"))]
    assert anchors(required) == [Requirement("", ("api",), True, "api/"),
                                 Requirement("", ("modules", "docs", "hooks"), True, "modules/docs/hooks/")]


@pytest.mark.parametrize("present, found", [
    pytest.param([], [], id="an optional part that is not there asks for nothing it holds"),
    pytest.param([Requirement("", ("api",), True, "api/")], ["app: missing api/routes.py"],
                 id="an optional part that is there asks for what it holds"),
    pytest.param([Requirement("", ("api",), True, "api/"),
                  Requirement("app", ("api", "routes.py"), False, "api/routes.py", ("api",))], [],
                 id="an optional part that holds what it should is complete"),
])
def test_missing_reports_what_an_optional_part_holds_only_where_the_part_is_there(present, found):
    required = [Requirement("app", ("api", "routes.py"), False, "api/routes.py", ("api",))]
    assert [str(v) for v in missing(required, present)] == found
