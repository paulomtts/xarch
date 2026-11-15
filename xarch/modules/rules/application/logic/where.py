"""Where a path sits and what code there may do, asked before the code is written: the same answers the checks give
afterwards, from the same profile.

A path is given from the working folder, the project root (the folder holding the app folder) or the app folder, and
may not exist yet; one that starts with `..` is the working folder's alone. `resolve` settles which of those it means, in
this order: what exists in the app or the tests, what exists elsewhere in the project, then what the app or the tests
would hold, then what the project would; a path that is in none of them is not placed. `describe` says what the path is:

  - in a part (PartPlace): the part's role and litmus test, the folders its code may import (its `rules`), the
    outside packages it may import, the names it may not use, and the kind of test that tests it with the file that
    test would be in;
  - in the structure (StructurePlace), or in no part (UngovernedPlace): which parts are near it, and for a place in
    no part whether the closed-tree guard is on;
  - below a folder the profile excludes, or outside the app and its tests: ungoverned, with why in the note;
  - below the tests root (SuitePlace, FakePlace): its tier (see tier_of), the part it mirrors, what it may import (the
    per-part rule of tier_imports), whether it may import the fakes, and what the tier proves and may touch.
"""
from __future__ import annotations

import os
from collections.abc import Collection, Iterable
from pathlib import Path

from xarch.kernel.logic.imports import may_import, shown_target
from xarch.kernel.logic.placement import EACH, Place, Target, matches, repeat_of
from xarch.kernel.logic.testing import TierView
from xarch.modules.rules.application.logic.places import place, targets_of
from xarch.modules.rules.application.logic.tier_of import NO_TIER, Tested, allowance, may_use_fakes, tested
from xarch.modules.rules.domain.values import (
    FakePlace,
    PartAt,
    PartInfo,
    PartPlace,
    Placed,
    Profile,
    Resolved,
    StructurePlace,
    SuitePlace,
    UngovernedPlace,
)

TESTS_FOLDER = "tests"
"""Where the tests are shown to be when no tests folder is known."""
SAMPLE = "x"
STAND_IN = "<name>"
OUTSIDE_NOTE = "it lies outside the app folder and the tests folder"
EXCLUDED_NOTE = "excluded from the checks by the profile"
FAKE_NOTE = "a test fake: it stands in for a port, and is no test"


def candidates(path: Path, cwd: Path, app: Path) -> tuple[Path, ...]:
    """Each path the given one may mean, from the working folder, the project root or the app folder, in that order,
    each once; a path that starts with `..` or is absolute is the working folder's alone."""
    root = app.parent
    bases = [cwd / path] if path.is_absolute() or path.parts[:1] == (os.pardir,) else [cwd / path, root / path, app / path]
    return tuple(dict.fromkeys(Path(os.path.normpath(b)) for b in bases))


def resolve(path: Path, cwd: Path, app: Path, tests: Path | None, existing: Collection[Path]) -> Resolved | None:
    """The path as the working folder, the project root or the app folder would have it, existing being those of its
    candidates that exist; None when it is outside the project."""
    root = app.parent
    found = [Resolved(within, base.relative_to(folder).parts, base, base in existing, _relative(base, root))
             for base in candidates(path, cwd, app)
             for within, folder in [_folder(base, app, tests, root)] if within is not None and folder is not None]
    for wanted in (lambda f: f.exists and f.within != "project", lambda f: f.exists, lambda f: f.within != "project",
                   lambda f: True):
        match = next((f for f in found if wanted(f)), None)
        if match is not None:
            return match
    return None


def _folder(path: Path, app: Path, tests: Path | None, root: Path) -> tuple[str | None, Path | None]:
    """Which folder holds the path: the app, the tests or the project."""
    for within, folder in (("app", app), ("tests", tests), ("project", root)):
        if folder is not None and path.is_relative_to(folder):
            return within, folder
    return None, None


def describe(profile: Profile, found: Resolved, app: Path, tests: Path | None) -> Placed:
    """What a resolved path is, and what code there may do."""
    root = app.parent
    if found.within == "tests":
        return _test(profile, found, _relative(tests, root) if tests is not None else TESTS_FOLDER, app.name)
    if found.within == "project":
        return UngovernedPlace(found, (), None, OUTSIDE_NOTE)
    return _app(profile, found, app.name, _relative(tests, root) if tests is not None else TESTS_FOLDER)


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()


def _app(profile: Profile, found: Resolved, app: str, tests: str) -> Placed:
    steps = found.steps
    for exclusion in profile.excluded:
        if steps[:len(exclusion.path)] == exclusion.path:
            return UngovernedPlace(found, (), None, f"{EXCLUDED_NOTE}: {exclusion.reason}")
    where = place(profile, steps)
    if where is None:
        nearest = _nearest(profile, steps, False, app)
        return UngovernedPlace(found, nearest, profile.closed_tree if nearest else None, "")
    if where.part is None:
        return StructurePlace(found, _nearest(profile, steps, True, app))
    part, info = where.part, profile.info.get(where.part)
    folders = {name: i.shown for name, i in profile.info.items()}
    targets = targets_of(profile, part)
    folder, name, tier = _mirror(profile, part, steps)
    return PartPlace(
        found, where, info or PartInfo(), _singular(profile, part), _reaches(profile, targets, where.instance, app),
        may_import(targets, folders, profile.words()),
        None if profile.libraries is None else profile.libraries.get(part, ()),
        tuple(".".join(n) for n in profile.forbidden.get(part, ())), tier,
        f"{tests}/{'/'.join(folder)}/".replace("//", "/") if tier else "", name if tier else "",
        info.untested if info and tier is None else "")


