"""The named filters of rules as data, each a question about a file or about a fact a rule found in it, and whether a
scope holds a file. A rule names them in its scope (where: of the file), in what it keeps, in what it exempts, and in
the condition of a saying; the names are a closed list, each with its meaning here.

Of a file:

    tiered            a test file of a tier
    untiered          a test file of no tier
    a-test            a file whose name the profile's test files match
    not-a-fake        a file below the tests root outside the fakes' folder
    not-a-package     a file that does not stand for its folder
    ungoverned        a file of the app that no part and no folder of the layout governs
    not-a-package-file a file whose name is not the language's package file
    not-wiring        a file of no part that may import everything (the wiring, which only binds what others use)
    in-the-fakes      a file below the fakes' folder; not-in-the-fakes, a test file outside it
    tested-by-a-tier  a file of the app whose part a tier tests
    another-file      a root other than the file of the declaration it reaches (see engine)

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
    public            a declaration whose name is public in the language of the app
    top-level         a function defined at the top level, in no class
    annotated         a callback of a parameter annotated as a callable
    receiver          a callback of the first parameter of a method, the object or class it is called on
    exception         a class that is an exception (see facts)
    record            a class that is a record (see facts)
    read-by-a-tool    a comment the language's tools read: a directive after the comment marker (a space in one
                      standing for any spaces), a shebang on line 1, an encoding declaration on line 1 or 2
    a-package-file    the file a fact is in is named as the language's package file; a-package, it stands for its
                      folder
    no-code           a file no function or method of which holds a real statement
    exceptions-only   a file that defines classes, every one an exception, and no top-level function
    port              a class that is a port (see facts)
    a-fake-name       a class whose name starts with the fakes' prefix and is more than it
    own-part-instance an import of another file of the file's own part and instance
    to-a-helper       a test file's import of test code that is no test file
    into-its-tier     an import of a file of the app that the tier of the importing file covers: a test's tier, or
                      the tier that covers an app file's part
    forwards          a method that only forwards (see facts)
    returns-a-part    a method that forwards and returns attributes of what the call answers
"""
from __future__ import annotations

import re
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
    return all(_file(name, read, profile) for name in scope.where)


def _wiring(profile: Profile) -> set[str]:
    """The parts that may import everything: the wiring, which only binds what others use."""
    return {part for part, targets in profile.rules.items() if any(t.part == EVERYTHING for t in targets)}


def _in_the_fakes(read: Read, profile: Profile) -> bool:
    return profile.fakes is not None and read.test and read.file.path[:len(profile.fakes.folder)] == profile.fakes.folder


def _file(name: str, read: Read, profile: Profile) -> bool:
    match name:
        case "tiered":
            return bool(read.tier)
        case "untiered":
            return not read.tier
        case "a-test":
            return read.is_test
        case "not-a-fake":
            return not read.is_fake
        case "not-a-package":
            return not read.package
        case "ungoverned":
            return not read.test and read.place is None
        case "not-a-package-file":
            return read.file.path[-1:] != (profile.language.package_file,)
        case "not-wiring":
            return not (read.place is not None and read.place.part in _wiring(profile))
        case "in-the-fakes":
            return _in_the_fakes(read, profile)
        case "not-in-the-fakes":
            return not _in_the_fakes(read, profile)
        case "tested-by-a-tier":
            return bool(read.tested_by)
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


def _public(found: Found, facts: Facts, profile: Profile) -> bool:
    return found.fact.name is not None and profile.language.is_public(found.fact.name)


def _trait(found: Found, name: str) -> bool:
    return name in found.fact.traits


def _top_level(found: Found, facts: Facts, profile: Profile) -> bool:
    return _trait(found, "top-level")


def _annotated(found: Found, facts: Facts, profile: Profile) -> bool:
    return _trait(found, "annotated")


def _receiver(found: Found, facts: Facts, profile: Profile) -> bool:
    return _trait(found, "receiver")


def _exception(found: Found, facts: Facts, profile: Profile) -> bool:
    return _trait(found, "exception")


def _record(found: Found, facts: Facts, profile: Profile) -> bool:
    return _trait(found, "record")


def _a_package_file(found: Found, facts: Facts, profile: Profile) -> bool:
    return found.read.file.path[-1:] == (profile.language.package_file,)


def _a_package(found: Found, facts: Facts, profile: Profile) -> bool:
    return found.read.package


def _no_code(found: Found, facts: Facts, profile: Profile) -> bool:
    return not _trait(found, "code")


def _exceptions_only(found: Found, facts: Facts, profile: Profile) -> bool:
    return _trait(found, "exceptions-only")


def _port(found: Found, facts: Facts, profile: Profile) -> bool:
    return _trait(found, "port")


def _a_fake_name(found: Found, facts: Facts, profile: Profile) -> bool:
    prefix, name = profile.fakes.prefix if profile.fakes is not None else "", found.fact.name or ""
    return name.startswith(prefix) and name != prefix


def _own_part_instance(found: Found, facts: Facts, profile: Profile) -> bool:
    return _same_part_instance(found, facts, profile) and found.fact.target != found.read.steps


def _to_a_helper(found: Found, facts: Facts, profile: Profile) -> bool:
    return found.fact.target in facts.known_tests and found.fact.target not in facts.test_files


def _forwards(found: Found, facts: Facts, profile: Profile) -> bool:
    return _trait(found, "forwards")


def _returns_a_part(found: Found, facts: Facts, profile: Profile) -> bool:
    return bool(found.fact.target)


def _into_its_tier(found: Found, facts: Facts, profile: Profile) -> bool:
    read = found.read
    tier = facts.tested_by.get(found.fact.target)
    return tier is not None and tier == (read.tier if read.test else read.tested_by)


def _read_by_a_tool(found: Found, facts: Facts, profile: Profile) -> bool:
    language, comment = profile.language, found.fact
    marker = re.escape(language.comment)
    words = "|".join(r"\s*".join(re.escape(part) for part in word.split(" ")) for word in language.directives)
    if words and re.match(rf"{marker}\s*({words})", comment.text):
        return True
    if comment.line == 1 and language.shebang and comment.text.startswith(language.shebang):
        return True
    return comment.line <= 2 and bool(language.encoding) and bool(
        re.match(rf"^[ \t\f]*{marker}.*?{language.encoding}", comment.text))


_FACT = {"absolute": _absolute, "has-a-path": _has_a_path, "unheld": _unheld, "placed": _placed,
         "below-a-package": _below_a_package, "same-part-instance": _same_part_instance, "own-package": _own_package,
         "standard-unreserved": _standard_unreserved, "reserved": _reserved, "owned": _owned,
         "reserved-and-owned": _reserved_and_owned, "bound-by-the-import-that-hit": _bound_by_the_import_that_hit,
         "own-code": _own_code, "names-a-name": _names_a_name, "built-by-a-builder": _built_by_a_builder,
         "narrowed": _narrowed, "permits-nothing": _permits_nothing, "into-the-fakes": _into_the_fakes,
         "into-a-test": _into_a_test, "a-call": _a_call, "mirroring": _mirroring, "public": _public,
         "top-level": _top_level, "annotated": _annotated, "receiver": _receiver, "exception": _exception,
         "record": _record, "read-by-a-tool": _read_by_a_tool, "a-package-file": _a_package_file,
         "a-package": _a_package, "no-code": _no_code, "exceptions-only": _exceptions_only, "port": _port,
         "a-fake-name": _a_fake_name, "own-part-instance": _own_part_instance, "to-a-helper": _to_a_helper,
         "into-its-tier": _into_its_tier, "forwards": _forwards, "returns-a-part": _returns_a_part}
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
