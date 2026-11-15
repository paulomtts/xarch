"""Structure rules: the folders and files that architecture.md section 1 requires to exist.

Only what is required is looked for: extra folders and files are none of the layout's business.
"""
from __future__ import annotations

from collections.abc import Collection, Iterable
from dataclasses import dataclass

from xarch.kernel.violations import Violation


@dataclass(frozen=True)
class Requirement:
    """Something that must exist below the root: owner is who is incomplete without it (e.g. "app" or
    "app/modules/docs"), and shown how it is named when missing (e.g. "kernel/" or "application/controller.py")."""
    owner: str
    path: tuple[str, ...]
    is_dir: bool
    shown: str


def is_instance_name(name: str) -> bool:
    """Whether a folder found in the `each` folder's parent is an instance of it, not a cache or private folder."""
    return name.isidentifier() and not name.startswith("_")


def requirements(root: str, top_level: Iterable[str], each_root: tuple[str, ...] | None,
                 each_parts: Iterable[tuple[tuple[str, ...], bool]], instances: Iterable[str]) -> list[Requirement]:
    """What must exist: every top-level folder, and every part of every instance found in the `each` folder's
    parent."""
    required = [Requirement(root, (name,), True, f"{name}/") for name in top_level]
    if each_root is None:
        return required
    parts = list(each_parts)
    for name in sorted(n for n in instances if is_instance_name(n)):
        owner = "/".join((root, *each_root, name))
        for path, is_dir in parts:
            shown = "/".join(path) + ("/" if is_dir else "")
            required.append(Requirement(owner, (*each_root, name, *path), is_dir, shown))
    return required


def missing(required: Iterable[Requirement], present: Collection[Requirement]) -> list[Violation]:
    return [Violation(r.owner, 0, f"missing {r.shown}") for r in required if r not in present]


def hidden(path: tuple[str, ...]) -> bool:
    """A folder such as __pycache__ or .cache, which mirrors nothing and is never checked."""
    return any(step.startswith(("_", ".")) for step in path)


def unmirrored(tests: str, root: str, each_root: tuple[str, ...], folders: Iterable[tuple[str, ...]],
               app: Collection[tuple[str, ...]]) -> list[Violation]:
    """Every folder below the tests of the `each` folder (tests/<each root>/) that mirrors no folder of the app.

    folders are below tests/<each root>/, app the app's folders below <each root>/; tests and root name the two
    roots in violations."""
    found: list[Violation] = []
    for folder in sorted(folders):
        if hidden(folder) or folder in app:
            continue
        mirrored = "/".join((root, *each_root, *folder))
        found.append(Violation("/".join((tests, *each_root, *folder)), 0,
                               f"mirrors no folder of the app ({mirrored})"))
    return found
