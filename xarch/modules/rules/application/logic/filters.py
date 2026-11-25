"""The filters of rules as data, each a question about the file a fact is in, about the fact, or about what it reaches
(see the vocabulary for what each means), and whether a scope holds a file. A rule names them in its scope (where:
about the file), in what it keeps, in what it exempts, in the condition of a saying and in what a link passes; a
condition negated passes when its filter does not hold.
"""
from __future__ import annotations

import re
from collections.abc import Callable

from xarch.kernel.logic.placement import name_matches
from xarch.kernel.placement import EVERYTHING
from xarch.modules.rules.application.logic.places import accepting, narrowed
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.rule import Facts, Found, Read
from xarch.profile_values.checks import ALL, ANY, APP, STRUCTURE, TESTS, Condition, Scope

Question = Callable[[Found, Facts, Profile], bool]
"""What a condition asks of a fact a rule found."""
Asked = Callable[[Found, Facts, Profile, str], bool]
"""What a filter asks of a fact a rule found, given its value ("" for a filter that takes none)."""


def in_scope(scope: Scope, read: Read, facts: Facts, profile: Profile) -> bool:
    if scope.files != {False: APP, True: TESTS}[read.in_tests] and scope.files != ALL:
        return False
    if scope.part == STRUCTURE and (read.in_tests or read.place is None or read.place.part is not None):
        return False
    if scope.part not in (ANY, STRUCTURE) and not (scope.part in read.mirrors if read.in_tests else
                                                   read.place is not None and read.place.part == scope.part):
        return False
    if scope.tier and read.tier != scope.tier:
        return False
    return all(_FILE[condition.name](read, profile, condition.value) != condition.negated for condition in scope.where)


def question(condition: Condition) -> Question:
    """The question a condition asks, by its filter's name."""
    about_file = _FILE.get(condition.name)
    if about_file is not None:
        return lambda found, facts, profile: about_file(found.read, profile, condition.value) != condition.negated
    asked = _FACT.get(condition.name)
    if asked is None:
        raise ValueError(f"no filter is named {condition.name!r}")
    return lambda found, facts, profile: asked(found, facts, profile, condition.value) != condition.negated


def _folder(value: str) -> tuple[str, ...]:
    return tuple(step for step in value.split("/") if step)


def _test(read: Read, profile: Profile, value: str) -> bool:
    return read.is_test


def _tiered(read: Read, profile: Profile, value: str) -> bool:
    return bool(read.tier)


def _placed_file(read: Read, profile: Profile, value: str) -> bool:
    return read.place is not None


def _package_file(read: Read, profile: Profile, value: str) -> bool:
    return read.package


def _mirrors_a_part(read: Read, profile: Profile, value: str) -> bool:
    return bool(read.mirrors)


def _may_import_everything(read: Read, profile: Profile, value: str) -> bool:
    part = read.place.part if read.place is not None else None
    return part is not None and any(t.part == EVERYTHING for t in profile.rules.get(part, ()))


def _below(read: Read, profile: Profile, value: str) -> bool:
    folder = _folder(value)
    return not read.file.beside and read.file.path[:len(folder)] == folder


def _beside(read: Read, profile: Profile, value: str) -> bool:
    return read.file.beside


_FILE: dict[str, Callable[[Read, Profile, str], bool]] = {
    "test": _test, "tiered": _tiered, "placed": _placed_file, "package-file": _package_file,
    "mirrors-a-part": _mirrors_a_part, "may-import-everything": _may_import_everything, "below": _below,
    "beside": _beside}
"""Each filter about the file by its name, the question it asks of the file."""


def _top(found: Found) -> str:
    return "".join(found.fact.path[:1])


