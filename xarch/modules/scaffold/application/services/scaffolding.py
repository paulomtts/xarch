from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from xarch.modules.scaffold.application.logic.names import valid_name
from xarch.modules.scaffold.application.logic.plan import app_name, holder, plan
from xarch.modules.scaffold.application.logic.pyproject_record import (
    pyproject_target,
    recorded_app,
    recorded_location,
    recorded_text,
)
from xarch.modules.scaffold.application.ports.files import Files
from xarch.modules.scaffold.application.ports.skeleton import Skeleton
from xarch.modules.scaffold.domain.errors import AlreadyExists, FolderMissing, InvalidName, UnknownKind
from xarch.modules.scaffold.domain.values import CREATED, FOLDER, SKIPPED, UPDATED, Touched


class ScaffoldingService:
    def __init__(self, files: Files, skeleton: Skeleton):
        self._files, self._skeleton = files, skeleton

    def init(self, root: Path, profile: str) -> list[Touched]:
        """The app's top level, then the profile (and the app folder, when it is not the default) recorded in the
        project's pyproject.toml, then the project docs and the profile's other project files, in the order each
        file is reached."""
        absolute = root.absolute()
        files = self._skeleton.files(profile, app_name(root, absolute.resolve()))
        package = self._skeleton.package_file(profile)
        touched = self._build(root, self._skeleton.top_level(profile), package)
        base = holder(root, absolute)
        touched.append(self._record(base, root, profile))
        for rel, template in self._skeleton.docs(profile):
            touched.append(self._write(base.joinpath(*rel), template))
        for rel, text in files:
            touched.append(self._write(base.joinpath(*rel), text))
        return touched

    def new(self, root: Path, kind: str, name: str, profile: str) -> list[Touched]:
        """Refused unless the name is valid, the kind is declared, init ran and nothing would be overwritten."""
        if not valid_name(name, self._skeleton.reserved(profile)):
            raise InvalidName(name, self._skeleton.language(profile))
        kinds = self._skeleton.kinds(profile)
        if kind not in kinds:
            raise UnknownKind(kind, kinds, {word: "/".join(path) for word, (path, _) in kinds.items()})
        folder, entries = kinds[kind]
        parent = root.joinpath(*folder)
        if self._files.kind(parent) != FOLDER:
            raise FolderMissing(parent)
        base = parent / name
        if self._files.kind(base) is not None:
            raise AlreadyExists(name, base)
        return self._build(base, entries, self._skeleton.package_file(profile))

    def _record(self, base: Path, root: Path, profile: str) -> Touched:
        """Record the profile, then the app folder when it is not the default, in the pyproject.toml of the project."""
        absolute = base.absolute()
        found = self._files.pyproject(absolute)
        target = pyproject_target(found[0] if found is not None else None, base, absolute)
        cwd = Path.cwd()
        changed = recorded_text(found[1] if found is not None else None,
                                recorded_location(profile, target.parent, cwd), recorded_app(root, target.parent, cwd))
        if changed is None:
            return Touched(target, SKIPPED)
        self._files.lay_down(target, changed)
        return Touched(target, CREATED if found is None else UPDATED)

    def _build(self, base: Path, entries: Iterable[tuple[tuple[str, ...], bool]], package_file: str) -> list[Touched]:
        return [self._write(base.joinpath(*rel), "") for rel in plan(entries, package_file)]

    def _write(self, target: Path, content: str | bytes) -> Touched:
        """Never overwrites: what exists is reported skipped."""
        if self._files.kind(target) is not None:
            return Touched(target, SKIPPED)
        self._files.lay_down(target, content)
        return Touched(target, CREATED)
