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
    """The Parts the import checker would derive from this file: the part named `entry` is the entry point."""
    root = architecture.module_root()
    assert root is not None
    depth = len(root) + 1                                    # below modules/<module>/
    in_module = [p.path[depth:] for p in architecture.parts.values() if p.in_module]
    outside = [p.path for p in architecture.parts.values() if not p.in_module]
    assert all(len(path) == 1 for path in outside)          # every part outside the modules is a top-level folder
    assert {path[0] for path in in_module if len(path) == 2} == {"application"}
    entry = architecture.parts["entry"].path[0]
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


def test_the_rules_are_the_rules_table(profile):
    loaded = {part: tuple(RuleTarget(t.part, t.scope, t.sub) for t in targets)
              for part, targets in load_architecture(profile).rules.items()}
    assert RULES["structure"] == ()                         # the package files: never a part of a file, never a target
    assert loaded == {part: targets for part, targets in RULES.items() if part != "structure"}


def test_the_parts_are_what_the_checker_derives(profile):
    assert parts_layout(load_architecture(profile)) == RulesSkeleton(build_spec()).parts(profile)


def test_a_part_is_named_for_its_folder_except_the_entry_point(profile):
    # place_of names a place by its folder (controller.py -> controller), and the entry point "entry"
    for part in load_architecture(profile).parts.values():
        expected = "entry" if part.path == (PROFILES[profile].entry_point,) else part.path[-1].removesuffix(".py")
        assert part.name == expected


def test_every_part_has_a_role_and_a_litmus_test(profile):
    for part in load_architecture(profile).parts.values():
        assert part.role and part.litmus, part.name
