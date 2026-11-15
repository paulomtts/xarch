"""How `xarch check` shows what it found, on hand-made violations and enforcement states: the text lines, the
enforcement section and the JSON document."""
import json

import pytest

from xarch.cli.reports.report import enforcement_lines, json_document, ordered, text_lines
from xarch.kernel.logic.origin import Origin
from xarch.kernel.violations import At, Violation, Weak
from xarch.modules.rules.contract import AppChecked, ApproximateView, EnforcementView, ExcludedView

A = Violation("app/a.py", 3, "a problem", "rules", "do this")
B = Violation("app/a.py", 7, "another", "rules", "do that")
C = Violation("app/b.py", 1, "a third", "tiers", "do the other")
WHOLE = Violation("app/a.py", 0, "missing x/", "structure", "create x/")


@pytest.mark.parametrize("found, hints, lines", [
    pytest.param([], {}, ["OK: no violations"], id="no violation is said so"),
    pytest.param([A, B, C], {}, [
        "app/a.py:3: a problem", "    fix: do this", "app/a.py:7: another", "    fix: do that",
        "app/b.py:1: a third", "    fix: do the other", "3 violation(s) in 2 file(s)"],
        id="each finding is followed by its fix, and the summary counts the violations and their files"),
    pytest.param([WHOLE], {}, ["app/a.py: missing x/", "    fix: create x/", "1 violation(s) in 1 file(s)"],
                 id="a finding of a whole file shows no line"),
    pytest.param([A, B], {"rules": "see docs/rules.md"}, [
        "app/a.py:3: a problem", "    fix: do this", "    hint: see docs/rules.md",
        "app/a.py:7: another", "    fix: do that", "    hint: see docs/rules.md", "2 violation(s) in 1 file(s)"],
        id="the hint of the rule follows the fix of each of its findings"),
    pytest.param([A, C], {"tiers": "ask the owner"}, [
        "app/a.py:3: a problem", "    fix: do this", "app/b.py:1: a third", "    fix: do the other",
        "    hint: ask the owner", "2 violation(s) in 2 file(s)"],
        id="a finding of another rule gets no hint"),
    pytest.param([A], {"stand-ins": "unused"}, ["app/a.py:3: a problem", "    fix: do this",
                                                 "1 violation(s) in 1 file(s)"],
                 id="a hint for a rule that found nothing is not shown"),
])
def test_text_lines(found, hints, lines):
    assert text_lines(found, hints) == lines


def test_violations_are_ordered_by_file_then_line_then_rule():
    later_rule = Violation("app/a.py", 3, "x", "tiers", "y")
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
    assert enforcement_lines(EnforcementView(Origin("web"), skipped=skipped), False)[2] == line


def test_the_json_document_gives_each_violation_its_fix_and_the_hint_of_its_rule_as_keys_of_their_own():
    checked = AppChecked((C, A), EnforcementView(Origin("web")), {"rules": "see the docs"}, False)
    document = json.loads(json_document("web", checked, False))
    assert document["violations"] == [
        {"rule": "rules", "file": "app/a.py", "line": 3, "message": "a problem", "fix": "do this",
         "hint": "see the docs"},
        {"rule": "tiers", "file": "app/b.py", "line": 1, "message": "a third", "fix": "do the other", "hint": None}]


def test_the_json_document_holds_the_violations_in_order_and_both_lists_of_guards_off():
    state = EnforcementView(Origin("my.yaml", False, "web", ("closed-tree", "no-comments"), ("closed-tree",)))
    document = json.loads(json_document("my.yaml", AppChecked((C, A), state, {}, False), False))
    assert ([v["line"] for v in document["violations"]], document["enforcement"]["profile"]["guards_off"],
            document["enforcement"]["profile"]["baseline_off"]) == ([3, 1], ["closed-tree", "no-comments"],
                                                                    ["closed-tree"])


def test_an_excluded_folder_is_named_with_its_reason_after_the_ungoverned_files():
    state = EnforcementView(Origin("web"), ("app/stray.py",), ("app/stray.py",), excluded=(ExcludedView("app/examples", "shipped as data"),
                                                                  ExcludedView("app/kernel/legacy", "copied code")),
                            language="Pascal")
    assert enforcement_lines(state, False)[2:] == [
        "  ungoverned:  1 Pascal file outside every part (app/stray.py)",
        "  excluded:    app/examples/ (shipped as data)",
        "  excluded:    app/kernel/legacy/ (copied code)"]


def test_the_json_document_lists_every_excluded_folder_with_its_reason():
    state = EnforcementView(Origin("web"), excluded=(ExcludedView("app/examples", "shipped as data"),))
    document = json.loads(json_document("web", AppChecked((), state, {}, True), False))
    assert document["enforcement"]["excluded"] == [{"folder": "app/examples", "reason": "shipped as data"}]


PASS = Weak("pass-through", "app/s.py", 4, "S.get only passes its arguments on to self.repo.get", "use self.repo.get")
OLD = Weak("stand-ins", "tests/fakes/r.py", 1, "FakeR does not define get, which R declares")


def test_a_weak_check_with_a_fix_shows_it_under_its_line_and_the_hint_of_its_rule_after_it():
    state = EnforcementView(origin=Origin("web"), weak=(OLD, PASS))
    assert enforcement_lines(state, False, {"pass-through": "see the ADR"})[-4:] == [
        "  weak:        tests/fakes/r.py:1: FakeR does not define get, which R declares",
        "  weak:        app/s.py:4: S.get only passes its arguments on to self.repo.get",
        "      fix: use self.repo.get",
        "      hint: see the ADR"]
    assert enforcement_lines(state, False)[-2:] == [
        "  weak:        app/s.py:4: S.get only passes its arguments on to self.repo.get", "      fix: use self.repo.get"]


def test_the_json_weak_items_hold_their_fix_or_null():
    state = EnforcementView(origin=Origin("web"), weak=(OLD, PASS))
    document = json.loads(json_document("web", AppChecked((), state, {}, True), False))
    assert document["enforcement"]["weak"] == [
        {"rule": "stand-ins", "file": "tests/fakes/r.py", "line": 1,
         "message": "FakeR does not define get, which R declares", "fix": None},
        {"rule": "pass-through", "file": "app/s.py", "line": 4,
         "message": "S.get only passes its arguments on to self.repo.get", "fix": "use self.repo.get"}]


def test_ungoverned_files_are_source_files_when_the_language_is_not_named():
    state = EnforcementView(Origin("web"), ("app/a.src", "app/b.src"), ("app/a.src", "app/b.src"))
    assert enforcement_lines(state, False)[2:] == ["  ungoverned:  2 source files outside every part (app/a.src, app/b.src)"]


APPROXIMATE = ApproximateView("parts.services.names", "class", "a class defined in a branch is not read",
                              "parts.services.names reads class only partly: a class defined in a branch is not read")


def test_a_key_read_approximately_has_a_line_of_its_own_and_is_an_item_of_the_json_document():
    state = EnforcementView(origin=Origin("web"), approximate=(APPROXIMATE,))
    assert enforcement_lines(state, False)[-1] == (
        "  approximate: parts.services.names reads class only partly: a class defined in a branch is not read")
    document = json.loads(json_document("web", AppChecked((), state, {}, True), False))
    assert document["enforcement"]["approximate"] == [
        {"key": "parts.services.names", "fact": "class", "note": "a class defined in a branch is not read"}]
