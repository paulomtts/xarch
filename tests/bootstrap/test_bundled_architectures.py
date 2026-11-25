"""The architecture files bundled with xarch, cli and web: what every one of them promises."""
from importlib import resources
from pathlib import Path

import pytest

from tests.bootstrap.project import PURE, bundled_profiles
from xarch.bootstrap.wiring import load_architecture

PROFILE_NAMES = ["cli", "web"]
OWN = Path(__file__).parent.parent.parent / "architecture.yaml"
FILES = [OWN, *(Path(str(resources.files("xarch").joinpath("architectures", f"{name}.yaml")))
                for name in PROFILE_NAMES)]


@pytest.fixture(params=PROFILE_NAMES)
def profile(request):
    return request.param


def test_cli_and_web_are_bundled():
    assert bundled_profiles() == tuple(PROFILE_NAMES)
    for name in PROFILE_NAMES:
        assert resources.files("xarch").joinpath("architectures", f"{name}.yaml").is_file()


def test_the_modules_live_under_modules(profile):
    architecture = load_architecture(profile)
    assert architecture.name == profile
    assert [repeat.root for repeat in architecture.repeats] == [("modules",)]


def test_the_entry_point_is_the_part_marked_entry_and_is_the_profiles_folder(profile):
    architecture = load_architecture(profile)
    assert [part.name for part in architecture.parts.values() if part.entry] == [profile]
    assert architecture.entry is not None and architecture.entry.path == (profile,)


def test_a_part_is_named_for_its_folder_or_for_its_parent_and_its_folder_when_another_part_has_that_name(profile):
    parts = load_architecture(profile).parts.values()
    folders = [part.path[-1].removesuffix(".py") for part in parts]
    for part, folder in zip(parts, folders):
        assert part.name == (folder if folders.count(folder) == 1 or part.name == folder
                             else f"{part.path[-2]}-{folder}")


def test_every_part_has_a_role_and_a_litmus_test(profile):
    for part in load_architecture(profile).parts.values():
        assert part.role and part.litmus, part.name


def test_bootstrap_may_import_everything_and_kernel_nothing_but_itself(profile):
    rules = load_architecture(profile).rules
    assert [t.part for t in rules["bootstrap"]] == ["*"]
    assert rules["kernel"] == ()


def test_the_rendering_tier_tests_the_entry_point(profile):
    architecture = load_architecture(profile)
    rendering = next(tier for tier in architecture.tiers if tier.name == "rendering")
    assert architecture.entry is not None and rendering.subject[0].part == architecture.entry.name


def folders(tree: dict, above: tuple[str, ...] = ()) -> list[tuple[str, ...]]:
    """Every path of the layout tree, folders and files, as the docs tree lists them."""
    return [path for name, sub in tree.items()
            for path in [(*above, name), *(folders(sub, (*above, name)) if sub else [])]]


def test_every_folder_of_the_tree_has_a_note_but_the_modules_folders(profile):
    architecture = load_architecture(profile)
    noted = set(architecture.notes) | {part.path for part in architecture.parts.values()}
    unnoted = {path for path in folders(architecture.layout) if path not in noted}
    assert unnoted == {("modules",), ("modules", "*"), ("modules", "*", "application")}


def test_placement_lists_every_part_once(profile):
    architecture = load_architecture(profile)
    assert sorted(architecture.placement) == sorted(architecture.parts)


@pytest.mark.parametrize("location", [*PROFILE_NAMES, str(OWN)])
def test_published_is_pure_then_typing_any_and_pure_is_as_written(location):
    architecture = load_architecture(location)
    assert architecture.uses_never["domain"] == tuple(tuple(name.split(".")) for name in PURE)
    assert architecture.uses_never["contract"] == tuple(tuple(name.split(".")) for name in (*PURE, "typing.Any"))


@pytest.mark.parametrize("path", FILES, ids=lambda path: path.name)
def test_each_profile_writes_published_as_an_include_of_pure(path):
    assert path.read_text(encoding="utf-8").count("\n  published: [pure, typing.Any]\n") == 1


WEB_ORDER = ("domain", "logic", "ports", "services", "controller", "adapters", "contract", "platform", "web",
             "bootstrap", "kernel", "kernel-logic")


@pytest.mark.parametrize("source, order", [
    pytest.param("web", WEB_ORDER, id="web"),
    pytest.param("cli", tuple("cli" if part == "web" else part for part in WEB_ORDER), id="cli"),
    pytest.param(OWN, ("domain", "logic", "ports", "services", "controller", "adapters", "contract", "platform", "cli",
                       "reports", "main", "bootstrap", "profile-values", "kernel", "kernel-logic"), id="xarch"),
])
def test_the_placement_of_each_profile_is_its_tree_s_reading_order(source, order):
    architecture = load_architecture(source)
    assert architecture.placement == order == tuple(architecture.parts)
