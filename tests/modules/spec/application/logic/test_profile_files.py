"""The files a profile points to: its templates, init files (a folder as every file under it) and examples."""
from xarch.modules.spec.application.logic.profile_files import pointed_files
from xarch.modules.spec.domain.values import Architecture, Doc, Example, FileEntry

LISTING = {"presets": ("a.txt", "deep/b.txt", "__pycache__/c.pyc")}


def architecture() -> Architecture:
    return Architecture(
        "mine", {}, {}, {},
        docs=(Doc(("statement.md",), "docs/statement.md"), Doc(("adrs",), None), Doc(("again.md",), "docs/statement.md")),
        examples={"src/x.py": Example("src/x.py", "", ("src", "x.py"), "examples/src/x.py")},
        files=(FileEntry(("AGENTS.md",), "agents.md"), FileEntry(("tests",), "presets", folder=True)))


def test_every_template_init_file_folder_entry_and_example_is_listed_once_in_the_order_the_profile_names_them():
    assert pointed_files(architecture(), LISTING) == (
        "docs/statement.md", "agents.md", "presets/a.txt", "presets/deep/b.txt", "examples/src/x.py")


def test_a_profile_that_points_to_nothing_lists_nothing():
    assert pointed_files(Architecture("mine", {}, {}, {}), {}) == ()
