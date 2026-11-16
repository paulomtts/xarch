"""How review cuts a file into the pieces it ranks, by the spans the reader gives: each piece at the top level, a large
class as its methods with the class's text before its first method, small pieces joined to the next, and only pieces
of 1,000 characters or more judged; and what is sent for one, with or without the file's opening lines."""
from xarch.modules.review.application.logic.pieces import large, opening, sections, sent
from xarch.modules.review.domain.values import Section, Span


def _lines(count: int, text: str) -> list[str]:
    return [f"{text}{n}\n" for n in range(count)]


def _file(*blocks: list[str]) -> tuple[str, list[tuple[int, int]]]:
    """The text of the blocks one after another, and the lines each spans."""
    spans, at = [], 1
    for block in blocks:
        spans.append((at, at + len(block) - 1))
        at += len(block)
    return "".join(line for block in blocks for line in block), spans


def test_each_function_and_class_at_the_top_level_is_a_piece_with_its_lines_and_text():
    text, (a, b) = _file(_lines(30, "    a = 1  # line "), _lines(30, "    b = 2  # line "))
    found = sections(text, (Span("function", "load", "", a), Span("class", "Store", "", b)))
    assert [(s.name, s.kind, s.lines, s.head) for s in found] == [("load", "function", a, ""), ("Store", "class", b, "")]
    assert found[0].text == "".join(_lines(30, "    a = 1  # line "))


def test_a_class_over_4000_characters_is_judged_as_its_methods_each_with_the_class_s_text_before_its_first_method():
    head = ["class Big:\n", '    """A big one."""\n']
    one, two = _lines(110, "        x = 'one' # "), _lines(110, "        y = 'two' # ")
    text, (h, m1, m2) = _file(head, one, two)
    spans = (Span("class", "Big", "", (h[0], m2[1])), Span("method", "one", "Big", m1), Span("method", "two", "Big", m2))
    found = sections(text, spans)
    assert [(s.name, s.kind, s.lines) for s in found] == [("Big.one", "method", m1), ("Big.two", "method", m2)]
    assert all(s.head == "".join(head) for s in found)
    assert sent(found[0], "") == "".join(head + one)


def test_a_class_of_4000_characters_or_fewer_is_one_piece():
    text, (h, m1) = _file(["class Small:\n"], _lines(10, "        x = 1 # "))
    found = sections(text, (Span("class", "Small", "", (h[0], m1[1])), Span("method", "go", "Small", m1)))
    assert [s.name for s in found] == ["Small"]


def test_a_piece_under_200_characters_is_joined_to_the_next_and_the_last_to_the_one_before():
    small, big, tail = _lines(2, "s"), _lines(40, "    big = 1 # "), _lines(1, "t")
    text, (s, b, t) = _file(small, big, tail)
    found = sections(text, (Span("function", "tiny", "", s), Span("function", "main", "", b),
                            Span("function", "end", "", t)))
    assert [(x.name, x.kind, x.lines) for x in found] == [("tiny, main, end", "function", (s[0], t[1]))]


def test_small_pieces_join_only_pieces_of_their_own_class():
    head = ["class Big:\n"]
    one, small = _lines(220, "        one = 1 # "), _lines(1, "        r")
    after = _lines(2, "z")
    text, (h, m1, m2, f) = _file(head, one, small, after)
    spans = (Span("class", "Big", "", (h[0], m2[1])), Span("method", "one", "Big", m1),
             Span("method", "two", "Big", m2), Span("function", "after", "", f))
    assert [s.name for s in sections(text, spans)] == ["Big.one, Big.two", "after"]


def test_only_pieces_of_1000_characters_or_more_are_judged():
    found = (Section("a", "function", (1, 2), "x" * 999), Section("b", "function", (3, 4), "x" * 1000))
    assert large(found) == found[1:]


def test_the_opening_lines_are_those_before_the_first_piece_and_are_sent_before_it_with_context():
    text = '"""Docs."""\nfrom app import x\n\ndef f():\n    pass\n'
    assert opening(text, (Span("function", "f", "", (4, 5)),)) == '"""Docs."""\nfrom app import x\n\n'
    assert sent(Section("f", "function", (4, 5), "def f():\n    pass\n"), "ctx\n") == "ctx\ndef f():\n    pass\n"
    assert opening(text, ()) == ""
