"""Reading YAML and JSON data files: plain values back, and a repeated key, or text that does not parse, refused with
every reason, each safe to show."""
import pytest

from xarch.platform.data_files import DataFileError, DataFileReader


def test_yaml_and_json_read_into_plain_values():
    reader = DataFileReader()
    assert reader.parse("a: 1\nb: [x, y]\n") == {"a": 1, "b": ["x", "y"]}
    assert reader.parse('{"a": 1, "b": ["x"]}', json_syntax=True) == {"a": 1, "b": ["x"]}


@pytest.mark.parametrize("text, json_syntax, problems", [
    pytest.param("a: 1\nb: 2\na: 3\n", False, ("line 3: duplicate key 'a'",), id="a key repeated in yaml"),
    pytest.param("a:\n  b: 1\n  b: 2\nc: 1\nc: 2\n", False, ("line 3: duplicate key 'b'", "line 5: duplicate key 'c'"),
                 id="every key repeated in yaml, at any depth"),
    pytest.param('{"a": 1, "a": 2}', True, ("duplicate key 'a'",), id="a key repeated in json"),
    pytest.param('{unclosed', False, ("not valid YAML: line 1, column 10: expected ',' or '}', but got '<stream end>'",),
                 id="an unclosed mapping"),
    pytest.param('a: &x [*x]\n', False, ("not valid YAML: line 1, column 4: found unconstructable recursive node",),
                 id="a recursive anchor"),
    pytest.param('? [a, b]\n: 1\n', False, ("not valid YAML: line 1, column 3: a mapping key must be a plain value",),
                 id="a key that is a list"),
    pytest.param('xarch: !!python/object:os.system x\n', False,
                 ("not valid YAML: line 1, column 8: could not determine a constructor for the tag "
                  "'tag:yaml.org,2002:python/object:os.system'",), id="a python tag"),
    pytest.param('{"a": ', True, ("not valid JSON: Expecting value: line 1 column 7 (char 6)",), id="json cut short"),
])
def test_a_bad_data_file_is_refused_with_every_reason(text, json_syntax, problems):
    with pytest.raises(DataFileError) as caught:
        DataFileReader().parse(text, json_syntax=json_syntax)
    assert caught.value.problems == problems
