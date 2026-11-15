"""The tier-imports check: a test imports only what the part it mirrors may import, by the rules.

A file below the tests root that has a tier (see tier_of) may import, of the app, the part its folder mirrors (its
subject, see tier_of) and whatever that part may import under `rules`, where @own means the instance of the `each`
folder the test mirrors; a file in the folder of file parts (such as an application controller) has those parts as its
subject. A file with no subject, placed by its tier's folder (such as the guard tier's), may import its
tier's subject parts and whatever those may import. Of the test code, it may import the fakes only when its tier's
subject holds a part the fakes stand in for, and any other file only from its own folder (see tier_of), never a test
file (a file whose name the profile's test files match): what tests share lives in test code that is no test. A test
file that has no tier is a violation; any other file with no tier (a shared configuration or a builders file above every part's
folder) and the fakes are not checked. Imports of the standard library and outside packages are not this check's
business.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import replace

from xarch.kernel.logic.placement import EACH, Target, reaches
from xarch.kernel.logic.testing import TierView
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.imports import dotted, targets
from xarch.modules.rules.application.logic.places import label, place, targets_of
from xarch.modules.rules.application.logic.tier_of import Tested, as_place, is_test, tested
from xarch.modules.rules.domain.values import Profile, SourceFile

NO_TIER = "lies in no tier: no part's folder and no tier's `folder` is mirrored here"
NO_TIER_FIX = "move it to the folder that mirrors its subject's path in the app, or into a tier's `folder`"
RULE = "tiers"


def may_import(profile: Profile, tier: TierView) -> tuple[Target, ...]:
    """What the tests in the tier's own folder may import: what the tier says, else its subject parts and what each of
    them may import."""
    if tier.may_import is not None:
        return tier.may_import
    return tuple(replace(t, names="") for s in tier.subject for t in (s, *targets_of(profile, s.part)))


def allowance(profile: Profile, where: Tested) -> tuple[Target, ...]:
    """What a test may import of the app: its subject parts and what each may import, else its tier's; a name pattern
    of a part's target does not narrow what its test imports."""
    if not where.parts:
        assert where.tier is not None
        return may_import(profile, where.tier)
    own = tuple(Target(p, "own" if EACH in profile.parts[p] else "none") for p in where.parts)
    return tuple(replace(t, names="") for s in own for t in (s, *targets_of(profile, s.part)))


def may_use_fakes(profile: Profile, tier: TierView) -> bool:
    return profile.fakes is not None and any(s.part in profile.fakes.stand_in_for for s in tier.subject)


def violations(tests: Iterable[SourceFile], app: Iterable[SourceFile], profile: Profile, root: str,
               tests_root: str) -> list[Violation]:
    """tests are the files below the tests root, imported as the package tests_root; app the app's files, below the
    root package root."""
    if not profile.tiers:
        return []
    tests = list(tests)
    known_app = {dotted(f.path, profile.language.marks)[0] for f in app}
    known_tests = {dotted(f.path, profile.language.marks)[0] for f in tests}
    test_files = {dotted(f.path, profile.language.marks)[0] for f in tests if is_test(profile, f.path)}
    found: list[Violation] = []
    for file in tests:
        where = tested(profile, file.path)
        if where.tier is None:
            if where.is_test and not where.is_fake:
                found.append(Violation(file.name, 0, NO_TIER, RULE, NO_TIER_FIX))
            continue
        found += _app_imports(file, where, profile, root, known_app)
        found += _test_imports(file, where, profile, tests_root, known_tests, test_files)
    return found


def _app_imports(file: SourceFile, where: Tested, profile: Profile, root: str,
                 known: set[tuple[str, ...]]) -> Iterator[Violation]:
    assert where.tier is not None
    allowed = allowance(profile, where)
    subject = " and ".join(f"{p}/" for p in where.parts)
    why = (f": it imports only what {subject} may ({', '.join(f'parts.{p}.may_import' for p in where.parts)})"
           if where.parts else "")
    test = f"a test of {subject} ({where.tier.name} tier)" if where.parts else f"a {where.tier.name} test"
    absolute = tuple(i for i in file.imports if not i.level)
    for line, target in targets(absolute, (), known, root):
        dst = place(profile, target)
        if dst is not None and not any(reaches(t, as_place(where.instance), dst) for t in allowed):
            yield Violation(file.name, line, f"{test} may not import {label(profile, dst)} "
                                             f"({'.'.join((root, *target))}){why}", RULE,
                            f"import here only what {subject or f'the subject of the {where.tier.name} tier'} may; "
                            f"test {label(profile, dst)} from the folder that mirrors it")


def _test_imports(file: SourceFile, where: Tested, profile: Profile, tests_root: str,
                  known: set[tuple[str, ...]], test_files: set[tuple[str, ...]]) -> Iterator[Violation]:
    assert where.tier is not None
    steps, is_package = dotted(file.path, profile.language.marks)
    seen: set[tuple[int, tuple[str, ...]]] = set()
    for line, target in targets(file.imports, steps if is_package else steps[:-1], known, tests_root):
        shown = ".".join((tests_root, *target))
        if profile.fakes is not None and target[:len(profile.fakes.folder)] == profile.fakes.folder:
            if not may_use_fakes(profile, where.tier):
                parts = ", ".join(profile.fakes.stand_in_for)
                yield Violation(file.name, line, f"a {where.tier.name} test may not import the fakes ({shown}): only "
                                                 f"a tier that tests {parts} may", RULE,
                                f"drop the import of {shown}, or move the test to a tier that tests {parts}")
        elif target in test_files:
            if (line, target) in seen:
                continue
            seen.add((line, target))
            yield Violation(file.name, line, f"a test may not import another test file ({shown}): what tests share "
                                             "lives in test code that is no test file", RULE,
                            f"move what {shown} holds that this test needs into test code of its folder that is no "
                            "test file, and import it from there")
        elif target[:len(where.own)] != where.own or not where.own:
            own = "/".join((tests_root, *where.own))
            yield Violation(file.name, line, f"a test may import test code only from its own folder {own}/ "
                                             f"({shown})", RULE,
                            f"move what {shown} holds into {own}/, or drop the import")

