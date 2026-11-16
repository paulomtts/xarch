"""Spec's ProfileFormat as YAML: the content of a profile file is the document as YAML, in UTF-8, and a copy's text is
named for the copy and based on what it was copied from."""
from xarch.modules.spec.adapters.yaml_profile_format import YamlProfileFormat
from xarch.platform.yaml_writer import YamlWriter

FORMAT = YamlProfileFormat(YamlWriter())


def test_a_profile_is_written_as_yaml_in_utf_8():
    assert YamlProfileFormat(YamlWriter()).written({"xarch": 2, "name": "cafés"}) == "xarch: 2\nname: \"cafés\"\n".encode()


ORIGINAL = "# a comment\nxarch: 2\nname: web\nlanguage: python\n\nparts:\n  name: not this one\n"


def test_the_copy_is_named_and_based_on_the_original_and_keeps_everything_else_as_written():
    assert FORMAT.renamed(ORIGINAL, "mine", "web") == (
        "# a comment\nxarch: 2\nname: mine\nbased_on: web\nlanguage: python\n\nparts:\n  name: not this one\n")


def test_a_based_on_the_original_already_had_is_replaced_not_repeated():
    text = FORMAT.renamed("xarch: 2\nname: web\nbased_on: cli\n", "mine", "web")
    assert text == "xarch: 2\nname: mine\nbased_on: web\n"


def test_a_profile_with_no_name_line_cannot_be_copied():
    assert FORMAT.renamed("xarch: 2\nparts: {}\n", "mine", "web") is None
