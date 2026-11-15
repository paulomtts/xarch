"""The syntax rule on hand-made source files: a file that does not parse is a violation at the line of its error."""
from tests.modules.rules.builders import source
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.syntax import violations


def test_a_file_that_does_not_parse_is_a_violation_and_one_that_does_is_not():
    broken = source("kernel/bad.py", error=(3, "invalid syntax"))
    assert violations([source("kernel/good.py"), broken]) == [
        Violation("app/kernel/bad.py", 3, "invalid syntax", "syntax", "correct the syntax so that the file can be read")]
