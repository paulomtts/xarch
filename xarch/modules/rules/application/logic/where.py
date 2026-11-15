"""Where a path sits and what code there may do, asked before the code is written: the same answers the checks give
afterwards, from the same profile.

A path is given from the working folder, the project root (the folder holding the app folder) or the app folder, and
may not exist yet; one that starts with `..` is the working folder's alone. `resolve` settles which of those it means, in
this order: what exists in the app or the tests, what exists elsewhere in the project, then what the app or the tests
would hold, then what the project would; a path that is in none of them is not placed. `describe` says what the path is:

  - in a part: the part's role and litmus test, the folders its code may import (its `rules`), the outside packages
    it may import, the names it may not use, and the kind of test that tests it with the file that test would be in;
  - in the structure, or in no part: which parts are near it, and whether the closed-tree guard is on;
  - below a folder the profile excludes: ungoverned, with the profile's reason in the note;
  - below the tests root: its tier (see tier_of), the part it mirrors, what it may import (the per-part rule of
    tier_imports), whether it may import the fakes, and what the tier proves and may touch.
"""
from __future__ import annotations

import os
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from xarch.kernel.logic.imports import may_import, shown_target
from xarch.kernel.logic.placement import EACH, Target, matches
from xarch.modules.rules.application.logic.tier_imports import NO_TIER, allowance, may_use_fakes
from xarch.modules.rules.application.logic.tier_of import Tested, tested
from xarch.modules.rules.domain.places import place, targets_of
from xarch.modules.rules.domain.values import Nearest, Profile, Reach, TestTier, TierInfo, Where

TESTS_FOLDER = "tests"
"""Where the tests are shown to be when no tests folder is known."""
FALLBACK_FILE = "x.py"
SAMPLE = "x"
STAND_IN = "<name>"
OUTSIDE_NOTE = "it lies outside the app folder and the tests folder"
EXCLUDED_NOTE = "excluded from the checks by the profile"
FAKE_NOTE = "a test fake: it stands in for a port, and is no test"


@dataclass(frozen=True)
class Resolved:
    """A path settled: which folder it lies in (app, tests or project), its steps below that folder, the path in full
    and whether it exists."""
    kind: str
    steps: tuple[str, ...]
    path: Path
    exists: bool


def resolve(path: Path, cwd: Path, app: Path, tests: Path | None, exists: Callable[[Path], bool]) -> Resolved | None:
    """The path as the working folder, the project root or the app folder would have it; None when it is outside the
    project."""
    root = app.parent
    bases = [cwd / path] if path.is_absolute() or path.parts[:1] == (os.pardir,) else [cwd / path, root / path, app / path]
    found = [Resolved(kind, base.relative_to(folder).parts, base, exists(base))
             for base in dict.fromkeys(Path(os.path.normpath(b)) for b in bases)
             for kind, folder in [_folder(base, app, tests, root)] if kind is not None and folder is not None]
    for wanted in (lambda f: f.exists and f.kind != "project", lambda f: f.exists, lambda f: f.kind != "project",
                   lambda f: True):
        match = next((f for f in found if wanted(f)), None)
        if match is not None:
            return match
    return None


def _folder(path: Path, app: Path, tests: Path | None, root: Path) -> tuple[str | None, Path | None]:
    """Which folder holds the path: the app, the tests or the project."""
    for kind, folder in (("app", app), ("tests", tests), ("project", root)):
        if folder is not None and path.is_relative_to(folder):
            return kind, folder
    return None, None


def describe(profile: Profile, found: Resolved, app: Path, tests: Path | None) -> Where:
    """What a resolved path is, and what code there may do."""
    root = app.parent
    shown = _relative(found.path, root)
    if found.kind == "tests":
        return _test(profile, found, shown, _relative(tests, root) if tests is not None else TESTS_FOLDER, app.name)
    if found.kind == "project":
        return Where("ungoverned", shown, found.exists, note=OUTSIDE_NOTE)
    return _app(profile, found, shown, app.name, _relative(tests, root) if tests is not None else TESTS_FOLDER)


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()


def _app(profile: Profile, found: Resolved, shown: str, app: str, tests: str) -> Where:
    steps = found.steps
    for exclusion in profile.excluded:
        if steps[:len(exclusion.path)] == exclusion.path:
            return Where("ungoverned", shown, found.exists, note=f"{EXCLUDED_NOTE}: {exclusion.reason}")
    where = place(profile, steps)
    if where is None or where.part is None:
        structure = where is not None
        return Where("structure" if structure else "ungoverned", shown, found.exists,
                     nearest=_nearest(profile, steps, structure, app), closed_tree=not structure and profile.closed_tree)
    part, info = where.part, profile.info.get(where.part)
    folders = {name: i.shown for name, i in profile.info.items()}
    targets = targets_of(profile, part)
    folder, name, tier = _mirror(profile, part, steps)
    return Where(
        "part", shown, found.exists, part, info.role if info else "", info.litmus if info else "",
        info.shown if info else "", where.instance or "", profile.singular,
        _reaches(profile, targets, where.instance, app), may_import(targets, folders, profile.singular),
        None if profile.libraries is None else profile.libraries.get(part, ()),
        tuple(".".join(n) for n in profile.forbidden.get(part, ())), _info(tier),
        info.untested if info and tier is None else "", f"{tests}/{'/'.join(folder)}/".replace("//", "/") if tier else "",
        name if tier else "")


