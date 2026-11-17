"""Whether a check passes: no violation, and under strict no finding of its enforcement either."""
from __future__ import annotations

from collections.abc import Sequence

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.outcomes import Finding


def passed(violations: Sequence[Violation], strict_findings: Sequence[Finding], strict: bool) -> bool:
    return not violations and not (strict and strict_findings)
