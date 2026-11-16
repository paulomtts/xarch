"""The shape of a profile in format 1 as the migration reads it, on hand-made documents."""
import pytest

from xarch.modules.spec.application.logic.profile_v1 import read_v1
from xarch.modules.spec.domain.errors import InvalidArchitecture

OLD = {"xarch": 1, "name": "small", "layout": {"core": {}, "src": {"each": {"api": {}}, "singular": "module"},
                                                 "main.py": "file"},
       "parts": {"core": {"path": "core", "role": "the rules"}}, "notes": {"core": "the rules"}, "colour": "blue"}


def test_the_layout_is_a_tree_with_the_repeating_folder_as_a_star_and_a_file_as_none():
    old = read_v1(OLD, "small.yaml")
    assert (old.name, old.layout, old.singular) == ("small", {"core": {}, "src": {"*": {"api": {}}}, "main.py": None},
                                                    "module")


def test_the_parts_and_notes_are_read_and_a_key_format_1_does_not_have_is_kept_aside():
    old = read_v1(OLD, "small.yaml")
    assert (old.parts["core"].path, old.parts["core"].role, old.notes, old.extra) == (
        ("core",), "the rules", {("core",): "the rules"}, ("colour",))


@pytest.mark.parametrize("document, problem", [
    pytest.param({"xarch": 1}, "missing `layout`", id="no layout"),
    pytest.param({"layout": {"src": {"each": {}}}, "parts": {}},
                 "layout.src: `each` needs `singular` beside it, one word naming an instance", id="a repeating folder with no word"),
])
def test_what_the_conversion_cannot_rely_on_is_refused(document, problem):
    with pytest.raises(InvalidArchitecture) as caught:
        read_v1(document, "small.yaml")
    assert f"small.yaml: {problem}" in caught.value.problems
