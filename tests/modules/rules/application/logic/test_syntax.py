"""The syntax rule on hand-made source files: a file that does not parse is a violation at the line of its error, said
as a file not valid in the language of the profile; one that cannot be read as text is one too, said as why."""
from tests.modules.rules.application.logic.checks import syntax as violations
from tests.modules.rules.builders import PYTHON, source
from xarch.kernel.source import Unparsable
from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.values import Profile


def test_a_file_that_does_not_parse_is_a_violation_and_one_that_does_is_not():
    broken = source("kernel/bad.py", error=Unparsable(3, "invalid syntax"))
    assert violations([source("kernel/good.py"), broken], Profile({}, {}, language=PYTHON)) == [
        Violation("app/kernel/bad.py", 3, "not valid Python: invalid syntax", "syntax",
                  "correct the syntax so that the file can be read")]


def test_a_profile_that_names_no_language_says_source():
    broken = source("kernel/bad.py", error=Unparsable(1, "invalid syntax"))
    assert violations([broken], Profile({}, {}))[0].message == "not valid source: invalid syntax"


def test_a_file_that_cannot_be_read_as_text_is_a_violation_that_says_why():
    unread = source("kernel/latin.py", error=Unparsable(0, "not UTF-8 text (byte 0xff at offset 0 cannot be decoded)",
                                                        unreadable=True))
    assert violations([unread], Profile({}, {}, language=PYTHON)) == [
        Violation("app/kernel/latin.py", 0, "not UTF-8 text (byte 0xff at offset 0 cannot be decoded), so no check "
                  "reads it", "syntax", "save the file as UTF-8 text that xarch may read")]
