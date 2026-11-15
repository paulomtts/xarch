"""Loading a profile file of format 2: what only fills the docs and the files `init` writes, the layers, the entry,
the way a part is shown, and every problem reported with the file's name, never a traceback."""
import pytest

from tests.modules.spec.profiles_v2 import layered, parsed, problems
from xarch.modules.spec.domain.values import Doc, ProjectFile


def test_a_document_that_is_not_a_mapping_stops_at_once():
    assert problems(["xarch", 2]) == ["layered.yaml: must be a mapping of keys, starting with `xarch: 2`"]


@pytest.mark.parametrize("layers, expected", [
    pytest.param([], ["layers: must be a mapping of names to lists of parts, from the inside out"],
                 id="layers that are not a mapping are refused"),
    pytest.param({"a b": ["api"]}, ["layers: 'a b' is not a name: use letters, digits, '_' and '-'"],
                 id="a layer name that is no name is refused"),
    pytest.param({"inside": ["api", "service", "store"], "again": ["store", "repo"], "wrong": ["api"], "empty": []},
                 ["layers.inside: 'api' imports 'service', which is outward of it",
                  "layers.inside: 'service' imports 'store', which is outward of it",
                  "layers.again: part 'store' is already in layer 'inside'",
                  "layers.again: no part named 'repo'",
                  "layers.wrong: part 'api' is already in layer 'inside'",
                  "layers.empty: must be a list of parts, from the inside out"],
                 id="a part in two layers, a part that does not exist, an empty layer and an import outward are all reported"),
])
def test_a_bad_layer_is_refused(layers, expected):
    assert problems(layered(layers=layers)) == [f"layered.yaml: {line}" for line in expected]


def test_the_example_of_a_part_nested_in_another_part_belongs_to_the_nested_part():
    document = layered(docs={"examples": ["ex"]})
    document["parts"]["sql"] = {"path": "src/<module>/store/sql", "role": "queries"}
    files = {"ex": ("src/b/store/sql/q.py", "src/b/store/repo.py")}
    examples = parsed(document, folder_files=files.get).examples
    assert {path: example.part for path, example in examples.items()} == {
        "src/b/store/sql/q.py": "sql", "src/b/store/repo.py": "store"}


def test_the_docs_pages_keep_their_order_and_notes_below_nested_folders():
    document = layered(docs={"pages": {
        "statement.md": {"from": "docs/statement.md", "note": "what and why"},
        "adrs/": {"note": "decisions"},
        "adrs/0000.md": {"from": "docs/adr.md"},
        "artifacts/guards/_template.md": {"from": "docs/guard.md"},
    }})
    assert parsed(document).docs == (
        Doc(("statement.md",), "docs/statement.md", "what and why"),
        Doc(("adrs",), None, "decisions"),
        Doc(("adrs", "0000.md"), "docs/adr.md"),
        Doc(("artifacts", "guards", "_template.md"), "docs/guard.md"),
    )


@pytest.mark.parametrize("pages, expected", [
    pytest.param([], ["docs.pages: must be a mapping of paths to {from, note}, such as {statement.md: "
                      "{from: docs/statement.md}}"], id="pages that are not a mapping are refused"),
    pytest.param({"a.md": {}}, ["docs.pages.a.md: missing `from`, the template file"], id="a page without a template"),
    pytest.param({"a.md": {"from": 3}}, ["docs.pages.a.md.from: must be a file name"],
                 id="a template that is no file name"),
    pytest.param({"a.md": {"from": "x.md", "extra": 1}}, ["docs.pages.a.md: unknown key 'extra': use from, note"],
                 id="an unknown key of a page"),
    pytest.param({"a.md": {"from": "x.md", "note": ["no"]}}, ["docs.pages.a.md.note: must be one line of text"],
                 id="a note that is no text"),
    pytest.param({"d/": {"from": "x.md"}}, ["docs.pages.d/: a folder takes only `note`"],
                 id="a folder with a template"),
    pytest.param({"d/": {"note": "n"}}, ["docs.pages.d/: holds no file"], id="a folder holding no file"),
    pytest.param({"../a.md": {"from": "x.md"}},
                 ["docs.pages.../a.md: must be a path of plain names below the docs folder"], id="a path climbing out"),
    pytest.param({"/a.md": {"from": "x.md"}},
                 ["docs.pages./a.md: must be a path of plain names below the docs folder"],
                 id="a path starting with a slash"),
    pytest.param({"a//b.md": {"from": "x.md"}},
                 ["docs.pages.a//b.md: must be a path of plain names below the docs folder"],
                 id="a path with an empty step"),
    pytest.param({"a.md": {"from": "x.md"}, "a.md/b.md": {"from": "x.md"}},
                 ["docs.pages.a.md/b.md: 'a.md' is a file, not a folder"], id="a page below a file"),
    pytest.param({"g/a.md": {"from": "x.md"}, "g/a.md/b.md": {"from": "x.md"}},
                 ["docs.pages.g/a.md/b.md: 'g/a.md' is a file, not a folder"], id="a page below a nested file"),
    pytest.param({"a.md": {"from": "nowhere.md"}},
                 ["docs.pages.a.md.from: no file 'nowhere.md' next to the architecture file"],
                 id="a template that does not exist"),
])
def test_a_bad_docs_page_is_refused_saying_what_to_write(pages, expected):
    assert problems(layered(docs={"pages": pages}), lambda relative: relative == "x.md") == [
        f"layered.yaml: {line}" for line in expected]


