"""The forbidden check: a file of a part neither imports a module the part's `forbidden` list names nor uses a name it
lists; a test of a tier marked `forbidden` is held to the list of the part it mirrors.

A listed entry is a dotted path: a call or attribute as an absolute import binds it (`datetime.datetime.now`), a
builtin as `builtins.<name>`, or a module by its import name (`socket`). What is read is what the file says:

    an import          `import a.b` imports a.b, `from a import x` imports a.x; it is reported when what it imports
                       is the entry or lies below it, so `import urllib.request` is `urllib`, `from time import time`
                       is `time.time`. Relative imports are the app's own.
    a use              a name read in the code, called or not, through the import that binds its first name (see
                       the Use value): `dt.now` after `from datetime import datetime as dt`, `datetime.datetime.now`
                       after `import datetime`, a bare `open` that no scope binds; it is reported when it reaches the
                       entry or below it, unless the import that binds it already imported the entry, which was
                       reported there.

It stays silent on what is not written in the file as such a name: a name reached through a variable or an
assignment (`clock = datetime.datetime; clock.now()`), through `getattr` or a string, through an object
(`Path(p).read_text()`), a builtin hidden by a star import, an annotation, and anything done on the part's behalf elsewhere: a
helper in another file, or a part with no list, may do the I/O the part asked for. It is a ban list of names, not a
proof that a part does no I/O.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.imports import dotted
from xarch.modules.rules.domain.places import label, place
from xarch.modules.rules.domain.values import Profile, SourceFile

RULE = "forbidden"


def violations(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile) -> list[Violation]:
    if not profile.forbidden:
        return []
    found: list[Violation] = []
    for file in app:
        where = place(profile, dotted(file.path)[0])
        if where is None or where.part not in profile.forbidden:
            continue
        found += _file(file, where.part, label(profile, where), f"({RULE}.{where.part})", profile)
    for file in tests:
        where = tested(profile, file.path)
        if where.tier is None or not where.tier.forbidden or where.is_fake:
            continue
        for part in where.parts:
            if part in profile.forbidden:
                found += _file(file, part, f"a test of {part}/ ({where.tier.name} tier)",
                               f"({RULE}.{part}; tiers.{where.tier.name}.{RULE})", profile)
    return found


def _file(file: SourceFile, part: str, who: str, tag: str, profile: Profile) -> Iterator[Violation]:
    names = profile.forbidden[part]
    seen: set[tuple[int, tuple[str, ...]]] = set()
    for line, verb, hit in [*_imports(file, names), *_uses(file, names)]:
        if (line, hit) in seen:
            continue
        seen.add((line, hit))
        shown = ".".join(hit)
        yield Violation(file.name, line, f"{who} may not {verb} {shown} {tag}", RULE,
                        f"do what needs {shown} outside {part}/, and hand {part}/ the result")


def _imports(file: SourceFile, names: tuple[tuple[str, ...], ...]) -> Iterator[tuple[int, str, tuple[str, ...]]]:
    for imp in file.imports:
        if imp.level:
            continue
        for path in [imp.module] if imp.names is None else [(*imp.module, name) for name in imp.names]:
            hit = _hit(path, names)
            if hit is not None:
                yield imp.line, "import", hit


def _uses(file: SourceFile, names: tuple[tuple[str, ...], ...]) -> Iterator[tuple[int, str, tuple[str, ...]]]:
    for use in file.uses:
        hit = _hit(use.name, names)
        if hit is not None and use.bound < len(hit):
            yield use.line, "use", hit


def _hit(path: tuple[str, ...], names: tuple[tuple[str, ...], ...]) -> tuple[str, ...] | None:
    """The first listed name that path is, or lies below."""
    return next((name for name in names if path[:len(name)] == name), None)
