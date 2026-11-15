"""Where a file below the tests root sits: tests mirror the app, so a file's tier follows from the app part its
folder mirrors.

A file at tests/<path> mirrors the app's <path>. Its tier is, in order:
1. the first tier whose subject holds the part that claims <path> (below the subject's sub-path, if it names one);
2. else, when its folder is the folder of parts that are files (such as a controller.py), the tier of those parts,
   if they share one;
3. else, the first tier whose example test lies in its folder or a folder above it.
A file under the fakes' folder is a fake, which no tier holds. A file in none of these has no tier.

Its subject is the part its folder mirrors (1.), or the file parts of its folder (2.); a file placed by its tier's
example folder (3.) mirrors no part and has none.

Its own folder is the instance of the `each` folder it mirrors (tests/<each root>/<name>/), else the top folder below
the tests root: the folder whose helpers it may import.
"""
from __future__ import annotations

from dataclasses import dataclass

from xarch.kernel.logic.placement import EACH, Place, matches, place_of
from xarch.modules.rules.domain.values import Profile, TestTier


@dataclass(frozen=True)
class Tested:
    """A file below the tests root: its tier (None if none), the instance of the `each` folder it is in, its own
    folder, whether it is a test (test_*.py or *_test.py) or a fake, and the parts it mirrors (its subject; empty
    when its tier was found by its example's folder)."""
    tier: TestTier | None
    instance: str | None
    own: tuple[str, ...]
    is_test: bool
    is_fake: bool
    parts: tuple[str, ...] = ()


def is_test(path: tuple[str, ...]) -> bool:
    return bool(path) and (path[-1].startswith("test_") or path[-1].endswith("_test.py"))


def tested(profile: Profile, path: tuple[str, ...]) -> Tested:
    fake = profile.fakes is not None and path[:len(profile.fakes.path)] == profile.fakes.path
    tier, instance, parts = (None, None, ()) if fake else _tier(profile, path)
    return Tested(tier, instance or _instance(profile, path), _own(profile, path), is_test(path), fake, parts)


def _tier(profile: Profile, path: tuple[str, ...]) -> tuple[TestTier | None, str | None, tuple[str, ...]]:
    where = place_of(profile.parts, path)
    if where.part is not None:
        tier = _first(profile, lambda t: any(s.part == where.part and where.sub[:len(s.sub)] == s.sub
                                             for s in t.subject))
        return tier, where.instance, (where.part,)
    folder = path[:-1]
    file_parts = [name for name, pattern in profile.parts.items()
                  if pattern and pattern[-1].endswith(".py") and matches(pattern[:-1], folder)]
    tiers = {id(t): t for name in file_parts for t in [_first(profile, lambda t, n=name: _tests(t, n))] if t}
    if len(tiers) == 1:
        instance = place_of({"": profile.parts[file_parts[0]][:-1]}, folder).instance
        return next(iter(tiers.values())), instance, tuple(file_parts)
    return _first(profile, lambda t: t.folder is not None and folder[:len(t.folder)] == t.folder), None, ()


def _tests(tier: TestTier, part: str) -> bool:
    return any(s.part == part for s in tier.subject)


def _first(profile: Profile, wanted) -> TestTier | None:
    return next((t for t in profile.tiers if wanted(t)), None)


def _instance(profile: Profile, path: tuple[str, ...]) -> str | None:
    root = profile.each_root
    if root is None or len(path) <= len(root) + 1 or path[:len(root)] != root:
        return None
    return path[len(root)]


def _own(profile: Profile, path: tuple[str, ...]) -> tuple[str, ...]:
    instance = _instance(profile, path)
    if instance is not None and profile.each_root is not None:
        return (*profile.each_root, instance)
    return path[:1] if len(path) > 1 else ()


def as_place(instance: str | None) -> Place:
    """The place a test speaks from: its `each` instance, so that @own reaches that instance's parts."""
    return Place(EACH, instance)
