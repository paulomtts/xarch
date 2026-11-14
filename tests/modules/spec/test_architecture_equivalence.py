"""The bundled architecture files describe exactly the architecture that is hard-coded today, for both profiles.

Three things must match: the folder tree (skeleton.py), the dependency rules (rules_table.RULES) and the Parts
layout the import checker derives from the skeleton (rules' SpecSkeleton adapter).
"""
from importlib import resources

import pytest

from xarch.bootstrap.wiring import build_spec, load_architecture
from xarch.modules.rules.adapters.spec_skeleton import SpecSkeleton as RulesSkeleton
from xarch.modules.rules.domain.rules_table import RULES, Target as RuleTarget
from xarch.modules.rules.domain.values import Parts
from xarch.modules.spec.domain.skeleton import MODULE_TREE, PROFILES, top_level_tree, walk
from xarch.modules.spec.domain.values import Architecture

PROFILE_NAMES = sorted(PROFILES)


def parts_layout(architecture: Architecture) -> Parts:
    """The Parts the import checker would derive from this file: the part marked `entry: true` is the entry point."""
    root = architecture.module_root()
    assert root is not None
    depth = len(root) + 1                                    # below modules/<module>/
    in_module = [p.path[depth:] for p in architecture.parts.values() if p.in_module]
    outside = [p.path for p in architecture.parts.values() if not p.in_module]
    assert all(len(path) == 1 for path in outside)          # every part outside the modules is a top-level folder
    assert {path[0] for path in in_module if len(path) == 2} == {"application"}
    assert architecture.entry is not None
    entry = architecture.entry.path[0]
    return Parts(top_level=frozenset(path[0] for path in outside) - {entry},
                 module_folders=frozenset(path[0] for path in in_module if len(path) == 1),
                 application_parts=frozenset(path[1].removesuffix(".py") for path in in_module if len(path) == 2),
                 entry_point=entry)


@pytest.fixture(params=PROFILE_NAMES)
def profile(request):
    return request.param


def test_cli_and_web_are_bundled():
    assert sorted(PROFILES) == ["cli", "web"]
    for name in PROFILES:
        assert resources.files("xarch").joinpath("architectures", f"{name}.yaml").is_file()


def test_the_layout_is_the_skeleton(profile):
    architecture = load_architecture(profile)
    assert architecture.name == profile
    assert architecture.top_level_tree() == top_level_tree(profile)
    assert architecture.module_tree() == MODULE_TREE
    assert architecture.module_root() == ("modules",)


def test_the_layout_keeps_the_skeletons_order(profile):
    architecture = load_architecture(profile)
    assert list(walk(architecture.top_level_tree())) == list(walk(top_level_tree(profile)))
    assert list(walk(architecture.module_tree())) == list(walk(MODULE_TREE))


def as_checker_names(architecture: Architecture, part: str) -> str:
    """rules_table names the entry point "entry"; the file names it as it likes and marks it `entry: true`."""
    return "entry" if architecture.entry is not None and part == architecture.entry.name else part


def test_the_rules_are_the_rules_table(profile):
    architecture = load_architecture(profile)
    loaded = {as_checker_names(architecture, part):
              frozenset(RuleTarget(as_checker_names(architecture, t.part), t.scope, t.sub) for t in targets)
              for part, targets in architecture.rules.items()}
    assert RULES["structure"] == ()                         # the package files: never a part of a file, never a target
    # the same targets per part; the file orders them as the docs' table lists them, which the checker ignores
    assert loaded == {part: frozenset(targets) for part, targets in RULES.items() if part != "structure"}


def test_the_parts_are_what_the_checker_derives(profile):
    assert parts_layout(load_architecture(profile)) == RulesSkeleton(build_spec()).parts(profile)


def test_the_entry_point_is_the_part_marked_entry_and_drives_the_profiles_folder(profile):
    architecture = load_architecture(profile)
    assert [part.name for part in architecture.parts.values() if part.entry] == [PROFILES[profile].entry_point]
    assert architecture.entry is not None and architecture.entry.path == (PROFILES[profile].entry_point,)


def test_a_part_is_named_for_its_folder(profile):
    # place_of names a place by its folder (controller.py -> controller); the entry point too, now it is marked
    for part in load_architecture(profile).parts.values():
        assert part.name == part.path[-1].removesuffix(".py")


def test_every_part_has_a_role_and_a_litmus_test(profile):
    for part in load_architecture(profile).parts.values():
        assert part.role and part.litmus, part.name


def test_only_the_entry_point_has_a_driver(profile):
    for part in load_architecture(profile).parts.values():
        assert bool(part.driver_proves) == bool(part.driver_test) == part.entry, part.name


def test_every_folder_of_the_tree_has_a_note_but_the_modules_folders(profile):
    architecture = load_architecture(profile)
    noted = set(architecture.notes) | {part.path for part in architecture.parts.values()}
    unnoted = {path for path, _, _ in walk(architecture.layout) if path not in noted}
    assert unnoted == {("modules",), ("modules", "*"), ("modules", "*", "application")}


def test_placement_lists_every_part_once(profile):
    architecture = load_architecture(profile)
    assert sorted(architecture.placement) == sorted(architecture.parts)
