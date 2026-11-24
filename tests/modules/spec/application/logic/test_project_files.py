"""The project files of an architecture: each written from its template, with the app folder's name filled in."""

import pytest

from tests.modules.spec.profiles import SOURCE, parsed
from xarch.modules.spec.application.logic.project_files import project_files, with_app
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.published import ProjectFile

PARTS = {"src/": {"role": "code"}}
"""A profile of one part, the folder src."""


def architecture(files: dict, parts: dict | None = None):
    document = {"name": "layered", "parts": parts or PARTS, "files": files}
    return parsed(document, missing={"preset"}, folders={"preset": ("x",)})


FILE_IN_SRC = {"src/": {"role": "code", "a.py": {"role": "code"}}}


def written(declared, contents, app="shop", folders=None):
    return list(project_files(declared, contents, app, SOURCE, folders or {}))


def test_each_file_is_its_template_with_the_app_folder_filled_in_in_the_order_declared():
    declared = architecture({"tests/a.py": {"from": "a.tpl"}, "b.txt": {"from": "b.tpl"}})
    texts = {"a.tpl": "ROOT / '{{app}}' and {{app}}\n", "b.tpl": "plain\n"}
    assert written(declared, texts) == [
        ProjectFile(("tests", "a.py"), "ROOT / 'shop' and shop\n"), ProjectFile(("b.txt",), "plain\n")]


def test_any_other_placeholder_is_written_as_it_stands():
    declared = architecture({"a.html": {"from": "a.tpl"}})
    assert written(declared, {"a.tpl": "{{ title }} {{tree}} {{app}}"}) == [
        ProjectFile(("a.html",), "{{ title }} {{tree}} shop")]


def test_an_architecture_without_files_yields_none():
    declared = parsed({"name": "layered", "parts": PARTS})
    assert written(declared, {}) == []


def test_a_file_inside_the_app_folder_is_written_there_when_the_skeleton_does_not_write_it():
    declared = architecture({"shop/extra.py": {"from": "a.tpl"}, "{{app}}/src/b.py": {"from": "a.tpl"}})
    assert [file.path for file in written(declared, {"a.tpl": ""})] == [("shop", "extra.py"), ("shop", "src", "b.py")]


@pytest.mark.parametrize("key, problem", [
    ("{{app}}/__init__.py", "'shop/__init__.py' is the package file the skeleton writes"),
    ("shop/src/__init__.py", "'shop/src/__init__.py' is the package file the skeleton writes"),
    ("{{app}}/src", "'shop/src' is a folder of the layout"),
    ("{{app}}/src/a.py/more.py", "'shop/src/a.py' is a file of the layout"),
    ("{{app}}/src/a.py", "'shop/src/a.py' is a file of the layout"),
    ("{{app}}", "'shop' is the app folder"),
])
def test_a_file_the_skeleton_writes_is_refused(key, problem):
    declared = architecture({key: {"from": "a.tpl"}}, FILE_IN_SRC)
    with pytest.raises(InvalidArchitecture) as caught:
        written(declared, {"a.tpl": ""})
    assert caught.value.problems == (f"layered.yaml: files.{key}: {problem}",)


def test_a_file_in_an_instance_folder_may_not_replace_what_a_new_instance_gets():
    declared = architecture({"{{app}}/mods/x/domain/__init__.py": {"from": "a.tpl"}},
                            {"mods/<mod>/domain/": {"role": "code"}})
    with pytest.raises(InvalidArchitecture) as caught:
        written(declared, {"a.tpl": ""})
    assert "is the package file the skeleton writes" in caught.value.problems[0]


def test_a_folder_entry_is_copied_with_its_relative_paths_below_a_target_in_the_app_folder():
    declared = architecture({"{{app}}/src/design/": {"from": "preset"}})
    contents = {"preset/tokens.css": b"a {{app}}", "preset/fonts/f.woff": b"\xff\x00"}
    assert written(declared, contents, folders={"preset": ("tokens.css", "fonts/f.woff")}) == [
        ProjectFile(("shop", "src", "design", "tokens.css"), b"a {{app}}"),
        ProjectFile(("shop", "src", "design", "fonts", "f.woff"), b"\xff\x00")]


def test_a_folder_entry_that_says_fill_has_its_text_filled():
    declared = architecture({"d/": {"from": "preset", "fill": True}})
    assert written(declared, {"preset/a.txt": b"for {{app}}"}, folders={"preset": ("a.txt",)}) == [
        ProjectFile(("d", "a.txt"), "for shop")]


def test_a_file_that_is_not_text_cannot_be_filled():
    declared = architecture({"d/": {"from": "preset", "fill": True}, "e.bin": {"from": "e.tpl"}})
    with pytest.raises(InvalidArchitecture) as caught:
        written(declared, {"preset/a.bin": b"\xff\xfe", "e.tpl": b"\xff"}, folders={"preset": ("a.bin",)})
    assert caught.value.problems == (
        "layered.yaml: files.d/: 'preset/a.bin' is not valid UTF-8 text: set `fill: false` to copy it unchanged",
        "layered.yaml: files.e.bin: 'e.tpl' is not valid UTF-8 text: set `fill: false` to copy it unchanged")


def test_a_file_entry_that_says_fill_false_is_copied_unchanged():
    declared = architecture({"a.txt": {"from": "a.tpl", "fill": False}})
    assert written(declared, {"a.tpl": b"{{app}}"}) == [ProjectFile(("a.txt",), b"{{app}}")]
    assert written(declared, {"a.tpl": "{{app}}"}) == [ProjectFile(("a.txt",), b"{{app}}")]


def test_two_entries_that_land_on_the_same_file_are_refused():
    declared = architecture({"shop/a.txt": {"from": "a.tpl"}, "{{app}}/a.txt": {"from": "a.tpl"}})
    with pytest.raises(InvalidArchitecture) as caught:
        written(declared, {"a.tpl": ""})
    assert caught.value.problems == ("layered.yaml: files.{{app}}/a.txt: 'shop/a.txt' is also written by "
                                     "files.shop/a.txt",)


def test_with_app_fills_only_the_app_placeholder():
    assert with_app("a {{app}} {{ x }}", "shop") == "a shop {{ x }}"


def test_a_file_may_be_pinned_so_check_reports_it_when_it_differs_from_what_init_writes():
    declared = architecture({"tests/a.py": {"from": "a.tpl", "pinned": True}, "b.txt": {"from": "b.tpl"}})
    assert [(file.path, file.pinned) for file in declared.files] == [(("tests", "a.py"), True), (("b.txt",), False)]


def test_pinned_is_true_or_false():
    with pytest.raises(InvalidArchitecture) as caught:
        architecture({"tests/a.py": {"from": "a.tpl", "pinned": "yes"}})
    assert caught.value.problems == ("layered.yaml: files.tests/a.py.pinned: must be true or false: whether `check` reports the "
                                     "file when it differs from what `init` writes",)
