"""The data file of the kinds of file the docs quote: read into a kind by each ending, or refused naming the file with
every problem."""
import pytest

from tests.modules.spec.format_files import FILE_TYPES_DOCUMENT
from xarch.modules.spec.application.logic.file_types import file_types_of
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import FileType

SOURCE = "presets/format/file_types.yaml"


def test_the_shipped_file_names_the_fence_and_the_comment_of_each_kind_it_lists():
    assert file_types_of(FILE_TYPES_DOCUMENT) == {
        ".sh": FileType("bash", "#"), ".yml": FileType("yaml", "#"), ".md": FileType("markdown"),
        ".js": FileType("javascript", "//"), ".ts": FileType("typescript", "//"), ".go": FileType(comment="//"),
        ".rs": FileType(comment="//"), ".java": FileType(comment="//"), ".kt": FileType(comment="//"),
        ".sql": FileType(comment="--")}


def test_a_kind_says_its_fence_or_its_comment_or_both():
    assert file_types_of({".pl": {"fence": "perl"}, ".lua": {"comment": "--"}, ".c": {"fence": "c", "comment": "//"}}) == {
        ".pl": FileType("perl"), ".lua": FileType(comment="--"), ".c": FileType("c", "//")}


@pytest.mark.parametrize("given, found", [
    pytest.param([".sql"], ["must be a mapping of endings, such as .sql, to {fence, comment}"],
                 id="a document that is no mapping"),
    pytest.param({"sql": {"comment": "--"}, 3: {"fence": "x"}},
                 ["sql: must be a dot and a name, such as .sql", "3: must be a dot and a name, such as .sql"],
                 id="a key that is no ending"),
    pytest.param({".sql": "--", ".go": {}},
                 [".sql: must be a mapping of fence, comment, one of them at least",
                  ".go: must be a mapping of fence, comment, one of them at least"],
                 id="a kind that says nothing"),
    pytest.param({".sql": {"comment": "", "fence": 3, "colour": "red"}},
                 [".sql: unknown key 'colour': use fence, comment", ".sql.fence: must be a non-empty string",
                  ".sql.comment: must be a non-empty string"],
                 id="an unknown key and empty values"),
])
def test_a_broken_data_file_is_refused_naming_it_with_every_problem(given, found):
    with pytest.raises(InvalidArchitecture) as caught:
        file_types_of(given)
    assert [problem.removeprefix(f"{SOURCE}: ") for problem in caught.value.problems] == found
