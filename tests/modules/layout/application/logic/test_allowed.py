"""The findings of the layout structure.accepted accepts: a finding an entry names by its path (below the app, or below
the tests root) is waived with the entry's reason, and an entry that names none is a finding of structure, or of
test-tree for one below the tests root."""
from xarch.kernel.violations import Violation
from xarch.modules.layout.application.logic.allowed import sifted
from xarch.modules.layout.domain.published import Waived
from xarch.modules.layout.domain.structure import Allowed

MISSING = Violation("app/modules/docs", 0, "missing domain/", "structure", "create app/modules/docs/domain/")
STRAY = Violation("tests/modules/old", 0, "mirrors no folder of the app (app/modules/old)", "test-tree", "remove it")
FOUND = [((("modules", "docs", "domain"), False), MISSING), ((("modules", "old"), True), STRAY)]


def test_a_finding_an_entry_names_is_waived_and_the_others_kept():
    entry = Allowed(("modules", "docs", "domain"), False, "modules/docs/domain/", "why")
    assert sifted(FOUND, [entry], "app", "tests") == (
        (STRAY,), (Waived("structure", "app/modules/docs", "missing domain/", "why"),))


def test_an_entry_below_the_tests_names_only_a_finding_below_the_tests():
    entry = Allowed(("modules", "old"), True, "tests/modules/old", "why")
    assert sifted(FOUND, [entry], "app", "tests")[1] == (Waived("test-tree", "tests/modules/old", STRAY.message, "why"),)
    assert sifted(FOUND, [Allowed(("modules", "old"), False, "modules/old", "why")], "app", "tests")[0][:2] == (
        MISSING, STRAY)


def test_an_entry_that_names_no_finding_is_a_finding_of_its_rule():
    app, tests = Allowed(("kernel",), False, "kernel/", "why"), Allowed(("gone",), True, "tests/gone", "why")
    kept, waived = sifted([], [app, tests], "app", "tests")
    assert waived == ()
    assert kept == (
        Violation("app/kernel", 0, "structure.accepted accepts kernel/ as a finding of structure, and structure finds "
                                   "none there (structure.accepted)", "structure",
                  "drop the entry of kernel/ from structure.accepted"),
        Violation("tests/gone", 0, "structure.accepted accepts tests/gone as a finding of test-tree, and test-tree "
                                   "finds none there (structure.accepted)", "test-tree",
                  "drop the entry of tests/gone from structure.accepted"))
