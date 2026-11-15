"""How `xarch init` and `xarch new` show what they did: a line per file, created, updated or skipped."""
from __future__ import annotations

from xarch.modules.scaffold.contract import Report


def report_lines(report: Report) -> list[str]:
    return ([f"created {path.as_posix()}" for path in report.created]
            + [f"updated {path.as_posix()}" for path in report.updated]
            + [f"skipped {path.as_posix()}" for path in report.skipped])
