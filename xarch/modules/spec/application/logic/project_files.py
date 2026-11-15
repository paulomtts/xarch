"""The project files beside the app: the files the architecture declares besides the docs, each filled from its template.

The architecture names every entry (`files: {<path>: {from, pinned, fill}}`, see profile_v2.py). A file entry
is its template; a folder entry (a key ending in `/`) is every file under its folder, written below the key with the
relative paths kept. `{{app}}` in a key is the name of the app folder, so an entry may land inside the app; in a text it
is replaced by the name when the entry is filled, and any other `{{...}}` is left alone: a template may hold code that
has its own braces. An entry that is not filled is copied byte for byte. The files are not part of the app's
structure: `check` does not require them, but a Python file that lands in a part is checked like any other.

What an entry may not do, inside the app folder: replace what the skeleton itself writes (a package file, a folder or a
file of the layout), or land on a file another entry writes.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass

from xarch.kernel.logic.placement import EACH
from xarch.modules.spec.application.logic.layout_walk import walk
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Architecture, ProjectFile

APP_PLACEHOLDER = "{{app}}"
"""The one placeholder of a project file's template: the name of the app folder."""
EXAMPLE_APP = "app"
"""The app folder's name in the docs' example project, which shows an example file with its placeholder filled."""
PACKAGE_FILE = "__init__.py"


@dataclass(frozen=True)
class Written:
    """One file `init` writes: its path below the folder holding the app, its content (text when filled, else the
    bytes as they are), whether the entry is pinned, and whether it comes from a folder entry."""
    path: tuple[str, ...]
    content: str | bytes
    pinned: bool = False
    preset: bool = False


def with_app(text: str, app: str) -> str:
    """The text with the placeholder replaced by the app folder's name."""
    return text.replace(APP_PLACEHOLDER, app)


def entries(architecture: Architecture, presets: bool) -> tuple[ProjectFile, ...]:
    """The entries `init` writes: every one, or with presets off only the file entries, leaving out what the folder
    entries copy."""
    return tuple(entry for entry in architecture.files if presets or not entry.folder)


def project_files(architecture: Architecture, contents: Mapping[str, str | bytes], app: str, source: str,
                  folders: Mapping[str, tuple[str, ...]] | None = None) -> Iterator[Written]:
    """Yield every file the architecture declares, in its order, a folder entry as each file under its folder.

    contents is each template file, by the name the architecture gives it, and each file of a folder by the folder's
    name, `/` and its path in the folder; folders lists the files of each folder, by its name; source names the
    architecture file in a problem. Raises InvalidArchitecture, with every problem found, for a file that is not
    text but is filled, one that would replace what the skeleton writes, or two that land on one path.
    """
    problems: list[str] = []
    found: list[Written] = []
    owners: dict[tuple[str, ...], str] = {}
    reserved = _Reserved(architecture, app)
    for entry in architecture.files:
        where = f"files.{'/'.join(entry.path)}{'/' if entry.folder else ''}"
        base = tuple(with_app(step, app) for step in entry.path)
        names = tuple((rel, f"{entry.source}/{rel}") for rel in (folders or {}).get(entry.source, ())) \
            if entry.folder else ((None, entry.source),)
        for rel, name in names:
            target = base + (tuple(rel.split("/")) if rel is not None else ())
            problem = reserved.problem(target)
            if problem is None and target in owners:
                problem = f"'{'/'.join(target)}' is also written by {owners[target]}"
            if problem is not None:
                problems.append(f"{where}: {problem}")
                continue
            owners[target] = where
            content = _content(contents[name], entry, app, name, where, problems)
            if content is not None:
                found.append(Written(target, content, entry.pinned, entry.folder))
    if problems:
        raise InvalidArchitecture(source, problems)
    yield from found


def _content(raw: str | bytes, entry: ProjectFile, app: str, name: str, where: str,
             problems: list[str]) -> str | bytes | None:
    if not entry.fill:
        return raw.encode() if isinstance(raw, str) else raw
    if isinstance(raw, str):
        return with_app(raw, app)
    try:
        return with_app(raw.decode("utf-8"), app)
    except UnicodeDecodeError:
        problems.append(f"{where}: '{name}' is not valid UTF-8 text: set `fill: false` to copy it unchanged")
        return None


class _Reserved:
    """What the skeleton writes for an app, as patterns below the app folder, `EACH` matching any instance."""

    def __init__(self, architecture: Architecture, app: str):
        self._app = app
        self._files: list[tuple[str, ...]] = [(PACKAGE_FILE,)]
        self._folders: list[tuple[str, ...]] = [()]
        for path, is_dir, _ in walk(architecture.layout):
            if is_dir:
                self._folders.append(path)
                self._files.append(path + (PACKAGE_FILE,))
            else:
                self._files.append(path)

    def problem(self, target: tuple[str, ...]) -> str | None:
        """What is wrong with a file landing at target (below the folder holding the app), or None."""
        if target[0] != self._app:
            return None
        inside = target[1:]
        shown = "/".join(target)
        if not inside:
            return f"'{shown}' is the app folder"
        for pattern in self._files:
            if _matches(pattern, inside):
                kind = "the package file the skeleton writes" if pattern[-1] == PACKAGE_FILE else "a file of the layout"
                return f"'{shown}' is {kind}"
            if len(inside) > len(pattern) and _matches(pattern, inside[:len(pattern)]):
                return f"'{'/'.join(target[:len(pattern) + 1])}' is a file of the layout"
        if any(_matches(pattern, inside) for pattern in self._folders):
            return f"'{shown}' is a folder of the layout"
        return None


def _matches(pattern: tuple[str, ...], path: tuple[str, ...]) -> bool:
    return len(pattern) == len(path) and all(want in (step, EACH) for want, step in zip(pattern, path))
