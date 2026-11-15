"""The project files of an architecture: each written from its template, with the app folder's name filled in."""

import pytest

from xarch.modules.spec.domain.architecture_file import parse_architecture
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.project_files import project_files, with_app


def layered() -> dict:
    return {"xarch": 1, "name": "layered", "layout": {"src": {}},
            "parts": {"src": {"path": "src", "role": "code"}}, "rules": {"src": ["src"]}}


def architecture(files: dict):
    return parse_architecture(layered() | {"files": files}, "layered.yaml", lambda relative: True)


def test_each_file_is_its_template_with_the_app_folder_filled_in_in_the_order_declared():
    declared = architecture({"tests/a.py": {"from": "a.tpl"}, "b.txt": {"from": "b.tpl"}})
    texts = {"a.tpl": "ROOT / '{{app}}' and {{app}}\n", "b.tpl": "plain\n"}
    assert list(project_files(declared, texts, "shop", "layered.yaml")) == [
        (("tests", "a.py"), "ROOT / 'shop' and shop\n"), (("b.txt",), "plain\n")]


def test_any_other_placeholder_is_written_as_it_stands():
    declared = architecture({"a.html": {"from": "a.tpl"}})
    assert list(project_files(declared, {"a.tpl": "{{ title }} {{tree}} {{app}}"}, "shop", "layered.yaml")) == [
        (("a.html",), "{{ title }} {{tree}} shop")]


def test_an_architecture_without_files_yields_none():
    declared = parse_architecture(layered(), "layered.yaml", lambda relative: True)
    assert list(project_files(declared, {}, "shop", "layered.yaml")) == []


@pytest.mark.parametrize("path", ["shop/extra.py", "shop"])
def test_a_file_inside_the_app_folder_is_refused(path):
    declared = architecture({path: {"from": "a.tpl"}})
    with pytest.raises(InvalidArchitecture) as caught:
        list(project_files(declared, {"a.tpl": ""}, "shop", "layered.yaml"))
    assert caught.value.problems == (f"layered.yaml: files.{path}: lies inside the app folder 'shop'",)


def test_with_app_fills_only_the_app_placeholder():
    assert with_app("a {{app}} {{ x }}", "shop") == "a shop {{ x }}"
