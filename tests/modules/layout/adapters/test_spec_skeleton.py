"""Layout's Skeleton read from spec's contract: the folders and files of the top level apart, and what every instance
of a repeating folder holds, as its leaves."""
from xarch.modules.layout.adapters.spec_skeleton import SpecSkeleton
from xarch.modules.spec.contract import Entry, Repeating, Skeleton

SKELETON = Skeleton(
    top_level=(Entry(("kernel",), True, True), Entry(("modules",), True, True), Entry(("__main__.py",), False, True)),
    repeating=(Repeating("module", ("modules",), (Entry(("domain",), True, True), Entry(("application",), True, False),
                                                  Entry(("application", "controller.py"), False, True))),),
    entry_point="")


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
