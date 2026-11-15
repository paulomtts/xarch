"""The structure rule on plain values: what must exist below the root, and what is missing."""
import pytest

from xarch.modules.layout.application.logic.requirements import is_instance_name, missing, requirements
from xarch.modules.layout.domain.structure import Naming, Repeated, Requirement

PYTHON_NAMING = Naming(r"(?!\d)\w+", "_")
"""How Python names a folder, as its data file says."""

PARTS = [(("domain",), True), (("application", "controller.py"), False)]


@pytest.mark.parametrize("name, instance", [
    pytest.param("docs", True, id="an identifier is an instance"),
    pytest.param("doc_store2", True, id="an identifier with an underscore and a digit is an instance"),
    pytest.param("_private", False, id="a name starting with an underscore is private"),
    pytest.param("__pycache__", False, id="a cache folder is not an instance"),
    pytest.param("not-a-module", False, id="a name that is no identifier is not an instance"),
    pytest.param("2docs", False, id="a name starting with a digit is not an instance"),
])
def test_is_instance_name(name, instance):
    assert is_instance_name(name, PYTHON_NAMING) == instance


@pytest.mark.parametrize("each_root, instances, required", [
    pytest.param(None, ["docs"], [Requirement("app", ("kernel",), True, "kernel/"),
                                  Requirement("app", ("modules",), True, "modules/")],
                 id="without an each folder only the top level is required"),
    pytest.param(("modules",), [], [Requirement("app", ("kernel",), True, "kernel/"),
                                    Requirement("app", ("modules",), True, "modules/")],
                 id="with no instance only the top level is required"),
    pytest.param(("modules",), ["users", "_cache", "docs"], [
        Requirement("app", ("kernel",), True, "kernel/"), Requirement("app", ("modules",), True, "modules/"),
        Requirement("app/modules/docs", ("modules", "docs", "domain"), True, "domain/"),
        Requirement("app/modules/docs", ("modules", "docs", "application", "controller.py"), False,
                    "application/controller.py"),
        Requirement("app/modules/users", ("modules", "users", "domain"), True, "domain/"),
        Requirement("app/modules/users", ("modules", "users", "application", "controller.py"), False,
                    "application/controller.py")],
                 id="every part of every instance is required, instances by name, a private folder left out"),
    pytest.param(("src", "features"), ["docs"], [
        Requirement("app", ("kernel",), True, "kernel/"), Requirement("app", ("modules",), True, "modules/"),
        Requirement("app/src/features/docs", ("src", "features", "docs", "domain"), True, "domain/"),
        Requirement("app/src/features/docs", ("src", "features", "docs", "application", "controller.py"), False,
                    "application/controller.py")],
                 id="an each folder below the top level is owned by its full path"),
])
def test_requirements(each_root, instances, required):
    repeated = [] if each_root is None else [Repeated(each_root, PARTS, instances)]
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
