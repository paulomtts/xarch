"""Where an answer is kept, and under which key: the project's cache below the folder holding the app unless another
is given, and a hash that changes with the model asked, the text sent or the question, holding none of them."""
import hashlib
import json
from pathlib import Path

import pytest

from xarch.modules.review.application.logic.answers import cache_folder, fits, record_file, request_key, versions
from xarch.modules.review.domain.published import SCORE, YES_NO, Choice, Option
from xarch.modules.review.domain.values import Answer

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


def test_a_choice_keeps_the_key_it_had_before_questions_had_forms_and_another_form_is_another_question():
    before = json.dumps({"model": "m-1", "text": "class Document: ...\n", "ask": "Which part?",
                         "options": [["domain", "Is it a value?"], ["main", "starts the app"]]},
                        ensure_ascii=False, separators=(",", ":"))
    assert KEY == hashlib.sha256(before.encode("utf-8")).hexdigest()
    assert len({KEY, *(request_key("m-1", "class Document: ...\n", Choice(QUESTION.ask, QUESTION.options, form))
                       for form in (YES_NO, SCORE))}) == 3


def test_the_record_of_the_evals_held_to_their_examples_lies_below_the_folder_holding_the_app():
    assert record_file(Path("/work/app")) == Path("/work/.xarch/calibration.json")


@pytest.mark.parametrize("probabilities, tokens, then", [
    pytest.param((("domain", 0.3), ("main", 0.7)), (10, 1), True, id="a probability for each option, summing to 1"),
    pytest.param((("main", 0.7), ("domain", 0.305)), (10, 1), True, id="in any order, within rounding of 1"),
    pytest.param((), (10, 1), False, id="no probability at all"),
    pytest.param((("domain", 1.0),), (10, 1), False, id="an option left out"),
    pytest.param((("domain", 0.3), ("main", 0.7), ("other", 0.0)), (10, 1), False, id="an option the question has not"),
    pytest.param((("domain", 1.0), ("main", 1.0)), (10, 1), False, id="probabilities summing above 1"),
    pytest.param((("domain", 0.3), ("domain", 0.7)), (10, 1), False, id="an option named twice"),
    pytest.param((("domain", 0.3), ("main", 0.7)), (-1, 1), False, id="a count of tokens below 0"),
])
def test_an_answer_kept_answers_the_question_only_when_it_is_of_its_shape(probabilities, tokens, then):
    assert fits(Answer("m", probabilities, *tokens), QUESTION) is then


def test_the_versions_that_answered_are_each_said_once_sorted():
    assert versions(Answer("m-2", ()), Answer("m-1", ()), Answer("m-2", ())) == ("m-1", "m-2")
    assert versions() == ()
