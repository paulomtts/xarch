"""The architecture files bundled with xarch, cli and web: what every one of them promises."""
from importlib import resources

import pytest

from tests.bootstrap.project import bundled_profiles
from xarch.bootstrap.wiring import load_architecture

PROFILE_NAMES = ["cli", "web"]


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


def test_a_part_is_named_for_its_folder(profile):
    for part in load_architecture(profile).parts.values():
        assert part.name == part.path[-1].removesuffix(".py")


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
