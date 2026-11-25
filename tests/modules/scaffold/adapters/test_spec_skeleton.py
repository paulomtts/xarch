"""SpecSkeleton: spec's skeleton, docs and project files as the plain tuples scaffold's Skeleton port speaks."""
import pytest

from xarch.modules.scaffold.adapters.spec_skeleton import SpecSkeleton
from xarch.modules.scaffold.domain.errors import ProfileUnusable
from xarch.modules.scaffold.domain.values import Language
from xarch.modules.spec.contract import (
    DocFile,
    Docs,
    Entry,
    FilesResult,
    ProfileRefused,
    ProjectFile,
    ProjectFiles,
    Repeating,
    Skeleton,
)


class SpecStandIn:
    """Answers as spec's controller does, the same under every profile, its project files filled in for the app."""

    def skeleton(self, profile: str) -> Skeleton:
        return Skeleton(
            top_level=(Entry(("kernel",), True, False), Entry(("kernel", "rules.py"), False, True)),
            repeating=(Repeating("module", ("modules",), (Entry(("domain",), True, True),)),
                       Repeating("plugin", ("app", "plugins"), (Entry(("manifest.py",), False, True),))),
            title="Python", package_file="__init__.py", private="_", reserved=frozenset({"class"}), names=r"\w+")

    def docs(self, profile: str) -> Docs:
        return Docs(("docs", "project"), (DocFile(("statement.md",), "# statement\n"),
                                          DocFile(("adrs", "0000-template.md"), "# adr\n")))

    def files(self, profile: str, app: str, presets: bool = True) -> FilesResult:
        if profile == "broken":
            return ProfileRefused("cli: files.x: no such template")
        return ProjectFiles((ProjectFile(("Makefile",), f"all: {app}\n"), ProjectFile((app, "logo.woff"), b"\xff\x00")))


def skeleton() -> SpecSkeleton:
    return SpecSkeleton(SpecStandIn())


def test_top_level_is_each_entry_as_its_path_and_whether_it_is_a_folder():
    assert skeleton().top_level("cli") == [(("kernel",), True), (("kernel", "rules.py"), False)]


def test_kinds_are_each_repeating_folder_by_its_word_with_its_root_and_entries():
    assert skeleton().kinds("cli") == {"module": (("modules",), [(("domain",), True)]),
                                       "plugin": (("app", "plugins"), [(("manifest.py",), False)])}


def test_docs_are_placed_below_the_docs_root_with_their_template():
    assert skeleton().docs("cli") == [(("docs", "project", "statement.md"), "# statement\n"),
                                      (("docs", "project", "adrs", "0000-template.md"), "# adr\n")]


def test_files_are_the_project_files_of_the_app_with_their_content_as_it_is():
    assert skeleton().files("cli", "shop") == [(("Makefile",), "all: shop\n"), (("shop", "logo.woff"), b"\xff\x00")]


def test_files_spec_refuses_are_refused_with_its_reason():
    with pytest.raises(ProfileUnusable, match="no such template"):
        skeleton().files("broken", "shop")


def test_the_language_is_how_spec_names_it_the_file_it_has_stand_for_a_folder_its_reserved_words_and_names():
    assert skeleton().language("cli") == Language("Python", "__init__.py", frozenset({"class"}), r"\w+", "_")


class SparseStandIn(SpecStandIn):
    """A skeleton with an optional part at the top level, holding a folder, and an optional file in each instance."""

    def skeleton(self, profile: str) -> Skeleton:
        return Skeleton(
            top_level=(Entry(("kernel",), True, True), Entry(("api",), True, False, True),
                       Entry(("api", "v1"), True, True, when=("api",))),
            repeating=(Repeating("module", ("modules",), (Entry(("domain",), True, True),
                                                          Entry(("config.py",), False, True, True))),))


def test_an_optional_part_and_what_it_holds_are_not_built():
    found = SpecSkeleton(SparseStandIn())
    assert found.top_level("cli") == [(("kernel",), True)]
    assert found.kinds("cli") == {"module": (("modules",), [(("domain",), True)])}
