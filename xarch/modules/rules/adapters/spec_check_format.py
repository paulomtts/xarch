"""The check format written by the spec module, which reads it too: rules hands it checks as a profile writes them and
takes back their text."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from xarch.modules.spec.contract import ChecksWritten, WriteChecks
from xarch.profile_values.checks import WrittenCheck


class _Spec(Protocol):
    """The little the check format uses of spec's controller."""

    def write_checks(self, cmd: WriteChecks) -> ChecksWritten: ...


class SpecCheckFormat:
    """Satisfies rules' CheckFormat port by asking spec to write the checks."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def written(self, checks: Mapping[str, WrittenCheck]) -> str:
        return self._spec.write_checks(WriteChecks(dict(checks))).text
