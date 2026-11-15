"""The closed-tree guard on a hand-built profile: a Python file in no part and no folder of the layout is reported."""
from xarch.kernel.logic.placement import Target
from xarch.modules.rules.application.logic.closed_tree import ungoverned, violations
from xarch.modules.rules.domain.values import Profile

PROFILE = Profile(parts={"domain": ("modules", "*", "domain"), "entry": ("cli",),
                         "controller": ("modules", "*", "application", "controller.py")},
                  rules={"domain": (Target("domain", "own"),)},
                  folders=((), ("modules",), ("modules", "*"), ("modules", "*", "domain"), ("modules", "*", "application"),
                           ("cli",)),
                  closed_tree=True)


def paths(*written: str) -> list[tuple[str, ...]]:
    return [tuple(p.split("/")) for p in written]


def test_files_in_parts_and_package_files_of_the_layout_pass():
    assert violations(paths("__init__.py", "modules/__init__.py", "modules/docs/__init__.py",
                            "modules/docs/domain/doc.py", "modules/docs/domain/rules/x.py",
                            "modules/docs/application/__init__.py", "modules/docs/application/controller.py",
                            "cli/main.py"), PROFILE, "app") == []


def test_a_file_in_no_part_and_no_folder_of_the_layout_is_reported():
    assert [str(v) for v in violations(paths("main.py", "modules/docs/helpers.py",
                                             "modules/docs/application/helpers.py", "scripts/__init__.py"),
                                       PROFILE, "app")] == [
        f"app/{p}: lies in no part and no folder of the layout: move it into a part, or add its folder to the "
        "layout (closed-tree)"
        for p in ["main.py", "modules/docs/helpers.py", "modules/docs/application/helpers.py", "scripts/__init__.py"]]


def test_without_the_guard_nothing_is_reported():
    assert violations(paths("main.py"), Profile(PROFILE.parts, PROFILE.rules, PROFILE.folders), "app") == []


def test_a_file_outside_the_tree_names_its_rule_and_its_fix():
    found = violations(paths("main.py"), PROFILE, "app")[0]
    assert (found.rule, found.fix) == ("closed-tree", "move it into a part, or add its folder to the layout")


def test_the_ungoverned_files_are_listed_whether_the_guard_is_on_or_not():
    off = Profile(PROFILE.parts, PROFILE.rules, PROFILE.folders)
    written = paths("main.py", "modules/docs/domain/doc.py", "modules/docs/__init__.py", "scripts/run.py")
    assert ungoverned(written, off, "app") == ungoverned(written, PROFILE, "app") == ["app/main.py", "app/scripts/run.py"]


def test_a_package_file_of_a_folder_of_the_layout_below_an_instance_passes_but_a_module_beside_it_does_not():
    assert [v.file for v in violations(paths("modules/docs/application/__init__.py", "modules/docs/application/x.py"),
                                       PROFILE, "app")] == ["app/modules/docs/application/x.py"]
