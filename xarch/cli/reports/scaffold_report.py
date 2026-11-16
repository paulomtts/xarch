"""How `xarch init` and `xarch new` show what they did: a line per file, created, updated or skipped; and why `new`
refuses the folder of a kind, or an app with no skeleton, with the command to type."""
from __future__ import annotations

from xarch.modules.scaffold.contract import KindIsAFolder, NotInitialized, Report


def report_lines(report: Report) -> list[str]:
    return ([f"created {path.as_posix()}" for path in report.created]
            + [f"updated {path.as_posix()}" for path in report.updated]
            + [f"skipped {path.as_posix()}" for path in report.skipped])


def refused_reason(refused: KindIsAFolder | NotInitialized) -> str:
    """Why `new` refuses, with the command that does what was meant."""
    match refused:
        case KindIsAFolder(kind, word):
            return f"no kind '{kind}' in the profile: that is the folder of the kind {word}: write `xarch new {word} <name>`"
        case NotInitialized(folder):
            return f"{folder} does not exist: run 'xarch init' first"
