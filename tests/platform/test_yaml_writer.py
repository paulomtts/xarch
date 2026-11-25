"""Plain values written as YAML: block style, the shortest safe form of each scalar, and a literal or folded block for
a long text, so that the file reads as one written by hand."""
import pytest
import yaml

from xarch.platform.yaml_writer import YamlWriter


@pytest.mark.parametrize("document, text", [
    pytest.param({"a": 1, "b": "x", "c": True, "d": None}, "a: 1\nb: x\nc: true\nd: null\n",
                 id="a scalar is written plain"),
    pytest.param({"p": "modules/<module>/domain", "q": "domain@own/values"}, "p: modules/<module>/domain\nq: domain@own/values\n",
                 id="a path or a target stays plain"),
    pytest.param({"a": "*", "b": "true", "c": "12", "d": "a: b", "e": "x #y", "f": "", "g": " x", "h": "- x", "i": "{{app}}"},
                 'a: "*"\nb: "true"\nc: "12"\nd: "a: b"\ne: "x #y"\nf: ""\ng: " x"\nh: "- x"\ni: "{{app}}"\n',
                 id="a text YAML would read as something else is quoted"),
    pytest.param({"a": {}, "b": [], "c": {"d": {"e": 1}}}, "a: {}\nb: []\n\nc:\n  d:\n    e: 1\n",
                 id="an empty collection is flow and a mapping nests by two spaces"),
    pytest.param({"a": ["x", "y z", "{{q}}", "a,b"]}, 'a: [x, y z, "{{q}}", "a,b"]\n',
                 id="a short list is flow with the items that need it quoted"),
    pytest.param({"a": "one\ntwo\n\nthree"}, "a: |-\n  one\n  two\n\n  three\n",
                 id="a text of several lines is a literal block"),
    pytest.param({"a": "one\n"}, 'a: "one\\n"\n', id="a text ending in a line break is quoted, which keeps it"),
    pytest.param({"a": [{"k": "v", "w": 1}, {"k": "x"}]}, "a:\n  - k: v\n    w: 1\n  - k: x\n",
                 id="a list of mappings is a block sequence"),
    pytest.param({"a": 1, "b": {"c": 1}, "d": [1]}, "a: 1\n\nb:\n  c: 1\nd: [1]\n",
                 id="a blank line comes before each key whose value is a block at the top"),
])
def test_a_document_is_written_in_the_form_a_person_would_write(document, text):
    assert YamlWriter().dump(document) == text


def test_a_long_text_of_one_line_is_folded_at_the_width_and_a_long_list_wraps_under_its_key():
    words = " ".join(f"word{n}" for n in range(40))
    folded = YamlWriter().dump({"a": words}, width=60)
    assert folded.startswith("a: >-\n  word0 ")
    assert all(len(line) <= 60 for line in folded.splitlines())
    items = [f"item{n}" for n in range(30)]
    wrapped = YamlWriter().dump({"a": items}, width=60)
    assert wrapped.splitlines()[0].startswith("a: [item0, item1")
    assert all(len(line) <= 60 for line in wrapped.splitlines())
    assert wrapped.endswith("item29]\n")


def test_a_text_that_folding_would_change_stays_on_one_line():
    spaced = "a  " + "b " * 80 + "c"
    assert YamlWriter().dump({"a": spaced}, width=40) == f"a: {spaced}\n"


@pytest.mark.parametrize("key, text", [
    pytest.param("modules/<module>/", "modules/<module>/: 1\n", id="a joined folder with a repeating step"),
    pytest.param("domain/", "domain/: 1\n", id="a folder"),
    pytest.param("controller.py", "controller.py: 1\n", id="a file"),
    pytest.param("__main__.py", "__main__.py: 1\n", id="a file named with underscores"),
    pytest.param("[slug]/", '"[slug]/": 1\n', id="a folder YAML reads as a list is quoted"),
    pytest.param("@types/", '"@types/": 1\n', id="a folder starting with @ is quoted"),
    pytest.param("(group)/", '"(group)/": 1\n', id="a folder starting with a bracket is quoted"),
])
def test_a_key_of_the_folder_tree_is_plain_when_yaml_reads_it_back_as_written(key, text):
    written = YamlWriter().dump({key: 1})
    assert written == text
    assert yaml.safe_load(written) == {key: 1}
