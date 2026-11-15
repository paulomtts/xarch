"""Spec's ProfileFormat as YAML: the content of a profile file is the document as YAML, in UTF-8."""
from xarch.modules.spec.adapters.yaml_profile_format import YamlProfileFormat
from xarch.platform.yaml_writer import YamlWriter


def test_a_profile_is_written_as_yaml_in_utf_8():
    assert YamlProfileFormat(YamlWriter()).written({"xarch": 2, "name": "cafés"}) == "xarch: 2\nname: \"cafés\"\n".encode()
