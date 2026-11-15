from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from xarch.modules.scaffold.application.ports.files import Files
from xarch.modules.scaffold.application.ports.skeleton import Skeleton
from xarch.modules.scaffold.contract import Report
from xarch.modules.scaffold.domain.errors import AlreadyExists, FolderMissing, InvalidName, UnknownKind
from xarch.modules.scaffold.domain.names import valid_name
from xarch.modules.scaffold.domain.plan import app_name, holder, plan
from xarch.modules.scaffold.domain.pyproject import recorded_app, recorded_location, with_profile, with_setting

PYPROJECT = "pyproject.toml"


class Scaffolding:
    def __init__(self, files: Files, skeleton: Skeleton):
        self._files, self._skeleton = files, skeleton

    def init(self, root: Path, profile: str) -> Report:
        """The app's top level, then the profile (and the app folder, when it is not the default) recorded in the
        project's pyproject.toml, then the project docs and the profile's other project files."""
        files = self._skeleton.files(profile, app_name(root))
        report = self._build(root, self._skeleton.top_level(profile))
        base = holder(root)
        self._record(base, root, profile, report)
        for rel, template in self._skeleton.docs(profile):
            self._write(base.joinpath(*rel), template, report)
        for rel, text in files:
            self._write(base.joinpath(*rel), text, report)
        return report

    def new(self, root: Path, kind: str, name: str, profile: str) -> Report:
        """Refused unless the name is valid, the kind is declared, init ran and nothing would be overwritten."""
        if not valid_name(name):
            raise InvalidName(name)
        kinds = self._skeleton.kinds(profile)
        if kind not in kinds:
            raise UnknownKind(kind, kinds, {word: "/".join(path) for word, (path, _) in kinds.items()})
        folder, entries = kinds[kind]
        parent = root.joinpath(*folder)
        if not self._files.is_dir(parent):
            raise FolderMissing(parent)
        base = parent / name
        if self._files.exists(base):
            raise AlreadyExists(name, base)
        return self._build(base, entries)

    def _record(self, base: Path, root: Path, profile: str, report: Report) -> None:
        """Record the profile, then the app folder when it is not the default, after the profile: each only if the
        pyproject.toml does not already hold it, so that no value is ever rewritten."""
        found = self._files.find_upward(base.absolute(), PYPROJECT)
        target = base / PYPROJECT if found is None or found.parent == base.absolute() else found
        text = self._files.read_text(target) if found is not None else None
        app = recorded_app(root, target.parent)
        edited = with_profile(text, recorded_location(profile, target.parent))
        changed = with_setting(edited if edited is not None else text, "app", app, after="profile") \
            if app is not None else edited
        changed = changed if changed is not None else edited
        if changed is None:
            report.skipped.append(target)
            return
        self._files.write_text(target, changed)
        (report.created if found is None else report.updated).append(target)

    def _build(self, base: Path, entries: Iterable[tuple[tuple[str, ...], bool]]) -> Report:
        report = Report()
        for rel in plan(entries):
            self._write(base.joinpath(*rel), "", report)
        return report

    def _write(self, target: Path, text: str | bytes, report: Report) -> None:
        """Never overwrites: what exists is reported skipped."""
        if self._files.exists(target):
            report.skipped.append(target)
            return
        if isinstance(text, bytes):
            self._files.write_bytes(target, text)
        elif text:
            self._files.write_text(target, text)
        else:
            self._files.create_empty(target)
        report.created.append(target)
