"""Rules' CheckFormat written by spec: the checks go to spec's controller as a command, in their order, and its text
comes back as it is."""
from xarch.modules.rules.adapters.spec_check_format import SpecCheckFormat
from xarch.modules.spec.contract import ChecksWritten, WriteChecks
from xarch.profile_values.checks import Quantified, Saying, Scope, WrittenCheck, WrittenTarget

CHECK = WrittenCheck(("class",), Scope(), Quantified("may_not", (WrittenTarget("exist"),)), (Saying("m", "f"),))


class Spec:
    def __init__(self):
        self.asked: list[WriteChecks] = []

    def write_checks(self, cmd: WriteChecks) -> ChecksWritten:
        self.asked.append(cmd)
        return ChecksWritten("checks:\n  one: ...\n")


def test_the_checks_are_handed_to_spec_and_its_text_is_the_format():
    spec = Spec()
    assert SpecCheckFormat(spec).written({"one": CHECK, "two": CHECK}) == "checks:\n  one: ...\n"
    assert spec.asked == [WriteChecks({"one": CHECK, "two": CHECK})]
    assert list(spec.asked[0].checks) == ["one", "two"]
