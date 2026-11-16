"""How review cuts a text into lines: at the line breaks the language's reader counts, and at nothing else."""
import pytest

from xarch.modules.review.application.logic.lines import lines


@pytest.mark.parametrize("text, then", [
    pytest.param("a\nb\n", ("a\n", "b\n"), id="line feeds"),
    pytest.param("a\r\nb\rc", ("a\r\n", "b\r", "c"), id="a carriage return and line feed, a carriage return alone"),
    pytest.param("a\x0cb\nc\x0bd\n", ("a\x0cb\n", "c\x0bd\n"), id="a form feed and a vertical tab end no line"),
    pytest.param("a b c\x85d\x1ce\n", ("a b c\x85d\x1ce\n",),
                 id="unicode line and paragraph separators, next line and file separator end no line"),
    pytest.param("", (), id="no text, no line"),
    pytest.param("\n\n", ("\n", "\n"), id="empty lines are lines"),
])
def test_a_text_is_cut_at_line_feeds_and_carriage_returns_alone(text, then):
    assert lines(text) == then
