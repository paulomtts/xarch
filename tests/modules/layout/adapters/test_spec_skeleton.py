"""Layout's Skeleton read from spec's contract: the folders and files of the top level apart, and what every instance
of a repeating folder holds, as its leaves; and how the language names a folder."""
from dataclasses import replace

from xarch.modules.layout.adapters.spec_skeleton import SpecSkeleton
from xarch.modules.layout.domain.structure import Beside, Naming
from xarch.modules.spec.contract import Entry, Repeating, Skeleton

SKELETON = Skeleton(
    top_level=(Entry(("kernel",), True, True), Entry(("modules",), True, True), Entry(("__main__.py",), False, True)),
    repeating=(Repeating("module", ("modules",), (Entry(("domain",), True, True), Entry(("application",), True, False),
                                                  Entry(("application", "controller.py"), False, True))),),
    title="Python", package_file="__init__.py", private="_", reserved=frozenset({"class"}), names=r"\w+")


class Spec:
    """Spec's controller as layout's adapter uses it: the skeleton of the profile asked for."""

    def skeleton(self, profile: str) -> Skeleton:
        return SKELETON


def test_the_top_level_is_split_into_folders_and_files():
    skeleton = SpecSkeleton(Spec())
    assert skeleton.top_level("cli") == [("kernel",), ("modules",)]
    assert skeleton.top_level_files("cli") == [("__main__.py",)]


def test_each_repeating_folder_is_named_by_its_root_and_holds_its_leaves():
    skeleton = SpecSkeleton(Spec())
    assert skeleton.each_roots("cli") == [("modules",)]
    assert skeleton.each_parts("cli", ("modules",)) == [(("domain",), True), (("application", "controller.py"), False)]


def test_the_naming_is_what_a_name_may_be_and_how_a_private_one_starts():
    assert SpecSkeleton(Spec()).naming("cli") == Naming(r"\w+", "_")


def test_without_beside_there_is_no_beside_and_with_it_the_test_files_and_the_kept_folders():
    assert SpecSkeleton(Spec()).beside("cli") is None
    near = replace(SKELETON, beside=True, test_files=("test_*.py",), kept=(("architecture",), ("fakes",)))

    class Near:
        def skeleton(self, profile: str) -> Skeleton:
            return near

    assert SpecSkeleton(Near()).beside("cli") == Beside(("test_*.py",), (("architecture",), ("fakes",)))
