"""Tests for the spec module: the skeleton of architecture.md section 1 per profile, published through the controller."""
import pytest

from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.skeleton import SkeletonService
from xarch.modules.spec.contract import Entry
from tests.fakes.settings import FakeSettings


def skeleton(*profile: str):
    return SpecController(SkeletonService(FakeSettings())).skeleton(*profile)


def test_top_level_lists_every_folder_parents_before_children():
    paths = [e.path for e in skeleton().top_level]
    assert paths == [("bootstrap",), ("bootstrap", "migrations"), ("kernel",), ("kernel", "logic"), ("modules",), ("platform",),
                     ("cli",), ("cli", "commands")]
    assert all(e.is_dir for e in skeleton().top_level)


def test_the_default_profile_is_cli():
    assert skeleton() == skeleton("cli")
    assert skeleton().entry_point == "cli"


def test_the_web_profile_has_web_with_routes_i18n_and_ui_instead_of_cli():
    paths = [e.path for e in skeleton("web").top_level]
    assert paths == [("bootstrap",), ("bootstrap", "migrations"), ("kernel",), ("kernel", "logic"), ("modules",), ("platform",),
                     ("web",), ("web", "routes"), ("web", "i18n"), ("web", "ui")]
    assert skeleton("web").entry_point == "web"


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_module_lists_every_part_with_files_marked(profile):
    assert skeleton(profile).module == (
        Entry(("contract",), True, True),
        Entry(("domain",), True, True),
        Entry(("application",), True, False),
        Entry(("application", "controller.py"), False, True),
        Entry(("application", "services"), True, True),
        Entry(("application", "logic"), True, True),
        Entry(("application", "ports"), True, True),
        Entry(("adapters",), True, True),
    )


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_kernel_holds_logic_and_every_module_holds_application_logic(profile):
    assert Entry(("kernel", "logic"), True, True) in skeleton(profile).top_level
    assert Entry(("application", "logic"), True, True) in skeleton(profile).module


def test_a_folder_with_children_is_not_a_leaf():
    bootstrap, migrations = skeleton().top_level[:2]
    assert not bootstrap.leaf and migrations.leaf


def test_the_profiles_are_listed():
    assert SpecController(SkeletonService(FakeSettings())).profiles() == ("cli", "web")
