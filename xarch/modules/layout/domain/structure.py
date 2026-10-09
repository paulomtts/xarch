"""Structure rules: the folders and files that architecture.md section 1 requires to exist.

Only what is required is looked for: extra folders and files are none of the layout's business.
"""
from __future__ import annotations

from collections.abc import Collection, Iterable
from dataclasses import dataclass

from xarch.kernel.violations import Violation


@dataclass(frozen=True)
class Requirement:
    owner: str                   # who is incomplete when it is missing, e.g. "app" or "app/modules/docs"
    path: tuple[str, ...]        # below the root
    is_dir: bool
    shown: str                   # how it is named when missing, e.g. "kernel/" or "application/controller.py"


def is_module_name(name: str) -> bool:
    return name.isidentifier() and not name.startswith("_")


def requirements(root: str, top_level: Iterable[str], module_parts: Iterable[tuple[tuple[str, ...], bool]],
                 modules: Iterable[str]) -> list[Requirement]:
    """What must exist: every top-level folder, and every part of every module found below modules/."""
    required = [Requirement(root, (name,), True, f"{name}/") for name in top_level]
    parts = list(module_parts)
    for module in sorted(m for m in modules if is_module_name(m)):
        for path, is_dir in parts:
            shown = "/".join(path) + ("/" if is_dir else "")
            required.append(Requirement(f"{root}/modules/{module}", ("modules", module, *path), is_dir, shown))
    return required


def missing(required: Iterable[Requirement], present: Collection[Requirement]) -> list[Violation]:
    return [Violation(r.owner, 0, f"missing {r.shown}") for r in required if r not in present]