def test_files_keep_their_order_and_name_their_template():
    document = layered(files={
        "tests/architecture/test_rules.py": {"from": "guard.py"},
        "Makefile": {"from": "make.txt"},
    })
    assert parsed(document).files == (
        ProjectFile(("tests", "architecture", "test_rules.py"), "guard.py"),
        ProjectFile(("Makefile",), "make.txt"),
    )


@pytest.mark.parametrize("files, expected", [
    pytest.param([], ["files: must be a mapping of paths to {from}, such as {tests/rules.py: {from: guard.py}}"],
                 id="files that are not a mapping are refused"),
    pytest.param({"a.py": {}}, ["files.a.py: missing `from`, the template file"], id="a file without a template"),
    pytest.param({"a.py": {"from": 3}}, ["files.a.py.from: must be a file name"], id="a template that is no file name"),
    pytest.param({"a.py": {"from": "x.py", "note": "n"}}, ["files.a.py: unknown key 'note': use fill, from, pinned"],
                 id="an unknown key of a file"),
    pytest.param({"a.py": {"from": "nowhere.py"}},
                 ["files.a.py.from: no file 'nowhere.py' next to the architecture file"],
                 id="a template that does not exist"),
    pytest.param({"../a.py": {"from": "x.py"}},
                 ["files.../a.py: must be a path of plain names below the project root"], id="a path climbing out"),
    pytest.param({"/a.py": {"from": "x.py"}},
                 ["files./a.py: must be a path of plain names below the project root"],
                 id="a path starting with a slash"),
    pytest.param({"a//b.py": {"from": "x.py"}},
                 ["files.a//b.py: must be a path of plain names below the project root"], id="a path with an empty step"),
    pytest.param({"/": {"from": "x.py"}}, ["files./: must be a path of plain names below the project root"],
                 id="a path that is only a slash"),
    pytest.param({3: {"from": "x.py"}}, ["files.3: must be a path of plain names below the project root"],
                 id="a path that is no text"),
    pytest.param({"docs/project/a.md": {"from": "x.py"}, "docs/project/a.md/b": {"from": "x.py"}},
                 ["files.docs/project/a.md/b: 'docs/project/a.md' is a file, not a folder"], id="a file below a file"),
])
def test_bad_files_are_refused_saying_what_to_write(files, expected):
    assert problems(layered(files=files), lambda relative: relative == "x.py") == [
        f"layered.yaml: {line}" for line in expected]


def folders(relative):
    return {"preset": ("a.txt", "sub/b.bin"), "empty": ()}.get(relative.rstrip("/"))


def test_a_key_ending_in_a_slash_is_a_folder_entry_which_is_not_filled_unless_it_says_so():
    files = {"{{app}}/web/ui/design/": {"from": "preset/"}, "docs/": {"from": "preset", "fill": True},
             "x.txt": {"from": "x.py"}, "y.txt": {"from": "x.py", "fill": False}}
    found = parsed(layered(files=files), lambda relative: relative == "x.py", folder_files=folders).files
    assert found == (ProjectFile(("{{app}}", "web", "ui", "design"), "preset", False, True, False),
                     ProjectFile(("docs",), "preset", False, True, True),
                     ProjectFile(("x.txt",), "x.py", False, False, True),
                     ProjectFile(("y.txt",), "x.py", False, False, False))


