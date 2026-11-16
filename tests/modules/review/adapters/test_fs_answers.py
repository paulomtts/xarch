"""The answers review keeps on the filesystem: one JSON file per key, holding the model that answered, the probability
of each option in order and the tokens, and nothing else; a file that holds no answer of that shape is none."""
import json

import pytest

from xarch.modules.review.adapters.fs_answers import FsAnswers
from xarch.modules.review.domain.errors import Refused
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


def test_an_answer_reached_through_a_link_is_none_and_keeping_one_replaces_the_link_not_what_it_points_to(tmp_path):
    victim = tmp_path / "victim.txt"
    victim.write_text("precious")
    folder = tmp_path / "cache"
    folder.mkdir()
    (folder / f"{KEY}.json").symlink_to(victim)
    assert answers().get(folder, KEY) is None
    answers().put(folder, KEY, ANSWER)
    assert victim.read_text() == "precious" and not (folder / f"{KEY}.json").is_symlink()
    assert answers().get(folder, KEY) == ANSWER


def test_a_folder_that_is_a_link_or_a_file_cannot_keep_answers_and_is_refused_naming_it(tmp_path):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (tmp_path / "linked").symlink_to(elsewhere, target_is_directory=True)
    (tmp_path / "file").write_text("x")
    for folder, why in ((tmp_path / "linked", "it is a link"), (tmp_path / "file", "it is a file, not a folder")):
        with pytest.raises(Refused, match=f"cannot keep answers in {folder}: {why}"):
            answers().ready(folder)
        with pytest.raises(Refused):
            answers().put(folder, KEY, ANSWER)
        assert answers().get(folder, KEY) is None
    answers().ready(tmp_path / "not yet made")
    assert list(elsewhere.iterdir()) == []


def test_a_folder_that_cannot_be_written_is_refused_naming_it(tmp_path):
    folder = tmp_path / "ro"
    folder.mkdir()
    folder.chmod(0o500)
    try:
        with pytest.raises(Refused, match=f"cannot keep an answer in {folder}"):
            answers().put(folder, KEY, ANSWER)
    finally:
        folder.chmod(0o700)