def _mirror(profile: Profile, part: str, steps: tuple[str, ...]) -> tuple[tuple[str, ...], str, TierView | None]:
    """The folder below the tests root that mirrors the path, the name of the test file there ("" when it is no
    source file) and the tier that tests it: the answer the tests' own mapping (tier_of) gives for that folder."""
    pattern = profile.framework.files[0] if profile.framework is not None and profile.framework.files else ""
    language = profile.language
    is_source = bool(steps) and steps[-1].endswith(language.extension)
    whole_file = profile.parts[part][-1].endswith(language.extension)
    folder = steps[:-1] if is_source else steps
    sample = pattern.replace("*", SAMPLE) if pattern else f"{SAMPLE}{language.extension}"
    tier = tested(profile, (*folder, sample)).tier
    if not pattern or not is_source or steps[-1] == language.package_file:
        return folder, "", tier
    stem = steps[-1].removesuffix(language.extension)
    if whole_file:
        stem = f"<{tier.one_file_per}>" if tier is not None and tier.one_file_per else STAND_IN
    return folder, pattern.replace("*", stem), tier


def _reaches(profile: Profile, targets: Iterable[Target], instance: str | None, app: str) -> tuple[PartAt, ...]:
    folders = {name: i.shown for name, i in profile.info.items()}
    reached = []
    for target in dict.fromkeys(targets):
        if target.part not in folders:
            continue
        steps = _concrete(profile, profile.parts[target.part], instance if target.scope == "own" else None)
        shown = shown_target(target, folders)
        slash = "/" if folders[target.part].endswith("/") and not target.sub else ""
        reached.append(PartAt(target, shown, f"{'/'.join((app, *steps, *target.sub))}{slash}"))
    return tuple(reached)


def _concrete(profile: Profile, pattern: tuple[str, ...], instance: str | None) -> tuple[str, ...]:
    """A part's pattern with its repeating step named: the instance, or a placeholder for any."""
    word = _word(profile, pattern)
    return tuple((instance or f"<{word}>") if step == EACH else step for step in pattern)


def _word(profile: Profile, pattern: tuple[str, ...]) -> str:
    """The word of the repeating folder a pattern lies in; "" if it lies in none."""
    repeat = repeat_of(profile.repeats, pattern)
    return repeat.word if repeat is not None else ""


def _word_of_instance(profile: Profile, where: Tested) -> str:
    """The word of the repeating folder a test's own folder is an instance of; "" if it is in none."""
    return next((r.word for r in profile.repeats if where.instance is not None and r.root == where.own[:-1]), "")


def _singular(profile: Profile, part: str) -> str:
    """The word of the part's repeating folder; for a part outside them, the profile's word when it has only one."""
    word = _word(profile, profile.parts[part]) if part in profile.parts else ""
    return word or (profile.repeats[0].word if len(profile.repeats) == 1 else "")


def _nearest(profile: Profile, steps: tuple[str, ...], exact: bool, app: str) -> tuple[PartAt, ...]:
    """The parts below the nearest folder of the layout that holds the path, or is the path, each in the scope of the
    instance it is in."""
    for depth in range(len(steps) if exact else len(steps) - 1, -1, -1):
        folder = next((f for f in profile.folders if matches(f, steps[:depth], profile.language.marks)), None)
        if folder is not None:
            break
    else:
        folder, depth = (), 0
    found = []
    for name, pattern in profile.parts.items():
        if len(pattern) > len(folder) and pattern[:len(folder)] == folder:
            shown = profile.info[name].shown if name in profile.info else name
            word = _word(profile, pattern)
            below = tuple(steps[i] if step == EACH and i < depth else f"<{word}>" if step == EACH else step
                          for i, step in enumerate(pattern))
            slash = "/" if shown.endswith("/") else ""
            found.append(PartAt(Target(name, "own" if EACH in pattern else "none"), shown,
                                f"{'/'.join((app, *below))}{slash}"))
    return tuple(found)


def _test(profile: Profile, found: Resolved, tests: str, app: str) -> Placed:
    where = tested(profile, found.steps)
    if where.is_fake:
        return FakePlace(found, _fakes(profile, tests), f"{tests}/", FAKE_NOTE)
    if where.tier is None:
        return SuitePlace(found, where.is_test, None, None, None, "", (), "", (), False, "", "",
                          NO_TIER if where.is_test else "")
    return _tier_place(profile, where, found, tests, app)


def _tier_place(profile: Profile, where: Tested, found: Resolved, tests: str, app: str) -> SuitePlace:
    assert where.tier is not None
    part = where.parts[0] if where.parts else ""
    folders = {name: i.shown for name, i in profile.info.items()}
    targets = tuple(dict.fromkeys(allowance(profile, where)))
    names = tuple(".".join(n) for p in where.parts for n in profile.forbidden.get(p, ())) if where.tier.forbidden else ()
    mirrored = Place(part, where.instance) if part else None
    return SuitePlace(found, where.is_test, where.tier, mirrored, profile.info.get(part) if part else None,
                      _word_of_instance(profile, where) or _singular(profile, part),
                      _reaches(profile, targets, where.instance, app), may_import(targets, folders, profile.words()),
                      names, may_use_fakes(profile, where.tier), _fakes(profile, tests),
                      f"{tests}/{'/'.join(where.own)}/" if where.own else f"{tests}/", "")


def _fakes(profile: Profile, tests: str) -> str:
    return f"{tests}/{'/'.join(profile.fakes.folder)}/" if profile.fakes is not None else ""
