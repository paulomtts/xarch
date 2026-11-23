"""Where a file below the tests root sits: tests mirror the app, so a file's tier follows from the app part its
folder mirrors.

A file at tests/<path> mirrors the app's <path>. Its tier is, in order:
1. the first tier whose subject holds the part that claims <path> (below the subject's sub-path, if it names one);
2. else, when its folder is the folder of parts that are files (such as an application controller), the tier of those parts,
   if they share one;
3. else, the first tier whose `folder` holds it: the file lies in that folder or below it.
A file under the fakes' folder is a fake, which no tier holds. A file in none of these has no tier.

Its subject is the part its folder mirrors (1.), or the file parts of its folder (2.); a file placed by its tier's
folder (3.) mirrors no part and has none.

Its own folder is the instance of the repeating folder it mirrors (tests/<its root>/<name>/), else the top folder below
the tests root: the folder whose helpers it may import.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fnmatch import fnmatchcase

from xarch.kernel.logic.placement import place_of, stem
from xarch.kernel.placement import EACH, Place
from xarch.modules.rules.application.logic.places import instance_root, matches, targets_of
from xarch.modules.rules.domain.profile import Profile
from xarch.profile_values.placement import Target
from xarch.profile_values.tiers import CheckedTier

NO_TIER = "lies in no tier: no part's folder and no tier's `folder` is mirrored here"
NO_TIER_FIX = "move it to the folder that mirrors its subject's path in the app, or into a tier's `folder`"


@dataclass(frozen=True)
class Tested:
    """A file below the tests root: its tier (None if none), the instance of the repeating folder it is in, its own
    folder, whether it is a test (a name the profile's test files match) or a fake, and the parts it mirrors (its
    subject; empty when its tier was found by its tier's folder)."""
    tier: CheckedTier | None
    instance: str | None
    own: tuple[str, ...]
    is_test: bool
    is_fake: bool
    parts: tuple[str, ...] = ()


def _is_test(profile: Profile, path: tuple[str, ...]) -> bool:
    """Whether the file name matches one of the profile's test file patterns; no file is a test when it names none."""
    return bool(path) and profile.framework is not None and any(fnmatchcase(path[-1], pattern)
                                                                for pattern in profile.framework.files)


def tested(profile: Profile, path: tuple[str, ...]) -> Tested:
    fake = profile.fakes is not None and path[:len(profile.fakes.folder)] == profile.fakes.folder
    tier, instance, parts = (None, None, ()) if fake else _tier(profile, path)
    return Tested(tier, instance or _instance(profile, path), _own(profile, path), _is_test(profile, path), fake, parts)


def _tier(profile: Profile, path: tuple[str, ...]) -> tuple[CheckedTier | None, str | None, tuple[str, ...]]:
    where = place_of(profile.parts, path, profile.language.marks)
    if where.part is not None:
        tier = _first(profile, lambda t: any(s.part == where.part and where.sub[:len(s.sub)] == s.sub
                                             for s in t.subject))
        return tier, where.instance, (where.part,)
    folder = path[:-1]
    file_parts = [name for name, pattern in profile.parts.items()
                  if pattern and stem(pattern[-1], profile.language.marks) is not None
                  and matches(pattern[:-1], folder, profile.language.marks)]
    tiers = {id(t): t for name in file_parts for t in [_first(profile, lambda t, n=name: _tests(t, n))] if t}
    if len(tiers) == 1:
        instance = place_of({"": profile.parts[file_parts[0]][:-1]}, folder, profile.language.marks).instance
        return next(iter(tiers.values())), instance, tuple(file_parts)
    return _first(profile, lambda t: bool(t.folder) and folder[:len(t.folder)] == t.folder), None, ()


def _tests(tier: CheckedTier, part: str) -> bool:
    return any(s.part == part for s in tier.subject)


def _first(profile: Profile, wanted) -> CheckedTier | None:
    return next((t for t in profile.tiers if wanted(t)), None)


def _instance(profile: Profile, path: tuple[str, ...]) -> str | None:
    """The instance of a repeating folder the folder of a test file lies in."""
    folder = instance_root(profile.repeats, path[:-1])
    return folder[-1] if folder is not None else None


def _own(profile: Profile, path: tuple[str, ...]) -> tuple[str, ...]:
    """The folder a test file's own code is in: its instance's folder, else its top folder."""
    folder = instance_root(profile.repeats, path[:-1])
    if folder is not None:
        return folder
    return path[:1] if len(path) > 1 else ()


def _folder_imports(profile: Profile, tier: CheckedTier) -> tuple[Target, ...]:
    """What the tests in the tier's own folder may import: what the tier says, else its subject parts and what each of
    them may import; then what the tier's tests may also import."""
    if tier.imports_may is not None:
        return (*tier.imports_may, *tier.imports_also)
    return (*(replace(t, names="") for s in tier.subject for t in (s, *targets_of(profile, s.part))),
            *tier.imports_also)


def allowance(profile: Profile, where: Tested) -> tuple[Target, ...]:
    """What a test may import of the app: its subject parts and what each may import, else its tier's, then what its
    tier's tests may also import; a name pattern of a part's target does not narrow what its test imports."""
    assert where.tier is not None
    if not where.parts:
        return _folder_imports(profile, where.tier)
    own = tuple(Target(p, "own" if EACH in profile.parts[p] else "none") for p in where.parts)
    return (*(replace(t, names="") for s in own for t in (s, *targets_of(profile, s.part))), *where.tier.imports_also)


def may_use_fakes(profile: Profile, tier: CheckedTier) -> bool:
    """Whether the tests of the tier may import the fakes: its subject holds a part they stand in for."""
    return profile.fakes is not None and any(s.part in profile.fakes.stand_in_for for s in tier.subject)


def as_place(instance: str | None) -> Place:
    """The place a test speaks from: its repeating folder's instance, so that @own reaches that instance's parts."""
    return Place(EACH, instance)
