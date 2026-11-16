"""Where an answer is kept, and under which key: the project's cache below the folder holding the app unless another
is given, and a hash that changes with the model asked, the text sent or the question, holding none of them."""
from pathlib import Path

import pytest

from xarch.modules.review.application.logic.answers import cache_folder, request_key
from xarch.modules.review.domain.published import Choice, Option

QUESTION = Choice("Which part?", (Option("domain", "Is it a value?"), Option("main", "starts the app")))
KEY = request_key("m-1", "class Document: ...\n", QUESTION)


@pytest.mark.parametrize("app, given, then", [
    pytest.param(Path("/work/app"), None, Path("/work/.xarch/cache/review"),
                 id="the project's own cache lies below the folder holding the app"),
    pytest.param(Path("/work/src/shop"), None, Path("/work/src/.xarch/cache/review"),
                 id="an app below src/ keeps its cache beside it"),
    pytest.param(Path("/work/app"), Path("/elsewhere"), Path("/elsewhere"), id="a folder given is the one used"),
])
def test_the_folder_the_answers_are_kept_in(app, given, then):
    assert cache_folder(app, given) == then


@pytest.mark.parametrize("model, text, question", [
    pytest.param("m-2", "class Document: ...\n", QUESTION, id="another model"),
    pytest.param("m-1", "class Document: pass\n", QUESTION, id="another text"),
    pytest.param("m-1", "class Document: ...\n", Choice("Where?", QUESTION.options), id="another question"),
    pytest.param("m-1", "class Document: ...\n", Choice(QUESTION.ask, QUESTION.options[::-1]),
                 id="the same options in another order"),
    pytest.param("m-1", "class Document: ...\n",
                 Choice(QUESTION.ask, (Option("domain", "Is it a record?"), QUESTION.options[1])),
                 id="another description of an option"),
])
def test_a_change_to_what_is_asked_changes_the_key(model, text, question):
    assert request_key(model, text, question) != KEY


def test_the_key_is_the_same_for_the_same_question_and_holds_none_of_it():
    assert request_key("m-1", "class Document: ...\n", QUESTION) == KEY
    assert len(KEY) == 64 and set(KEY) <= set("0123456789abcdef")
