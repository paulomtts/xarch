from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic import baseline
from xarch.modules.rules.application.logic.chosen import chosen
from xarch.modules.rules.application.logic.ordered import ordered
from xarch.modules.rules.application.logic.verdict import passed
from xarch.modules.rules.application.ports.baseline import Baselines
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.application.ports.structure import Structure
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.contract import (
    BASELINE,
    AppChecked,
    BaselineWritten,
    EnforcementView,
    FindingView,
    Partial,
)
from xarch.modules.rules.domain.errors import RootMissing, StrictAgainst
from xarch.modules.rules.domain.outcomes import Finding

RECORD = (".xarch", "baseline.json")
"""The file the baseline is recorded in, below the folder holding the app."""


class AppCheckService:
    """The whole check of an app folder: what its source says, then whether its structure is there, under the profile
    in force; the app is imported as the package its folder names."""

    def __init__(self, source: SourceCheckService, structure: Structure, tree: SourceTree, baselines: Baselines):
        self._source, self._structure, self._tree, self._baselines = source, structure, tree, baselines

    def check(self, root: Path, profile: str, tests: Path | None, cwd: Path, strict: bool,
              against: str | None = None, paths: tuple[Path, ...] | None = None) -> AppChecked:
        """The violations of the source and of the structure, in order of file, line and rule, a relative root or
        tests folder read from cwd, the working folder; whether the check passes, under strict too on the findings of
        its enforcement. Raises StrictAgainst, before anything is looked at, when strict is asked with against, and
        RootMissing, with the folder as given, when the app folder or the tests folder is no folder. With paths, each
        read from cwd, every check still runs on the whole app and its tests, and the violations of files at or below
        them alone are shown and decide whether it passes; the others are counted. With a baseline recorded beside the app
        (RECORD), the violations it holds back are counted, not shown, before the paths choose; under strict, one that
        records more than is found fails."""
        if strict and against is not None:
            raise StrictAgainst()
        app, tested, hints, violations, view, found = self._found(root, profile, tests, cwd)
        record = self._baselines.read(app.parent.joinpath(*RECORD))
        if record is not None:
            applied = baseline.applied(violations, record, "/".join(RECORD))
            violations, standing = list(applied.shown), applied.standing
            if standing.below:
                detail = (f"{standing.below} finding(s) below baseline ({'/'.join(RECORD)}): run `xarch baseline write` "
                          "to lower it")
                found = [*found, Finding(BASELINE, detail)]
                view = replace(view, strict=(*view.strict, FindingView(BASELINE, detail)))
            view = replace(view, baseline=standing)
        partial = None
        if paths is not None:
            places = [self._tree.resolved(cwd, path) for path in dict.fromkeys(paths)]
            violations, elsewhere = chosen(violations, places, app.parent, tested)
            partial = Partial(tuple(path.as_posix() for path in paths), elsewhere)
        return AppChecked(tuple(violations), view, hints, passed(violations, found, strict), partial)

    def write_baseline(self, root: Path, profile: str, tests: Path | None, cwd: Path, reset: bool) -> BaselineWritten:
        """Record what a whole check finds now in the baseline beside the app: with reset, or with no record, every
        violation; else the record lowered to what is found. Raises RootMissing as check does."""
        app, _, _, violations, _, _ = self._found(root, profile, tests, cwd)
        file = app.parent.joinpath(*RECORD)
        before = self._baselines.read(file)
        findings = baseline.recorded(violations) if reset or before is None else baseline.lowered(before, violations)
        self._baselines.write(file, findings)
        return BaselineWritten("/".join(RECORD), sum(f.count for f in findings),
                               None if before is None else sum(f.count for f in before), reset)

    def _found(self, root: Path, profile: str, tests: Path | None,
               cwd: Path) -> tuple[Path, Path | None, dict[str, str], list[Violation], EnforcementView, list[Finding]]:
        """The app and tests folders in full, the profile's hints, every violation of the source and of the structure
        in order, the enforcement as shown and the findings strict fails on; raises RootMissing with the folder as
        given."""
        app, tested = cwd / root, (cwd / tests if tests is not None else None)
        absent = self._tree.absent(folder for folder in (app, tested) if folder is not None)
        if absent:
            raise RootMissing(root if absent[0] == app else tests)
        app, tested = self._tree.resolved(cwd, root), (self._tree.resolved(cwd, tests) if tests is not None else None)
        package = app.name
        checked = self._source.check(app, package, profile, tested)
        structure = self._structure.checked(app, package, profile, tested)
        violations = list(ordered((*checked.violations, *structure.violations)))
        view = self._source.view(replace(checked.enforcement,
                                         excused=(*checked.enforcement.excused, *structure.excused)))
        return app, tested, dict(checked.profile.hints), violations, view, list(checked.enforcement.strict)
