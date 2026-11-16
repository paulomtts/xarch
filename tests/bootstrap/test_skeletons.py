"""The skeleton of architecture.md section 1 of each bundled profile, published through the wired spec controller."""
import pytest

from tests.bootstrap.project import bundled_profiles
from xarch.bootstrap.wiring import build_controllers
from xarch.modules.spec.contract import Entry


def skeleton(profile: str):
    return build_controllers().spec.skeleton(profile)


def test_top_level_lists_every_folder_parents_before_children():
    paths = [e.path for e in skeleton("cli").top_level]
    assert paths == [("modules",), ("platform",), ("cli",), ("cli", "commands"), ("bootstrap",), ("bootstrap", "migrations"),
                     ("kernel",), ("kernel", "logic")]
    assert all(e.is_dir for e in skeleton("cli").top_level)


def test_the_web_profile_has_web_with_routes_i18n_and_ui_instead_of_cli():
    paths = [e.path for e in skeleton("web").top_level]
    assert paths == [("modules",), ("platform",), ("web",), ("web", "routes"), ("web", "i18n"), ("web", "ui"),
                     ("bootstrap",), ("bootstrap", "migrations"), ("kernel",), ("kernel", "logic")]


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_module_lists_every_part_with_files_marked(profile):
    assert skeleton(profile).repeating[0].entries == (
        Entry(("domain",), True, True),
        Entry(("application",), True, False),
        Entry(("application", "logic"), True, True),
        Entry(("application", "ports"), True, True),
        Entry(("application", "services"), True, True),
        Entry(("application", "controller.py"), False, True),
        Entry(("adapters",), True, True),
        Entry(("contract",), True, True),
    )


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_kernel_holds_logic_and_every_module_holds_application_logic(profile):
    assert Entry(("kernel", "logic"), True, True) in skeleton(profile).top_level
    assert Entry(("application", "logic"), True, True) in skeleton(profile).repeating[0].entries


def test_a_folder_with_children_is_not_a_leaf():
    entries = {e.path: e for e in skeleton("cli").top_level}
    assert not entries[("bootstrap",)].leaf and entries[("bootstrap", "migrations")].leaf


def test_the_profiles_are_listed():
    assert bundled_profiles() == ("cli", "web")
