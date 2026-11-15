"""A profile file in format 2: what only fills the docs (`docs`), the files `init` writes, the excluded folders and the
hints, each with the address it has in the file."""
import pytest

from tests.modules.spec.profiles_v2 import layered, parsed, problems
from xarch.kernel.violations import RULES
from xarch.modules.spec.domain.docs_template import fill
from xarch.modules.spec.domain.values import Doc, Example, Excluded, Naming, ProjectFile


def test_the_entry_point_is_the_part_docs_names():
    architecture = parsed(layered(docs={"entry": "api"}))
    assert architecture.entry is not None and architecture.entry.name == "api"
    assert [part.name for part in architecture.parts.values() if part.entry] == ["api"]
    assert parsed(layered()).entry is None


def test_the_docs_pages_are_files_written_from_templates_and_folders_with_a_note_and_a_bare_string_is_from():
    pages = {"statement.md": "docs/statement.md", "architecture.md": {"from": "web.md", "note": "this file"},
             "adrs/": {"note": "decisions"}, "adrs/0000.md": {"from": "docs/adr.md"}}
    assert parsed(layered(docs={"pages": pages})).docs == (
        Doc(("statement.md",), "docs/statement.md"), Doc(("architecture.md",), "web.md", "this file"),
        Doc(("adrs",), None, "decisions"), Doc(("adrs", "0000.md"), "docs/adr.md"))


def test_a_bad_docs_page_is_refused_with_its_address_under_pages():
    pages = {"a.md": 3, "b.md": {"from": "gone.md"}, "c/": {"from": "x"}, "d/": {"note": "empty"}, "e.md": {"note": "x"},
             "../f.md": "x"}
    assert problems(layered(docs={"pages": pages}), has_file=lambda relative: relative != "gone.md") == [
        "layered.yaml: docs.pages.a.md: must be a mapping such as {from: <file>, note: <text>}",
        "layered.yaml: docs.pages.b.md.from: no file 'gone.md' next to the architecture file",
        "layered.yaml: docs.pages.c/: a folder takes only `note`",
        "layered.yaml: docs.pages.e.md: missing `from`, the template file",
        "layered.yaml: docs.pages.../f.md: must be a path of plain names below the docs folder",
        "layered.yaml: docs.pages.d/: holds no file"]


def test_the_docs_keys_are_known_and_docs_is_a_mapping():
    assert problems(layered(docs={"colour": 1})) == [
        "layered.yaml: docs: unknown key 'colour': use entry, example_notes, examples, naming, pages"]
    assert problems(layered(docs=3)) == [
        "layered.yaml: docs: must be a mapping of {entry, pages, naming, examples, example_notes}"]
    assert problems(layered(docs={"pages": 3})) == [
        "layered.yaml: docs.pages: must be a mapping of paths to {from, note}, such as {statement.md: {from: "
        "docs/statement.md}}"]


@pytest.mark.parametrize("entry, expected", [
    pytest.param("repo", "layered.yaml: docs.entry: no part named 'repo'", id="no such part"),
    pytest.param(3, "layered.yaml: docs.entry: no part named 3", id="not a name"),
])
def test_the_entry_must_be_a_part(entry, expected):
    assert problems(layered(docs={"entry": entry})) == [expected]


def test_the_naming_table_is_docs_only_and_keeps_its_rows():
    rows = [{"kind": "service", "where": "service/", "pattern": "thing and `Service`", "example": ["XService"]}]
    assert parsed(layered(docs={"naming": rows})).naming == (
        Naming("service", ("service/",), "thing and `Service`", ("XService",)),)


def test_a_bad_naming_row_is_refused_with_its_address_under_docs():
    rows = [{"kind": "service", "where": [], "pattern": "x"}, "row"]
    assert problems(layered(docs={"naming": rows})) == [
        "layered.yaml: docs.naming[0]: missing `example`",
        "layered.yaml: docs.naming[0].where: must be a string or a list of strings",
        "layered.yaml: docs.naming[1]: must be a mapping with `kind`, `where`, `pattern` and `example`"]
    assert problems(layered(docs={"naming": 3})) == [
        "layered.yaml: docs.naming: must be a list of rows such as {kind, where, pattern, example}"]


def test_the_examples_are_the_folders_of_example_projects_and_every_file_below_them_is_one_named_by_its_path():
    folders = {"ex/shared": ("shared/text.py", "src/billing/store/repo.py"), "ex/web": ("src/billing/api/page.py",
               "tests/src/billing/api/test_page.py")}
    notes = {"src/billing/store/repo.py": "the only file that names sql"}
    examples = parsed(layered(docs={"examples": ["ex/shared", "ex/web"], "example_notes": notes}),
                      folder_files=folders.get).examples
    assert list(examples) == ["shared/text.py", "src/billing/store/repo.py", "src/billing/api/page.py",
                              "tests/src/billing/api/test_page.py"]
    assert examples["src/billing/store/repo.py"] == Example(
        "src/billing/store/repo.py", "store", ("src", "billing", "store", "repo.py"), "ex/shared/src/billing/store/repo.py",
        "the only file that names sql")
    assert [(e.part, e.file) for e in examples.values()][::2] == [
        ("shared", "ex/shared/shared/text.py"), ("api", "ex/web/src/billing/api/page.py")]
    assert examples["tests/src/billing/api/test_page.py"].part == ""


