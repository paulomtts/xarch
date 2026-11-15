"""How `xarch check` shows what it found, on hand-made violations and enforcement states: the text lines, the
enforcement section and the JSON document."""
import json

import pytest

from xarch.cli.report import enforcement_lines, folders, json_document, ordered, text_lines
from xarch.kernel.violations import Violation
from xarch.modules.rules.contract import At, Enforcement, Origin

A = Violation("app/a.py", 3, "a problem", "rules")
B = Violation("app/a.py", 7, "another", "rules")
C = Violation("app/b.py", 1, "a third", "tiers")
WHOLE = Violation("app/a.py", 0, "missing x/", "structure")


@pytest.mark.parametrize("found, lines", [
    pytest.param([], ["OK: no violations"], id="no violation is said so"),
    pytest.param([A, B, C], ["app/a.py:3: a problem", "app/a.py:7: another", "app/b.py:1: a third",
                             "3 violation(s) in 2 file(s)"], id="the summary counts the violations and their files"),
])
def test_text_lines(found, lines):
    assert text_lines(found) == lines


@pytest.mark.parametrize("files, tops", [
    pytest.param(["app/main.py", "app/kernel/x.py", "app/kernel/y/z.py", "app/scripts/a.py"],
                 ["app/main.py", "app/kernel/", "app/scripts/"],
                 id="a file at the app's root is itself, any other its top folder, each once in order"),
])
def test_folders(files, tops):
    assert folders(files) == tops


def test_violations_are_ordered_by_file_then_line_then_rule():
    later_rule = Violation("app/a.py", 3, "x", "tiers")
    assert ordered([C, later_rule, B, A, WHOLE]) == [WHOLE, A, later_rule, B, C]


SKIPS = tuple(At("tests/test_a.py", line) for line in range(1, 8))


@pytest.mark.parametrize("skipped, line", [
    pytest.param(SKIPS[:5], "  skipped:     5 skips (" + ", ".join(f"tests/test_a.py:{n}" for n in range(1, 6)) + ")",
                 id="up to five skips are each named"),
    pytest.param(SKIPS, "  skipped:     7 skips (" + ", ".join(f"tests/test_a.py:{n}" for n in range(1, 6))
                 + " and 2 more)", id="past five the rest are counted"),
    pytest.param(SKIPS[:1], "  skipped:     1 skip (tests/test_a.py:1)", id="one skip is singular"),
])
def test_a_line_of_skips_names_five_places_then_counts_the_rest(skipped, line):
    assert enforcement_lines(Enforcement(Origin("web"), skipped=skipped), False)[2] == line


def test_the_json_document_holds_the_violations_in_order_and_both_lists_of_guards_off():
    state = Enforcement(Origin("my.yaml", False, "web", ("closed-tree", "no-comments"), ("closed-tree",)))
    document = json.loads(json_document("my.yaml", [C, A], state, False))
    assert ([v["line"] for v in document["violations"]], document["enforcement"]["profile"]["guards_off"],
            document["enforcement"]["profile"]["baseline_off"]) == ([3, 1], ["closed-tree", "no-comments"],
                                                                    ["closed-tree"])
