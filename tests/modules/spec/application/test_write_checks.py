"""Use case: checks written as the `checks` of a profile, in the format spec reads them, for what `profile explain`
shows of a rule."""
from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.modules.spec.application.helpers import controller
from xarch.modules.spec.contract import ChecksWritten, WriteChecks
from xarch.profile_values.checks import Quantified, Saying, Scope, WrittenCheck, WrittenTarget

SPEC = controller(FakeArchitectureFiles({}))


def check(slot: str) -> WrittenCheck:
    return WrittenCheck(("class",), Scope(), Quantified(slot, (WrittenTarget("exist"),)), (Saying("m", "f"),))


def test_checks_are_written_by_the_profile_format_each_under_its_id_in_order():
    written = SPEC.write_checks(WriteChecks({"no-class": check("may_not"), "only-class": check("may_only")}))
    assert written == ChecksWritten("no-class: may_not\nonly-class: may_only\n")
