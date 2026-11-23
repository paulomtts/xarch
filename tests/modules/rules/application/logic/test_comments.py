"""The no-comments guard on hand-made comments, each with the marker its reader says it opens with: a comment is
reported unless it is a directive a tool reads right after its own marker, a shebang on line 1 or an encoding
declaration on line 1 or 2; under the test-only languages too, whose comments come in several forms."""
import pytest

from tests.modules.rules.application.logic.checks import comment_allowed as allowed
from tests.modules.rules.application.logic.checks import no_comments as violations
from tests.modules.rules.builders import BRACE, PERCENT, PYTHON, source
from xarch.modules.rules.domain.parsed import Comment


def python_comment(line: int, text: str) -> Comment:
    """A comment as Python's reader hands it over: opened by its one marker."""
    return Comment(line, text, marker="#")


@pytest.mark.parametrize("comment, kept", [
    pytest.param(python_comment(5, "# a note"), False, id="a whole-line comment is reported"),
    pytest.param(python_comment(5, "#a note"), False, id="a comment with no space is reported"),
    pytest.param(python_comment(5, "# type: ignore"), True, id="a type: ignore stays"),
    pytest.param(python_comment(5, "#type:ignore[attr-defined]"), True,
                 id="a type: ignore with a code and no spaces stays"),
    pytest.param(python_comment(5, "# noqa: E501"), True, id="a noqa stays"),
    pytest.param(python_comment(5, "# pragma: no cover"), True, id="a pragma with its colon stays"),
    pytest.param(python_comment(5, "# pragmatic note"), False, id="a word starting with pragma is a comment"),
    pytest.param(python_comment(5, "# pragma no cover"), False, id="a pragma without its colon is a comment"),
    pytest.param(python_comment(5, "# see the noqa rule"), False, id="a directive not at the start is a comment"),
    pytest.param(python_comment(1, "#!/usr/bin/env python"), True, id="a shebang on line 1 stays"),
    pytest.param(python_comment(2, "#!/usr/bin/env python"), False, id="a shebang on line 2 is a comment"),
    pytest.param(python_comment(1, "# -*- coding: utf-8 -*-"), True, id="an encoding declaration on line 1 stays"),
    pytest.param(python_comment(2, "# vim: set fileencoding=utf-8 :"), True,
                 id="an encoding declaration on line 2 stays"),
    pytest.param(python_comment(3, "# -*- coding: utf-8 -*-"), False, id="an encoding declaration on line 3 is a comment"),
    pytest.param(python_comment(1, "# coding is fun"), False, id="the word coding without its value is a comment"),
    pytest.param(Comment(5, "# noqa"), False, id="a comment whose reader gives no marker is no directive"),
    pytest.param(Comment(1, "# -*- coding: utf-8 -*-"), False, id="nor an encoding declaration, with no marker given"),
    pytest.param(Comment(5, "noqa", marker="#"), False,
                 id="a comment whose text does not start with its marker is no directive"),
])
def test_allowed(comment, kept):
    assert allowed(comment, PYTHON) is kept


@pytest.mark.parametrize("comment, kept", [
    pytest.param(Comment(5, "// a note", marker="//"), False, id="a line comment is reported"),
    pytest.param(Comment(5, "/* a note */", marker="/*"), False, id="a block comment is reported"),
    pytest.param(Comment(5, "// @ts-expect-error", marker="//"), True, id="a directive after a line marker stays"),
    pytest.param(Comment(5, "//@ts-expect-error", marker="//"), True, id="a directive right after the marker stays"),
    pytest.param(Comment(5, "/* eslint-disable */", marker="/*"), True,
                 id="a directive after a block opening stays, though the docs print the line marker"),
    pytest.param(Comment(5, "// see @ts-expect-error", marker="//"), False,
                 id="a directive not right after the marker is a comment"),
    pytest.param(Comment(5, "/** a note */", marker="/*"), False,
                 id="a block the reader says is no doc comment is reported, whatever its text starts with"),
])
def test_allowed_under_a_language_of_line_and_block_comments(comment, kept):
    assert allowed(comment, BRACE) is kept


@pytest.mark.parametrize("comment, kept", [
    pytest.param(Comment(5, "; a note", marker=";"), False, id="a comment of the second line marker is reported"),
    pytest.param(Comment(5, "// a note", marker="//"), False, id="a comment of the first line marker is reported"),
    pytest.param(Comment(5, "/// a note", marker="//"), False,
                 id="a line comment whose text starts as a doc one is reported, the reader saying which it is"),
])
def test_allowed_under_a_language_of_two_line_markers(comment, kept):
    assert allowed(comment, PERCENT) is kept


def test_every_comment_not_allowed_is_reported_where_it_is_with_its_fix():
    found = violations([source("kernel/x.py", comments=(python_comment(1, "#!/bin/python"), python_comment(3, "# why"),
                                                         python_comment(4, "# noqa")))], PYTHON)
    assert [(str(v), v.rule, v.fix) for v in found] == [
        ("app/kernel/x.py:3: a comment (no-comments)", "no-comments",
         "say it in a docstring or a name, and delete the comment")]
