"""The no-comments guard on hand-made comments: a `#` comment is reported unless it is a directive a tool reads, a
shebang on line 1 or an encoding declaration on line 1 or 2."""
import pytest

from tests.modules.rules.builders import source
from xarch.modules.rules.application.logic.comments import allowed, violations
from xarch.modules.rules.domain.values import Comment


@pytest.mark.parametrize("comment, kept", [
    pytest.param(Comment(5, "# a note"), False, id="a whole-line comment is reported"),
    pytest.param(Comment(5, "#a note"), False, id="a comment with no space is reported"),
    pytest.param(Comment(5, "# type: ignore"), True, id="a type: ignore stays"),
    pytest.param(Comment(5, "#type:ignore[attr-defined]"), True, id="a type: ignore with a code and no spaces stays"),
    pytest.param(Comment(5, "# noqa: E501"), True, id="a noqa stays"),
    pytest.param(Comment(5, "# pragma: no cover"), True, id="a pragma with its colon stays"),
    pytest.param(Comment(5, "# pragmatic note"), False, id="a word starting with pragma is a comment"),
    pytest.param(Comment(5, "# pragma no cover"), False, id="a pragma without its colon is a comment"),
    pytest.param(Comment(5, "# see the noqa rule"), False, id="a directive not at the start is a comment"),
    pytest.param(Comment(1, "#!/usr/bin/env python"), True, id="a shebang on line 1 stays"),
    pytest.param(Comment(2, "#!/usr/bin/env python"), False, id="a shebang on line 2 is a comment"),
    pytest.param(Comment(1, "# -*- coding: utf-8 -*-"), True, id="an encoding declaration on line 1 stays"),
    pytest.param(Comment(2, "# vim: set fileencoding=utf-8 :"), True, id="an encoding declaration on line 2 stays"),
    pytest.param(Comment(3, "# -*- coding: utf-8 -*-"), False, id="an encoding declaration on line 3 is a comment"),
    pytest.param(Comment(1, "# coding is fun"), False, id="the word coding without its value is a comment"),
])
def test_allowed(comment, kept):
    assert allowed(comment) is kept


def test_every_comment_not_allowed_is_reported_where_it_is_with_its_fix():
    found = violations([source("kernel/x.py", comments=(Comment(1, "#!/bin/python"), Comment(3, "# why"),
                                                         Comment(4, "# noqa")))])
    assert [(str(v), v.rule, v.fix) for v in found] == [
        ("app/kernel/x.py:3: a comment (no-comments)", "no-comments",
         "say it in a docstring or a name, and delete the comment")]
