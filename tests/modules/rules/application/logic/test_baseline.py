"""The baseline held against the violations of a run: a violation is keyed by rule, file and message with its digits
read alike, the record holds back as many of a key as it counts, and lowering only lowers."""
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.baseline import applied, recorded, written
from xarch.modules.rules.domain.published import BaselineStanding, Recorded, RuleCeiling


def found(file: str, message: str, rule: str = "may-import") -> Violation:
    return Violation(file, 1, message, rule, "fix it")


A = found("app/a.py", "a/ may not import b/ (app.b) at line 3")
B = found("app/b.py", "b/ may not import c/ (app.c)")
FILE = ".xarch/baseline.json"


def test_the_record_counts_each_key_once_in_the_order_of_rule_file_and_message():
    moved = found("app/a.py", "a/ may not import b/ (app.b) at line 12")
    assert recorded([B, A, moved, found("app/z.py", "missing x/", "structure")]) == (
        Recorded("may-import", "app/a.py", A.message, 2), Recorded("may-import", "app/b.py", B.message, 1),
        Recorded("structure", "app/z.py", "missing x/", 1))


def test_what_the_record_holds_is_held_back_and_digits_do_not_change_a_key():
    moved = found("app/a.py", "a/ may not import b/ (app.b) at line 40")
    result = applied([moved, B], recorded([A]), FILE)
    assert result.shown == (B,)
    assert result.standing == BaselineStanding(FILE, (RuleCeiling("may-import", 1, 1),), 1, 0)


def test_a_swap_is_shown_and_leaves_the_record_below():
    other = found("app/a.py", "a/ may not import d/ (app.d) at line 3")
    result = applied([other], recorded([A]), FILE)
    assert (result.shown, result.standing.held, result.standing.below) == ((other,), 0, 1)


def test_more_of_a_key_than_recorded_shows_the_rest():
    result = applied([A, A], recorded([A]), FILE)
    assert (result.shown, result.standing.held) == ((A,), 1)


def test_lowering_drops_a_key_gone_and_lowers_a_count_but_never_adds_or_raises():
    record = (Recorded("may-import", "app/a.py", A.message, 2), Recorded("may-import", "app/b.py", B.message, 1))
    assert written(record, [A, found("app/n.py", "new")], False) == (Recorded("may-import", "app/a.py", A.message, 1),)
    assert written(record, [A, A, A, B], False) == record


def test_a_write_of_one_rule_changes_that_rule_alone():
    other = Recorded("syntax", "app/s.py", "s", 1)
    record = (Recorded("may-import", "app/a.py", A.message, 2), other)
    assert written(record, [A], False, "may-import") == (Recorded("may-import", "app/a.py", A.message, 1), other)
    assert written(record, [B], True, "may-import") == (Recorded("may-import", "app/b.py", B.message, 1), other)
    assert written(None, [A, found("app/s.py", "s", "syntax")], False, "may-import") == (
        Recorded("may-import", "app/a.py", A.message, 1),)
