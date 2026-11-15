"""The named filters of rules as data, each a question about a file or about a fact a rule found in it, and whether a
scope holds a file. A rule names them in its scope (where: of the file), in what it keeps, in what it exempts, and in
the condition of a saying; the names are a closed list, each with its meaning here.

Of a file:

    tiered            a test file of a tier
    untiered          a test file of no tier
    a-test            a file whose name the profile's test files match
    not-a-fake        a file below the tests root outside the fakes' folder

Of a fact:

    absolute          not named from the importing file's own folder
    has-a-path        an import that names a path (one of the importing file's own folder names none)
    unheld            a method called on something else than the object a method is called on, or what it holds
    placed            an import into the app whose target a part or a folder of the layout governs
    below-a-package   ... whose target lies below the folder of the part it is in
    same-part-instance... whose target lies in the file's own part and instance
    own-package       an import whose first step is the app's root package
    standard-unreserved an import of the standard library the profile does not reserve
    reserved          an import whose first step the profile reserves
    owned             an import of an outside package another part's libraries list
    reserved-and-owned both
    bound-by-the-import-that-hit  a use whose binding import already took the whole name it hit
    own-code          an import of the app's or the tests' own package, or a relative one
    names-a-name      an import of a name, not of a whole module
    built-by-a-builder a build in a file of a part the built class's part lists in its built_by
    narrowed          an import whose target a target of the file's part reaches but for its name pattern
    permits-nothing   an import in a file of a part whose rules name no other part
    into-the-fakes    a test file's import into the fakes' folder
    into-a-test       a test file's import of another test file
    a-call            a call, rather than a reference
    mirroring         a fact of a test file that mirrors parts of the app
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from xarch.kernel.logic.placement import EVERYTHING, reaches
from xarch.modules.rules.application.logic.places import targets_of
from xarch.modules.rules.domain.rule import ALL, ANY, APP, STRUCTURE, TESTS, Facts, Found, Read, Scope
from xarch.modules.rules.domain.values import Profile

Question = Callable[[Found, Facts, Profile], bool]
"""What a filter of a fact asks of a fact a rule found."""


def in_scope(scope: Scope, read: Read, facts: Facts, profile: Profile) -> bool:
    if scope.files != {False: APP, True: TESTS}[read.test] and scope.files != ALL:
        return False
    if scope.part == STRUCTURE and (read.test or read.place is None or read.place.part is not None):
        return False
    if scope.part not in (ANY, STRUCTURE) and not (scope.part in read.mirrors if read.test else
                                                   read.place is not None and read.place.part == scope.part):
        return False
    if scope.tier and read.tier != scope.tier:
        return False
    return all(_file(name, read) for name in scope.where)


def _file(name: str, read: Read) -> bool:
    match name:
        case "tiered":
            return bool(read.tier)
        case "untiered":
            return not read.tier
        case "a-test":
            return read.is_test
        case "not-a-fake":
            return not read.is_fake
    raise ValueError(f"no filter of a file is named {name!r}")


def holds(name: str, found: Found, facts: Facts, profile: Profile) -> bool:
    return question(name)(found, facts, profile)


def question(name: str) -> Question:
    """The question a filter of a fact asks, by its name."""
    asked = _FACT.get(name)
    if asked is None:
        raise ValueError(f"no filter of a fact is named {name!r}")
    return asked


def _absolute(found: Found, facts: Facts, profile: Profile) -> bool:
    return "relative" not in found.fact.traits


def _has_a_path(found: Found, facts: Facts, profile: Profile) -> bool:
    return bool(found.fact.path)


def _unheld(found: Found, facts: Facts, profile: Profile) -> bool:
    return "held" not in found.fact.traits


def _placed(found: Found, facts: Facts, profile: Profile) -> bool:
    return found.fact.at is not None


def _below_a_package(found: Found, facts: Facts, profile: Profile) -> bool:
    return found.fact.at is not None and bool(found.fact.at.sub)


def _same_part_instance(found: Found, facts: Facts, profile: Profile) -> bool:
    src, at = found.read.place, found.fact.at
    return src is not None and at is not None and src.part == at.part and src.instance == at.instance


def _own_package(found: Found, facts: Facts, profile: Profile) -> bool:
    return found.fact.path[:1] == (facts.root,)


def _standard_unreserved(found: Found, facts: Facts, profile: Profile) -> bool:
    return "standard" in found.fact.traits and "".join(found.fact.path[:1]) not in profile.reserved


def _reserved(found: Found, facts: Facts, profile: Profile) -> bool:
    return "".join(found.fact.path[:1]) in profile.reserved


def _owned(found: Found, facts: Facts, profile: Profile) -> bool:
    top = "".join(found.fact.path[:1])
    return any(top in packages and part != found.rule.part for part, packages in (profile.libraries or {}).items())


def _reserved_and_owned(found: Found, facts: Facts, profile: Profile) -> bool:
    return _reserved(found, facts, profile) and _owned(found, facts, profile)


def _bound_by_the_import_that_hit(found: Found, facts: Facts, profile: Profile) -> bool:
    return found.fact.kind == "use" and found.hit is not None and found.fact.bound >= len(found.hit)


def _own_code(found: Found, facts: Facts, profile: Profile) -> bool:
    return "relative" in found.fact.traits or found.fact.path[:1] in ((facts.root,), (facts.tests_root,))


def _names_a_name(found: Found, facts: Facts, profile: Profile) -> bool:
    return found.fact.name is not None


def _built_by_a_builder(found: Found, facts: Facts, profile: Profile) -> bool:
    src, at = found.read.place, found.fact.at
    return src is not None and at is not None and src.part in profile.built_by.get(at.part or "", ())


def _narrowed(found: Found, facts: Facts, profile: Profile) -> bool:
    return bool(narrowed(found, profile))


def _permits_nothing(found: Found, facts: Facts, profile: Profile) -> bool:
    part = found.read.place.part if found.read.place is not None else None
    return not any(t.part != EVERYTHING for t in (targets_of(profile, part) if part is not None else ()))


def _into_the_fakes(found: Found, facts: Facts, profile: Profile) -> bool:
    return profile.fakes is not None and found.fact.target[:len(profile.fakes.folder)] == profile.fakes.folder


def _into_a_test(found: Found, facts: Facts, profile: Profile) -> bool:
    return found.fact.target in facts.test_files


def _a_call(found: Found, facts: Facts, profile: Profile) -> bool:
    return found.fact.kind == "call"


def _mirroring(found: Found, facts: Facts, profile: Profile) -> bool:
    return bool(found.read.mirrors)


_FACT = {"absolute": _absolute, "has-a-path": _has_a_path, "unheld": _unheld, "placed": _placed,
         "below-a-package": _below_a_package, "same-part-instance": _same_part_instance, "own-package": _own_package,
         "standard-unreserved": _standard_unreserved, "reserved": _reserved, "owned": _owned,
         "reserved-and-owned": _reserved_and_owned, "bound-by-the-import-that-hit": _bound_by_the_import_that_hit,
         "own-code": _own_code, "names-a-name": _names_a_name, "built-by-a-builder": _built_by_a_builder,
         "narrowed": _narrowed, "permits-nothing": _permits_nothing, "into-the-fakes": _into_the_fakes,
         "into-a-test": _into_a_test, "a-call": _a_call, "mirroring": _mirroring}
"""Each filter of a fact by its name, the question it asks."""


def narrowed(found: Found, profile: Profile) -> tuple[str, ...]:
    """The name patterns of the targets of the file's part that reach the import's target but for their pattern, each
    once, in order."""
    read, fact = found.read, found.fact
    if read.place is None or read.place.part is None or fact.at is None:
        return ()
    src = read.place
    return tuple(dict.fromkeys(t.names for t in targets_of(profile, src.part)
                               if t.names and reaches(replace(t, names=""), src, fact.at)))
