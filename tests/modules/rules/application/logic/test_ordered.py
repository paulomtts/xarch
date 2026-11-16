"""The order a check gives its violations in."""
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.ordered import ordered

A = Violation("app/a.py", 3, "a problem", "rules", "do this")
B = Violation("app/a.py", 7, "another", "rules", "do that")
C = Violation("app/b.py", 1, "a third", "tiers", "do the other")
WHOLE = Violation("app/a.py", 0, "missing x/", "structure", "create x/")


def test_violations_are_ordered_by_file_then_line_then_rule():
    later_rule = Violation("app/a.py", 3, "x", "tiers", "y")
    assert ordered([C, later_rule, B, A, WHOLE]) == (WHOLE, A, later_rule, B, C)


def test_violations_alike_in_file_line_and_rule_keep_the_order_found():
    second = Violation("app/a.py", 3, "a second problem", "rules", "do this too")
    assert ordered([second, A]) == (second, A)