def test_a_bad_example_root_or_note_is_refused_with_its_address_under_docs():
    folders = {"a": ("x.py",), "b": ("x.py",), "empty": ()}
    docs = {"examples": ["a", "b", "gone", "empty", 3], "example_notes": {"x.py": "ok", "y.py": "no such file", "z": 1}}
    assert problems(layered(docs=docs), folder_files=folders.get) == [
        "layered.yaml: docs.examples[2]: no folder 'gone' holding a file next to the profile file",
        "layered.yaml: docs.examples[3]: no folder 'empty' holding a file next to the profile file",
        "layered.yaml: docs.examples[4]: must be a folder next to the profile file, such as examples/shared",
        "layered.yaml: docs.examples: 'x.py' is in both 'a' and 'b': an example is named by its path in its project",
        "layered.yaml: docs.example_notes.y.py: no file 'y.py' in any folder of docs.examples",
        "layered.yaml: docs.example_notes.z: no file 'z' in any folder of docs.examples"]


def test_the_examples_and_their_notes_must_have_the_shape_the_message_says():
    folders = {"a": ("x.py",)}
    assert problems(layered(docs={"examples": "a"}), folder_files=folders.get) == [
        "layered.yaml: docs.examples: must be a list of folders next to the profile file, each an example project, "
        "such as [examples/shared]"]
    assert problems(layered(docs={"example_notes": {"x.py": "n"}})) == [
        "layered.yaml: docs.example_notes.x.py: no file 'x.py' in any folder of docs.examples"]
    assert problems(layered(docs={"examples": ["a"], "example_notes": {"x.py": "a\nb"}}), folder_files=folders.get) == [
        "layered.yaml: docs.example_notes.x.py: must be one line of text"]
    assert problems(layered(docs={"examples": ["a"], "example_notes": ["x.py"]}), folder_files=folders.get) == [
        "layered.yaml: docs.example_notes: must be a mapping of paths in an example project to one line of text"]


def test_files_are_written_from_templates_and_a_bare_string_is_from():
    files = {"AGENTS.md": "agents.md", "tests/test_rules.py": {"from": "guard.py", "pinned": True},
             "{{app}}/web/ui/": {"from": "ui"}}
    architecture = parsed(layered(files=files), has_file=lambda relative: relative in {"agents.md", "guard.py"},
                          folder_files=lambda relative: ("a.py",) if relative == "ui" else None)
    assert architecture.files == (
        ProjectFile(("AGENTS.md",), "agents.md"), ProjectFile(("tests", "test_rules.py"), "guard.py", True),
        ProjectFile(("{{app}}", "web", "ui"), "ui", False, True, False))


def test_a_bad_file_is_refused_with_its_address_and_what_to_write():
    files = {"a.md": 3, "b.md": {"from": "gone.md", "colour": 1}, "c.md": {"from": "x.md", "pinned": "yes"}}
    assert problems(layered(files=files), has_file=lambda relative: relative == "x.md") == [
        "layered.yaml: files.a.md: must be a mapping such as {from: <file>}",
        "layered.yaml: files.b.md: unknown key 'colour': use fill, from, pinned",
        "layered.yaml: files.b.md.from: no file 'gone.md' next to the architecture file",
        "layered.yaml: files.c.md.pinned: must be true or false: whether `check` reports the file when it differs "
        "from what `init` writes"]


def test_a_file_that_lies_where_a_docs_page_is_written_is_refused_naming_the_page():
    document = layered(docs={"pages": {"statement.md": "s.md"}}, files={"docs/project/statement.md": "s.md"})
    assert problems(document) == [
        "layered.yaml: files.docs/project/statement.md: collides with docs.pages.statement.md, written to "
        "docs/project/statement.md"]


def test_excluded_folders_and_hints_are_as_they_were():
    architecture = parsed(layered(excluded={"vendor": "copied code"}, hints={"rules": "see the docs"}))
    assert architecture.excluded == (Excluded(("vendor",), "copied code"),)
    assert architecture.hints == {"rules": "see the docs"}
    assert problems(layered(excluded={"shared": "no", "../x": "no"}, hints={"nope": "x"})) == [
        "layered.yaml: excluded.shared: 'shared' is a folder of the layout: it is source, not excluded",
        "layered.yaml: excluded: '../x' is not a folder below the app, such as vendor/generated",
        f"layered.yaml: hints.nope: unknown rule id 'nope': use {', '.join(sorted(RULES))}"]


def test_the_guards_list_of_the_docs_says_in_words_that_a_part_may_import_any_outside_package():
    document = layered()
    document["parts"]["store"]["libraries"] = ["sqlmodel"]
    document["parts"]["shared"]["libraries"] = "everything"
    text = fill("{{guards}}", parsed(document), "layered.md")
    assert "`shared/`: any outside package" in text and "`shared/`: *" not in text
