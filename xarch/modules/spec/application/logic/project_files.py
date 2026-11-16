"""The project files beside the app: the files the architecture declares besides the docs, each filled from its template.

The architecture names every entry (`files: {<path>: {from, pinned, fill}}`, see profile_v2). A file entry
is its template; a folder entry (a key ending in `/`) is every file under its folder, written below the key with the
relative paths kept. `{{app}}` in a key is the name of the app folder, so an entry may land inside the app; in a text it
is replaced by the name when the entry is filled, and any other `{{...}}` is left alone: a template may hold code that
has its own braces. An entry that is not filled is copied byte for byte. The files are not part of the app's
structure: `check` does not require them, but a source file that lands in a part is checked like any other.

What an entry may not do, inside the app folder: replace what the skeleton itself writes (a package file, a folder or a
file of the layout), or land on a file another entry writes.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence

from xarch.kernel.placement import EACH
from xarch.modules.spec.application.logic.layout_walk import walk
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.published import ProjectFile
from xarch.modules.spec.domain.values import Architecture, FileEntry, Layout

APP_PLACEHOLDER = "{{app}}"
"""The one placeholder of a project file's template: the name of the app folder."""
EXAMPLE_APP = "app"
"""The app folder's name in the docs' example project, which shows an example file with its placeholder filled."""


def with_app(text: str, app: str) -> str:
    """The text with the placeholder replaced by the app folder's name."""
    return text.replace(APP_PLACEHOLDER, app)


def entries(architecture: Architecture, presets: bool) -> tuple[FileEntry, ...]:
    """The entries `init` writes: every one, or with presets off only the file entries, leaving out what the folder
    entries copy."""
    return tuple(entry for entry in architecture.files if presets or not entry.folder)


def project_files(architecture: Architecture, contents: Mapping[str, str | bytes], app: str, source: str,
                  folders: Mapping[str, tuple[str, ...]] | None = None) -> Iterator[ProjectFile]:
    """Yield every file the architecture declares, in its order, a folder entry as each file under its folder.

    contents is each template file, by the name the architecture gives it, and each file of a folder by the folder's
    name, `/` and its path in the folder; folders lists the files of each folder, by its name; source names the
    architecture file in a problem. Raises InvalidArchitecture, with every problem found, for a file that is not
    text but is filled, one that would replace what the skeleton writes, or two that land on one path.
    """
    problems: list[str] = []
    found: list[ProjectFile] = []
    owners: dict[tuple[str, ...], str] = {}
    package = architecture.language.checked.package_file
    files, folders_written = _skeleton_files(architecture.layout, package), _skeleton_folders(architecture.layout)
    for entry in architecture.files:
        where = f"files.{'/'.join(entry.path)}{'/' if entry.folder else ''}"
        base = tuple(with_app(step, app) for step in entry.path)
        names = tuple((rel, f"{entry.source}/{rel}") for rel in (folders or {}).get(entry.source, ())) \
            if entry.folder else ((None, entry.source),)
        for rel, name in names:
            target = base + (tuple(rel.split("/")) if rel is not None else ())
            problem = _problem(target, app, package, files, folders_written)
            if problem is None and target in owners:
                problem = f"'{'/'.join(target)}' is also written by {owners[target]}"
            if problem is not None:
                problems.append(f"{where}: {problem}")
                continue
            owners[target] = where
            content = _content(contents[name], entry, app, name, where, problems)
            if content is not None:
                found.append(ProjectFile(target, content, entry.pinned))
    if problems:
        raise InvalidArchitecture(source, problems)
    yield from found


def _content(raw: str | bytes, entry: FileEntry, app: str, name: str, where: str,
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


def _skeleton_files(layout: Layout, package: str) -> tuple[tuple[str, ...], ...]:
    """The files the skeleton writes, as patterns below the app folder, `EACH` matching any instance: the package file
    of each folder, the app folder's first, and each file of the layout."""
    return ((package,), *(entry.path + (package,) if entry.is_dir else entry.path for entry in walk(layout)))


def _skeleton_folders(layout: Layout) -> tuple[tuple[str, ...], ...]:
    """The folders the skeleton writes, as patterns below the app folder: the app folder itself, then each folder of
    the layout."""
    return ((), *(entry.path for entry in walk(layout) if entry.is_dir))


def _problem(target: tuple[str, ...], app: str, package: str, files: Sequence[tuple[str, ...]],
             folders: Sequence[tuple[str, ...]]) -> str | None:
    """What is wrong with a file landing at target (below the folder holding the app folder named app), given what the
    skeleton writes there, or None."""
    if target[0] != app:
        return None
    inside = target[1:]
    shown = "/".join(target)
    if not inside:
        return f"'{shown}' is the app folder"
    for pattern in files:
        if _matches(pattern, inside):
            kind = "the package file the skeleton writes" if pattern[-1] == package else "a file of the layout"
            return f"'{shown}' is {kind}"
        if len(inside) > len(pattern) and _matches(pattern, inside[:len(pattern)]):
            return f"'{'/'.join(target[:len(pattern) + 1])}' is a file of the layout"
    if any(_matches(pattern, inside) for pattern in folders):
        return f"'{shown}' is a folder of the layout"
    return None


def _matches(pattern: tuple[str, ...], path: tuple[str, ...]) -> bool:
    return len(pattern) == len(path) and all(want in (step, EACH) for want, step in zip(pattern, path))
