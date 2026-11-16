"""The answers review keeps on the filesystem: one JSON file per key, holding the model that answered, the probability
of each option in order and the tokens, and nothing else; a file that holds no answer of that shape is none."""
import json

import pytest

from xarch.modules.review.adapters.fs_answers import FsAnswers
from xarch.modules.review.domain.values import Answer
from xarch.platform.data_files import DataFileReader, DataFileWriter
from xarch.platform.filesystem import FileSystem

ANSWER = Answer("jev-1.14.0", (("main", 0.7), ("domain", 0.3)), 2400, 3)
KEY = "ab" * 32


def answers() -> FsAnswers:
    return FsAnswers(FileSystem(), DataFileReader(), DataFileWriter())


def test_an_answer_kept_is_read_back_as_it_was_and_the_file_holds_only_the_answer(tmp_path):
    folder = tmp_path / ".xarch" / "cache" / "review"
    answers().put(folder, KEY, ANSWER)
    assert answers().get(folder, KEY) == ANSWER
    assert json.loads((folder / f"{KEY}.json").read_text()) == {
        "model": "jev-1.14.0", "probabilities": {"main": 0.7, "domain": 0.3}, "input_tokens": 2400, "output_tokens": 3}


def test_a_key_with_no_file_is_no_answer(tmp_path):
    assert answers().get(tmp_path, KEY) is None


@pytest.mark.parametrize("text", [
    pytest.param("not json", id="a file that is not JSON"),
    pytest.param("[]", id="a document that is not an object"),
    pytest.param('{"probabilities": {"a": 1}, "input_tokens": 1, "output_tokens": 1}', id="no model"),
    pytest.param('{"model": "m", "probabilities": [1], "input_tokens": 1, "output_tokens": 1}',
                 id="probabilities that are not an object"),
    pytest.param('{"model": "m", "probabilities": {"a": 2}, "input_tokens": 1, "output_tokens": 1}',
                 id="a probability above 1"),
    pytest.param('{"model": "m", "probabilities": {"a": true}, "input_tokens": 1, "output_tokens": 1}',
                 id="a probability that is a boolean"),
    pytest.param('{"model": "m", "probabilities": {"a": 1}, "input_tokens": "1", "output_tokens": 1}',
                 id="a count of tokens that is not a number"),
    pytest.param('{"model": "m", "probabilities": {"a": 1}, "output_tokens": 1}', id="no count of input tokens"),
])
def test_a_file_that_holds_no_answer_of_the_shape_written_is_no_answer(tmp_path, text):
    (tmp_path / f"{KEY}.json").write_text(text)
    assert answers().get(tmp_path, KEY) is None
