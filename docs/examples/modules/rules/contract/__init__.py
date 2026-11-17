from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.kernel.violations import Place, Violation


@dataclass(frozen=True)
class CheckApp:
    root: Path
    profile: str
    strict: bool = False


@dataclass(frozen=True)
class CycleView:
    modules: tuple[str, ...]


@dataclass(frozen=True)
class AppChecked:
    violations: tuple[Violation, ...]
    cycles: tuple[CycleView, ...]
    profile: str


@dataclass(frozen=True)
class ChecksCannotRun:
    problems: tuple[str, ...]


@dataclass(frozen=True)
class CheckRefused:
    reason: str


CheckAppResult = AppChecked | ChecksCannotRun | CheckRefused

__all__ = ["AppChecked", "CheckApp", "CheckAppResult", "CheckRefused", "ChecksCannotRun", "CycleView", "Place",
           "Violation"]
