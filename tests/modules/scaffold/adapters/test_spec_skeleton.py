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
from xarch.profile_values.language import CheckedLanguage


class SpecStandIn:
    """Answers as spec's controller does, the same under every profile, its project files filled in for the app."""

    def skeleton(self, profile: str) -> Skeleton:
        return Skeleton(
            top_level=(Entry(("kernel",), True, False), Entry(("kernel", "rules.py"), False, True)),
            repeating=(Repeating("module", ("modules",), (Entry(("domain",), True, True),)),
                       Repeating("plugin", ("app", "plugins"), (Entry(("manifest.py",), False, True),))),
            language=CheckedLanguage("Python", ".py", "__init__.py"), reserved=frozenset({"class"}))

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


def test_the_language_is_how_spec_names_it_the_file_it_has_stand_for_a_folder_and_its_reserved_words():
    assert skeleton().language("cli") == Language("Python", "__init__.py", frozenset({"class"}))
