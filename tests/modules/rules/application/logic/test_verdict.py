"""Whether a check passes: no violation, and under strict no finding of its enforcement."""
import pytest

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.verdict import passed
from xarch.modules.rules.domain.outcomes import Finding

FOUND = [Violation("app/a.py", 1, "a problem", "rules", "do this")]
FINDINGS = [Finding("ungoverned", "app/stray.py")]


@pytest.mark.parametrize("violations, findings, strict, ok", [
    pytest.param([], [], False, True, id="nothing found passes"),
    pytest.param(FOUND, [], False, False, id="a violation fails"),
    pytest.param([], FINDINGS, False, True, id="a finding of the enforcement does not fail without strict"),
    pytest.param([], FINDINGS, True, False, id="a finding of the enforcement fails under strict"),
    pytest.param([], [], True, True, id="under strict nothing found passes"),
])
def test_passed(violations, findings, strict, ok):
    assert passed(violations, findings, strict) is ok
