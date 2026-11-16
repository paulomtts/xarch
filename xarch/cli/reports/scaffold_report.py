"""How `xarch init` and `xarch new` show what they did: a line per file, created, updated or skipped; and why `new`
refuses the folder of a kind, an app with no skeleton, or an instance there already, with the command to type."""
from __future__ import annotations

from pathlib import Path

from xarch.cli.reports.shown import shown
from xarch.modules.scaffold.contract import InstanceExists, KindIsAFolder, NotInitialized, ReportView


def report_lines(report: ReportView, cwd: Path) -> list[str]:
    """A line per file, each path shown from cwd, the folder the command was run in, when it lies below it."""
    return ([f"created {shown(path, cwd)}" for path in report.created]
            + [f"updated {shown(path, cwd)}" for path in report.updated]
            + [f"skipped {shown(path, cwd)}" for path in report.skipped])


def refused_reason(refused: KindIsAFolder | NotInitialized | InstanceExists, cwd: Path) -> str:
    """Why `new` refuses, with the command that does what was meant, a folder shown from the working folder."""
    match refused:
        case InstanceExists(name, folder):
            return f"'{name}' already exists at {shown(folder, cwd)}"
        case KindIsAFolder(kind, word):
            return f"no kind '{kind}' in the profile: that is the folder of the kind {word}: write `xarch new {word} <name>`"
        case NotInitialized(folder):
            return f"{shown(folder, cwd)} does not exist: run 'xarch init' first"


