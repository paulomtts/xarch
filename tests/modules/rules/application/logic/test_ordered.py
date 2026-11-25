"""The order a check gives its violations in."""
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.ordered import ordered

A = Violation("app/a.py", 3, "a problem", "may-import", "do this")
B = Violation("app/a.py", 7, "another", "may-import", "do that")
C = Violation("app/b.py", 1, "a third", "tiers", "do the other")
WHOLE = Violation("app/a.py", 0, "missing x/", "structure", "create x/")


def test_violations_are_ordered_by_file_then_line_then_rule():
    later_rule = Violation("app/a.py", 3, "x", "tiers", "y")
    assert ordered([C, later_rule, B, A, WHOLE]) == (WHOLE, A, later_rule, B, C)


def test_violations_alike_in_file_line_and_rule_keep_the_order_found():
    second = Violation("app/a.py", 3, "a second problem", "may-import", "do this too")
    assert ordered([second, A]) == (second, A)


def test_a_may_import_finding_comes_before_a_package_only_finding_at_the_same_line():
    package_only = Violation("app/a.py", 3, "imported only as a package", "package-only", "import the package")
    assert ordered([package_only, A]) == (A, package_only)
