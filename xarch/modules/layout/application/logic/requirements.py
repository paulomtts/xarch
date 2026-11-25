"""The structure rule: the folders and files that architecture.md section 1 requires to exist, at any depth, and what
is missing of them.

Only what is required is looked for: extra folders and files are none of the layout's business.
"""
from __future__ import annotations

from collections.abc import Collection, Iterable, Mapping

from xarch.kernel.logic.names import is_name, is_private_name
from xarch.kernel.violations import Violation
from xarch.modules.layout.domain.structure import Naming, Repeated, Requirement


def _is_instance_name(name: str, naming: Naming) -> bool:
    """Whether a folder found in a repeating folder's parent is an instance of it, not a cache or private folder: its
    name is a name of the language, and no private one."""
    return is_name(name, naming.names) and not is_private_name(name, naming.private)


def requirements(root: str, top_level: Iterable[tuple[str, ...]], repeated: Iterable[Repeated],
                 top_files: Iterable[tuple[str, ...]], naming: Naming,
                 when: Mapping[tuple[str, ...], tuple[str, ...]] | None = None) -> list[Requirement]:
    """What must exist: every folder the layout declares outside the repeating folders, at any depth, then every file
    it declares there, and every part of every instance found in each repeating folder's parent; when gives, for a
    path outside the repeating folders that lies in an optional part, that part's path, so that it is required only
    where that part is there (each repeating folder says the same of its parts)."""
    when = when or {}
    required = [Requirement(root, path, True, "/".join(path) + "/", when.get(path, ())) for path in top_level]
    required += [Requirement(root, path, False, "/".join(path), when.get(path, ())) for path in top_files]
    for each in repeated:
        parts = list(each.parts)
        for name in sorted(n for n in each.instances if _is_instance_name(n, naming)):
            owner = "/".join((root, *each.root, name))
            for path, is_dir in parts:
                shown = "/".join(path) + ("/" if is_dir else "")
                held = each.when.get(path)
                required.append(Requirement(owner, (*each.root, name, *path), is_dir, shown,
                                            (*each.root, name, *held) if held else ()))
    return required


def anchors(required: Iterable[Requirement]) -> list[Requirement]:
    """The optional parts the required lie in, each once, as the folders to look for."""
    return [_anchor(path) for path in dict.fromkeys(r.when for r in required if r.when)]


def missing(required: Iterable[Requirement], present: Collection[Requirement]) -> list[Violation]:
    """What is required and not present, but what lies in an optional part that is not present either."""
    return [Violation(r.owner, 0, f"missing {r.shown}", "structure", f"create {r.owner}/{r.shown}")
            for r in required if r not in present and (not r.when or _anchor(r.when) in present)]


def _anchor(path: tuple[str, ...]) -> Requirement:
    """The folder of an optional part, as looked for."""
    return Requirement("", path, True, "/".join(path) + "/")