def _relative(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return "relative" in found.fact.traits


def _standard(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return "standard" in found.fact.traits


def _reserved(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return _top(found) in profile.reserved


def _listed_by_another_part(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    top, own = _top(found), found.read.place.part if found.read.place is not None else None
    return any(top in packages and part != own for part, packages in (profile.imports_libraries or {}).items())


def _app_package(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return found.fact.path[:1] == (facts.root,)


def _own_code(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return "relative" in found.fact.traits or found.fact.path[:1] in ((facts.root,), (facts.tests_root,))


def _takes_a_name(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return found.fact.name is not None


def _on_own_object(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return "on-own-object" in found.fact.traits


def _special(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return found.fact.name is not None and profile.language.is_special(found.fact.name)


def _named(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return found.fact.name is not None and name_matches(value, found.fact.name)


def _fake_named(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    fakes, name = profile.fakes, found.fact.name
    return fakes is not None and name is not None and any(
        name.startswith(prefix) and name != prefix for prefix in fakes.prefixes or (fakes.prefix,))


def _extends(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return any(base and name_matches(value, base[-1]) for base in found.fact.bases)


def _trait(name: str) -> Asked:
    return lambda found, facts, profile, value: name in found.fact.traits


def _returns_an_attribute(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return "forwards" in found.fact.traits and bool(found.fact.target)


def _directive(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    language, comment = profile.language, found.fact
    marker = comment.name or ""
    after = comment.text[len(marker):] if marker and comment.text.startswith(marker) else None
    words = "|".join(r"\s*".join(re.escape(part) for part in word.split(" ")) for word in language.directives)
    if after is not None and words and re.match(rf"\s*({words})", after):
        return True
    if comment.line == 1 and language.shebang and comment.text.startswith(language.shebang):
        return True
    return after is not None and comment.line <= 2 and bool(language.encoding) and bool(
        re.match(rf".*?{language.encoding}", after))


def _reported_at_import(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return bool(found.hit) and found.fact.bound >= len(found.hit)


def _names_restricted(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return bool(narrowed(found.read.place, found.fact.at, profile))


def _target_accepted(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    part = found.read.place.part if found.read.place is not None else None
    return accepting(profile, part, found.read.file.path, found.fact.target, found.fact.name) is not None


def _of_kind(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return found.fact.kind == value


def _target_placed(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return found.fact.at is not None


def _target_inside_part(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return found.fact.at is not None and bool(found.fact.at.sub)


def _target_in_own_part(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    src, at = found.read.place, found.fact.at
    return src is not None and at is not None and src.part == at.part and src.instance == at.instance


def _target_in_own_tier(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    tier = facts.tested_by.get(found.fact.target)
    return tier is not None and tier == found.read.tier


def _target_test(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    return found.fact.target in facts.test_files


def _target_below(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    folder = _folder(value)
    return bool(found.fact.target) and found.fact.target[:len(folder)] == folder


def _target_allows_under(found: Found, facts: Facts, profile: Profile, value: str) -> bool:
    src, at = found.read.place, found.fact.at
    listed = {"built_by": profile.holds_built_by}.get(value, {})
    return src is not None and at is not None and src.part in listed.get(at.part or "", ())


_FACT: dict[str, Asked] = {
    "relative": _relative, "standard": _standard, "reserved": _reserved,
    "listed-by-another-part": _listed_by_another_part, "app-package": _app_package, "own-code": _own_code,
    "takes-a-name": _takes_a_name, "on-own-object": _on_own_object, "special": _special, "named": _named,
    "fake-named": _fake_named, "extends": _extends,
    **{name: _trait(name) for name in ("top-level", "forwards", "exception", "record", "interface", "immutable",
                                       "receiver", "annotated-callable", "no-statements", "exceptions-only",
                                       "unreadable", "doc", "public", "type-only")},
    "returns-an-attribute": _returns_an_attribute, "directive": _directive, "reported-at-import": _reported_at_import,
    "names-restricted": _names_restricted, "of-kind": _of_kind, "target-placed": _target_placed,
    "target-inside-part": _target_inside_part, "target-in-own-part": _target_in_own_part,
    "target-in-own-tier": _target_in_own_tier, "target-test": _target_test, "target-below": _target_below,
    "target-allows-under": _target_allows_under, "target-accepted": _target_accepted}
"""Each filter about the fact or what it reaches by its name, the question it asks."""

NAMES = (*_FILE, *_FACT)
"""The name of every filter the engine answers."""
