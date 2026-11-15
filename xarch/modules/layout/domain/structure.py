"""Structure rules: the folders and files that architecture.md section 1 requires to exist, at any depth.

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
    """Whether a folder found in a repeating folder's parent is an instance of it, not a cache or private folder."""
    return name.isidentifier() and not name.startswith("_")


@dataclass(frozen=True)
class Repeated:
    """A repeating folder: root, the folder holding its instances; parts, (path below an instance, is_dir) for what
    every instance holds; instances, the folders found in root."""
    root: tuple[str, ...]
    parts: Iterable[tuple[tuple[str, ...], bool]]
    instances: Iterable[str]


def requirements(root: str, top_level: Iterable[tuple[str, ...]], repeated: Iterable[Repeated],
                 top_files: Iterable[tuple[str, ...]] = ()) -> list[Requirement]:
    """What must exist: every folder the layout declares outside the repeating folders, at any depth, then every file
    it declares there, and every part of every instance found in each repeating folder's parent."""
    required = [Requirement(root, path, True, "/".join(path) + "/") for path in top_level]
    required += [Requirement(root, path, False, "/".join(path)) for path in top_files]
    for each in repeated:
        parts = list(each.parts)
        for name in sorted(n for n in each.instances if is_instance_name(n)):
            owner = "/".join((root, *each.root, name))
            for path, is_dir in parts:
                shown = "/".join(path) + ("/" if is_dir else "")
                required.append(Requirement(owner, (*each.root, name, *path), is_dir, shown))
    return required


def missing(required: Iterable[Requirement], present: Collection[Requirement]) -> list[Violation]:
    return [Violation(r.owner, 0, f"missing {r.shown}", "structure", f"create {r.owner}/{r.shown}")
            for r in required if r not in present]


def hidden(path: tuple[str, ...]) -> bool:
    """A folder such as __pycache__ or .cache, which mirrors nothing and is never checked."""
    return any(step.startswith(("_", ".")) for step in path)


def unmirrored(tests: str, root: str, each_root: tuple[str, ...], folders: Iterable[tuple[str, ...]],
               app: Collection[tuple[str, ...]]) -> list[Violation]:
    """Every folder below the tests of a repeating folder (tests/<its root>/) that mirrors no folder of the app.

    folders are below tests/<each root>/, app the app's folders below <each root>/; tests and root name the two
    roots in violations."""
    found: list[Violation] = []
    for folder in sorted(folders):
        if hidden(folder) or folder in app:
            continue
        mirrored = "/".join((root, *each_root, *folder))
        found.append(Violation("/".join((tests, *each_root, *folder)), 0,
                               f"mirrors no folder of the app ({mirrored})", "test-tree",
                               f"create {mirrored}/ in the app, or move what it holds to the folder that mirrors its "
                               "subject, or remove it"))
    return found