def _mirror(profile: Profile, part: str, steps: tuple[str, ...]) -> tuple[tuple[str, ...], str, TestTier | None]:
    """The folder below the tests root that mirrors the path, the name of the test file there ("" when it is no
    Python file) and the tier that tests it: the answer the tests' own mapping (tier_of) gives for that folder."""
    pattern = profile.framework.files[0] if profile.framework is not None and profile.framework.files else ""
    is_python = bool(steps) and steps[-1].endswith(".py")
    whole_file = profile.parts[part][-1].endswith(".py")
    folder = steps[:-1] if is_python else steps
    sample = pattern.replace("*", SAMPLE) if pattern else FALLBACK_FILE
    tier = tested(profile, (*folder, sample)).tier
    if not pattern or not is_python or steps[-1] == "__init__.py":
        return folder, "", tier
    stem = steps[-1].removesuffix(".py")
    if whole_file:
        stem = f"<{tier.one_file_per}>" if tier is not None and tier.one_file_per else STAND_IN
    return folder, pattern.replace("*", stem), tier


def _info(tier: TestTier | None) -> TierInfo | None:
    return TierInfo(tier.name, tier.proves, tier.may_touch, tier.litmus) if tier is not None else None


def _reaches(profile: Profile, targets: Iterable[Target], instance: str | None, app: str) -> tuple[Reach, ...]:
    folders = {name: i.shown for name, i in profile.info.items()}
    reached = []
    for target in dict.fromkeys(targets):
        if target.part not in folders:
            continue
        steps = _concrete(profile.parts[target.part], instance if target.scope == "own" else None, profile.singular)
        shown = shown_target(target, folders)
        slash = "/" if folders[target.part].endswith("/") and not target.sub else ""
        reached.append(Reach(target.part, target.scope, shown, f"{'/'.join((app, *steps, *target.sub))}{slash}"))
    return tuple(reached)


def _concrete(pattern: tuple[str, ...], instance: str | None, singular: str) -> tuple[str, ...]:
    """A part's pattern with its `each` step named: the instance, or a placeholder for any."""
    return tuple((instance or f"<{singular}>") if step == EACH else step for step in pattern)


def _nearest(profile: Profile, steps: tuple[str, ...], exact: bool, app: str) -> tuple[Nearest, ...]:
    """The parts below the nearest folder of the layout that holds the path, or is the path."""
    for depth in range(len(steps) if exact else len(steps) - 1, -1, -1):
        folder = next((f for f in profile.folders if matches(f, steps[:depth])), None)
        if folder is not None:
            break
    else:
        folder, depth = (), 0
    found = []
    for name, pattern in profile.parts.items():
        if len(pattern) > len(folder) and pattern[:len(folder)] == folder:
            shown = profile.info[name].shown if name in profile.info else name
            below = tuple(steps[i] if step == EACH and i < depth else f"<{profile.singular}>" if step == EACH else step
                          for i, step in enumerate(pattern))
            slash = "/" if shown.endswith("/") else ""
            found.append(Nearest(name, shown, f"{'/'.join((app, *below))}{slash}"))
    return tuple(found)


def _test(profile: Profile, found: Resolved, shown: str, tests: str, app: str) -> Where:
    where = tested(profile, found.steps)
    if where.is_fake:
        return Where("fake", shown, found.exists, note=FAKE_NOTE, fakes_path=_fakes(profile, tests),
                     test_code_from=f"{tests}/")
    kind = "test" if where.is_test else "support"
    if where.tier is None:
        return Where(kind, shown, found.exists, note=NO_TIER if where.is_test else "")
    return _tier_place(profile, where, kind, shown, found.exists, tests, app)


def _tier_place(profile: Profile, where: Tested, kind: str, shown: str, exists: bool, tests: str, app: str) -> Where:
    assert where.tier is not None
    part = where.parts[0] if where.parts else ""
    info = profile.info.get(part)
    folders = {name: i.shown for name, i in profile.info.items()}
    targets = tuple(dict.fromkeys(allowance(profile, where)))
    names = tuple(".".join(n) for p in where.parts for n in profile.forbidden.get(p, ())) if where.tier.forbidden else ()
    return Where(kind, shown, exists, part, info.role if info else "", info.litmus if info else "",
                 info.shown if info else "", where.instance or "", profile.singular,
                 _reaches(profile, targets, where.instance, app), may_import(targets, folders, profile.singular),
                 forbidden=names, tier=_info(where.tier), may_use_fakes=may_use_fakes(profile, where.tier),
                 fakes_path=_fakes(profile, tests), types_only=where.tier.types_only,
                 test_code_from=f"{tests}/{'/'.join(where.own)}/" if where.own else f"{tests}/")


def _fakes(profile: Profile, tests: str) -> str:
    return f"{tests}/{'/'.join(profile.fakes.path)}/" if profile.fakes is not None else ""