@pytest.mark.parametrize("files, expected", [
    pytest.param({"d/": {}}, ["files.d/: missing `from`, the folder"], id="a folder entry without a folder"),
    pytest.param({"d/": {"from": 3}}, ["files.d/.from: must be a folder name"], id="a folder that is no name"),
    pytest.param({"d/": {"from": "x.py"}},
                 ["files.d/.from: 'x.py' is a file, not a folder: a folder entry copies a folder"],
                 id="a folder entry copying a file"),
    pytest.param({"d/": {"from": "nowhere"}}, ["files.d/.from: no folder 'nowhere' next to the architecture file"],
                 id="a folder that does not exist"),
    pytest.param({"d/": {"from": "empty"}}, ["files.d/.from: the folder 'empty' holds no file"],
                 id="a folder holding no file"),
    pytest.param({"d/": {"from": "preset", "pinned": True}},
                 ["files.d/.pinned: a folder entry cannot be pinned: a project edits what it copies"],
                 id="a pinned folder entry"),
    pytest.param({"d": {"from": "preset"}},
                 ["files.d.from: 'preset' is a folder, not a file: end the key with / to copy a folder"],
                 id="a file entry copying a folder"),
    pytest.param({"d/": {"from": "preset", "fill": "no"}},
                 ["files.d/.fill: must be true or false: whether `{{app}}` is filled in"],
                 id="a fill that is no boolean"),
    pytest.param({"d/": {"from": "preset"}, "d/a.txt": {"from": "x.py"}},
                 ["files.d/a.txt: lies inside the folder entry 'd/'"], id="a file inside a folder entry"),
    pytest.param({"d/": {"from": "preset"}, "d/e/": {"from": "preset"}},
                 ["files.d/e/: lies inside the folder entry 'd/'"], id="a folder entry inside a folder entry"),
    pytest.param({"d/e/": {"from": "preset"}, "d/": {"from": "preset"}},
                 ["files.d/e/: lies inside the folder entry 'd/'"], id="a folder entry that holds an earlier one"),
    pytest.param({"d/": {"from": "preset"}, "d": {"from": "x.py"}}, ["files.d: is also a folder entry"],
                 id="a file entry named like a folder entry"),
    pytest.param({"d/{{other}}/": {"from": "preset"}},
                 ["files.d/{{other}}/: must be a path of plain names below the project root; the only placeholder "
                  "is {{app}}"], id="a placeholder that is not the app"),
    pytest.param({"docs/project/": {"from": "preset"}},
                 ["files.docs/project/: collides with docs.pages.statement.md, written to "
                  "docs/project/statement.md"], id="a folder entry over a docs page"),
])
def test_bad_folder_entries_are_refused_saying_what_to_write(files, expected):
    document = layered(docs={"pages": {"statement.md": {"from": "x.py"}}}, files=files)
    assert problems(document, lambda relative: relative == "x.py", folder_files=folders) == [
        f"layered.yaml: {line}" for line in expected]


def test_a_file_colliding_with_a_page_in_a_folder_names_the_docs_path():
    document = layered(docs={"pages": {"guides/a.md": {"from": "x.py"}}},
                       files={"docs/project/guides/a.md": {"from": "x.py"}})
    assert problems(document) == ["layered.yaml: files.docs/project/guides/a.md: collides with "
                                  "docs.pages.guides/a.md, written to docs/project/guides/a.md"]


@pytest.mark.parametrize("path", [
    pytest.param("docs/project/statement.md", id="the page itself"),
    pytest.param("docs/project/statement.md/more", id="a path below the page"),
    pytest.param("docs/project", id="the folder that holds the pages"),
])
def test_a_file_may_not_collide_with_a_docs_page(path):
    document = layered(docs={"pages": {"statement.md": {"from": "x.py"}}}, files={path: {"from": "x.py"}})
    assert problems(document) == [
        f"layered.yaml: files.{path}: collides with docs.pages.statement.md, written to docs/project/statement.md"]


def test_a_part_is_shown_as_the_docs_show_it_below_its_instance_and_ending_in_a_slash_for_a_folder():
    document = layered()
    document["parts"] = {
        "core": {"path": "src/<feature>/core", "role": "r"}, "main": {"path": "src/<feature>/main.py", "role": "r"},
        "src": {"path": "src", "role": "r"}, "entry": {"path": "__main__.py", "role": "r"}}
    architecture = parsed(document)
    assert {name: architecture.shown(part) for name, part in architecture.parts.items()} == {
        "core": "core/", "main": "main.py", "src": "src/", "entry": "__main__.py"}
