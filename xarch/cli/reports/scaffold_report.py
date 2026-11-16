"""How `xarch init` and `xarch new` show what they did: a line per file, created, updated or skipped; and why `new`
refuses the folder of a kind, or an app with no skeleton, with the command to type."""
from __future__ import annotations

from pathlib import Path

from xarch.modules.scaffold.contract import KindIsAFolder, NotInitialized, ReportView


def report_lines(report: ReportView, cwd: Path) -> list[str]:
    """A line per file, each path shown from cwd, the folder the command was run in, when it lies below it."""
    return ([f"created {_shown(path, cwd)}" for path in report.created]
            + [f"updated {_shown(path, cwd)}" for path in report.updated]
            + [f"skipped {_shown(path, cwd)}" for path in report.skipped])


def refused_reason(refused: KindIsAFolder | NotInitialized, cwd: Path) -> str:
    """Why `new` refuses, with the command that does what was meant."""
    match refused:
        case KindIsAFolder(kind, word):
            return f"no kind '{kind}' in the profile: that is the folder of the kind {word}: write `xarch new {word} <name>`"
        case NotInitialized(folder):
            return f"{_shown(folder, cwd)} does not exist: run 'xarch init' first"


def _shown(path: Path, cwd: Path) -> str:
    return (path.relative_to(cwd) if path.is_relative_to(cwd) else path).as_posix()
