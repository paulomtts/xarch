"""In-memory implementation of rules' CheckFormat port. Not an adapter: a test double only."""
from __future__ import annotations

from collections.abc import Mapping

from xarch.profile_values.checks import WrittenCheck


class FakeCheckFormat:
    """Satisfies rules' CheckFormat: a line per check, its id and the kinds of fact it reads, then a line per file of
    its examples, the side, its path and its code as written."""

    def written(self, checks: Mapping[str, WrittenCheck]) -> str:
        lines: list[str] = []
        for name, check in checks.items():
            lines.append(f"{name}: reads {', '.join(check.read)}")
            lines += [f"{name}.{side}: {path}: {code!r}" for side, files in (("flagged", check.flagged),
                                                                             ("clean", check.clean))
                      for path, code in files]
        return "\n".join(lines) + "\n"
