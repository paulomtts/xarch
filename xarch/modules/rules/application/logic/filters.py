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
    named-name        an import into the app of a name rather than of a whole file
    narrowed          an import whose target a target of the file's part reaches but for its name pattern
    permits-nothing   an import in a file of a part whose rules name no other part
    into-the-fakes    a test file's import into the fakes' folder
    into-a-test       a test file's import of another test file
    a-call            a call, rather than a reference
    mirroring         a fact of a test file that mirrors parts of the app
"""
from __future__ import annotations

from dataclasses import replace

from xarch.kernel.logic.placement import EVERYTHING, reaches
from xarch.modules.rules.application.logic.places import targets_of
from xarch.modules.rules.domain.rule import ALL, ANY, APP, STRUCTURE, TESTS, Facts, Found, Read, Scope
from xarch.modules.rules.domain.values import Profile


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
    fact, read = found.fact, found.read
    match name:
        case "absolute":
            return "relative" not in fact.traits
        case "has-a-path":
            return bool(fact.path)
        case "unheld":
            return "held" not in fact.traits
        case "placed":
            return fact.at is not None
        case "below-a-package":
            return fact.at is not None and bool(fact.at.sub)
        case "same-part-instance":
            return (read.place is not None and fact.at is not None and read.place.part == fact.at.part
                    and read.place.instance == fact.at.instance)
        case "own-package":
            return fact.path[:1] == (facts.root,)
        case "standard-unreserved":
            return "standard" in fact.traits and "".join(fact.path[:1]) not in profile.reserved
        case "reserved":
            return "".join(fact.path[:1]) in profile.reserved
        case "owned":
            return any("".join(fact.path[:1]) in packages and part != found.rule.part
                       for part, packages in (profile.libraries or {}).items())
        case "reserved-and-owned":
            return holds("reserved", found, facts, profile) and holds("owned", found, facts, profile)
        case "bound-by-the-import-that-hit":
            return fact.kind == "use" and found.hit is not None and fact.bound >= len(found.hit)
        case "own-code":
            return "relative" in fact.traits or fact.path[:1] in ((facts.root,), (facts.tests_root,))
        case "names-a-name":
            return fact.name is not None
        case "built-by-a-builder":
            return (read.place is not None and fact.at is not None
                    and read.place.part in profile.built_by.get(fact.at.part or "", ()))
        case "named-name":
            return fact.name is not None
        case "narrowed":
            return bool(narrowed(found, profile))
        case "permits-nothing":
            part = read.place.part if read.place is not None else None
            return not any(t.part != EVERYTHING for t in (targets_of(profile, part) if part is not None else ()))
        case "into-the-fakes":
            return profile.fakes is not None and fact.target[:len(profile.fakes.folder)] == profile.fakes.folder
        case "into-a-test":
            return fact.target in facts.test_files
        case "a-call":
            return fact.kind == "call"
        case "mirroring":
            return bool(read.mirrors)
    raise ValueError(f"no filter of a fact is named {name!r}")


def narrowed(found: Found, profile: Profile) -> tuple[str, ...]:
    """The name patterns of the targets of the file's part that reach the import's target but for their pattern, each
    once, in order."""
    read, fact = found.read, found.fact
    if read.place is None or read.place.part is None or fact.at is None:
        return ()
    src = read.place
    return tuple(dict.fromkeys(t.names for t in targets_of(profile, src.part)
                               if t.names and reaches(replace(t, names=""), src, fact.at)))
