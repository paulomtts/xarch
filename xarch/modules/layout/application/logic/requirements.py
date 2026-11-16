"""The structure rule: the folders and files that architecture.md section 1 requires to exist, at any depth, and what
is missing of them.

Only what is required is looked for: extra folders and files are none of the layout's business.
"""
from __future__ import annotations

from collections.abc import Collection, Iterable

from xarch.kernel.logic.names import is_public_name
from xarch.kernel.violations import Violation
from xarch.modules.layout.domain.structure import Naming, Repeated, Requirement


def is_instance_name(name: str, naming: Naming) -> bool:
    """Whether a folder found in a repeating folder's parent is an instance of it, not a cache or private folder: its
    name is a name of the language, and no private one."""
    return is_public_name(name, naming.names, naming.private)


def requirements(root: str, top_level: Iterable[tuple[str, ...]], repeated: Iterable[Repeated],
                 top_files: Iterable[tuple[str, ...]], naming: Naming) -> list[Requirement]:
    """What must exist: every folder the layout declares outside the repeating folders, at any depth, then every file
    it declares there, and every part of every instance found in each repeating folder's parent."""
    required = [Requirement(root, path, True, "/".join(path) + "/") for path in top_level]
    required += [Requirement(root, path, False, "/".join(path)) for path in top_files]
    for each in repeated:
        parts = list(each.parts)
        for name in sorted(n for n in each.instances if is_instance_name(n, naming)):
            owner = "/".join((root, *each.root, name))
            for path, is_dir in parts:
                shown = "/".join(path) + ("/" if is_dir else "")
                required.append(Requirement(owner, (*each.root, name, *path), is_dir, shown))
    return required


def missing(required: Iterable[Requirement], present: Collection[Requirement]) -> list[Violation]:
    return [Violation(r.owner, 0, f"missing {r.shown}", "structure", f"create {r.owner}/{r.shown}")
            for r in required if r not in present]
