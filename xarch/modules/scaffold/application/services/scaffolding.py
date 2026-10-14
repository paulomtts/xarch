from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from xarch.modules.scaffold.application.ports.files import Files
from xarch.modules.scaffold.application.ports.skeleton import Skeleton
from xarch.modules.scaffold.contract import Report
from xarch.modules.scaffold.domain.errors import InvalidModuleName, ModuleExists, ModulesFolderMissing
from xarch.modules.scaffold.domain.names import valid_name
from xarch.modules.scaffold.domain.plan import holder, plan


class Scaffolding:
    def __init__(self, files: Files, skeleton: Skeleton):
        self._files, self._skeleton = files, skeleton

    def init(self, root: Path, profile: str) -> Report:
        report = self._build(root, self._skeleton.top_level(profile))
        base = holder(root)
        for rel, template in self._skeleton.docs(profile):           # the project docs, after the app
            self._write(base.joinpath(*rel), template, report)
        return report

    def new_module(self, root: Path, name: str, profile: str) -> Report:
        if not valid_name(name):
            raise InvalidModuleName(name)
        modules = root / "modules"
        if not self._files.is_dir(modules):
            raise ModulesFolderMissing(modules)                      # precondition: init ran
        base = modules / name
        if self._files.exists(base):
            raise ModuleExists(name, base)                           # precondition: nothing to overwrite
        return self._build(base, self._skeleton.module(profile))

    def _build(self, base: Path, entries: Iterable[tuple[tuple[str, ...], bool]]) -> Report:
        report = Report()
        for rel in plan(entries):
            self._write(base.joinpath(*rel), "", report)
        return report

    def _write(self, target: Path, text: str, report: Report) -> None:
        if self._files.exists(target):                               # never overwrite
            report.skipped.append(target)
            return
        if text:
            self._files.write_text(target, text)
        else:
            self._files.create_empty(target)
        report.created.append(target)
