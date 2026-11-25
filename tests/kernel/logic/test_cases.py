"""How a name is written in a case: split into words where the case of its letters changes, joined in the case a
profile asks for, and filled into a text in place of the placeholder that asks for it."""
import pytest

from xarch.kernel.logic.cases import CASED, CASES, filled, written


@pytest.mark.parametrize("name, forms", [
    pytest.param("Publish", ("publish", "publish", "publish", "Publish"), id="one word"),
    pytest.param("PublishDocument", ("publish_document", "publish-document", "publishDocument", "PublishDocument"),
                 id="two words"),
    pytest.param("HTTPCheck", ("http_check", "http-check", "httpCheck", "HttpCheck"), id="a run of capitals is one word"),
    pytest.param("MarkRead2", ("mark_read2", "mark-read2", "markRead2", "MarkRead2"), id="a digit stays with its word"),
])
def test_a_name_is_written_in_each_case(name, forms):
    assert tuple(written(name, case) for case in CASES) == forms


def test_the_cases_are_four_in_order_and_each_has_its_placeholder():
    assert (CASES, CASED) == (("snake", "kebab", "camel", "pascal"),
                              ("{name:snake}", "{name:kebab}", "{name:camel}", "{name:pascal}"))


@pytest.mark.parametrize("name, snake", [
    pytest.param("Publish_Doc", "publish_doc", id="an underscore stays inside its word"),
    pytest.param("ABC", "abc", id="a run of capitals alone is one word"),
    pytest.param("A", "a", id="one capital is one word"),
    pytest.param("X2Y", "x2_y", id="a capital after a digit starts a word"),
])
def test_snake_case_is_the_rule_of_before(name, snake):
    assert written(name, "snake") == snake


def test_no_character_but_a_change_of_case_ends_a_word():
    assert tuple(written("Publish_Doc", case) for case in CASES) == ("publish_doc", "publish_doc", "publish_doc",
                                                                     "Publish_doc")


@pytest.mark.parametrize("text, expected", [
    pytest.param("test_{name:snake}.py", "test_http_check.py", id="snake fills the words joined by an underscore"),
    pytest.param("{name:kebab}.test.ts", "http-check.test.ts", id="kebab fills them joined by a hyphen"),
    pytest.param("{name:camel}.test.ts", "httpCheck.test.ts", id="camel capitalises each word but the first"),
    pytest.param("{name:pascal}.test.ts", "HttpCheck.test.ts", id="pascal capitalises every word"),
    pytest.param("test_{name}.py", "test_{name}.py", id="a name with no case is no placeholder and stays"),
    pytest.param("test_{name:upper}.py", "test_{name:upper}.py", id="nor is a name in a case there is not"),
])
def test_a_text_is_filled_with_the_name_in_the_case_its_placeholder_asks_for(text, expected):
    assert filled(text, "HTTPCheck") == expected
