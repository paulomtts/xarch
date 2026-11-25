"""Which parts' `holds` a file of the app would break were it to lie there: the file read as if it lay in each part
that lists `holds`, by the rules `check` runs in that part (see expansion: one for the functions a part's kinds do not
allow, one for the classes), on the facts of the run as they are, so that what it defines, and whether a class of it
is an exception or a record, read as `check` reads them. Its own part is asked as any other: a file that breaks its
own part's `holds` says so too, and a part is named once whichever of its rules the file breaks. A test is never
asked."""
from __future__ import annotations

from dataclasses import replace

from xarch.kernel.placement import Place
from xarch.modules.rules.application.logic.engine import run
from xarch.modules.rules.application.logic.expansion import book
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.rule import Facts, Rule
from xarch.profile_values.checks import ANY


def reading(profile: Profile) -> tuple[Rule, ...]:
    """The rules whose kinds of fact each file of the app must be read with to be asked where else it could lie: the
    `holds` rules of each part, each scope widened to every part."""
    return tuple(replace(rule, scope=replace(rule.scope, part=ANY)) for rule in book(profile)["holds"])


def broken(facts: Facts, profile: Profile, paths: frozenset[str]) -> dict[str, tuple[str, ...]]:
    """For each file of the app at one of the paths (below the app, written with "/"), by its path, the parts whose
    `holds` it would break were it to lie there, in the profile's order, each once: the facts must hold the kinds
    reading(profile) reads."""
    rules = book(profile)["holds"]
    return {"/".join(read.file.path): tuple(dict.fromkeys(rule.scope.part for rule in rules if run(
        (rule,), replace(facts, files=(replace(read, place=Place(rule.scope.part)),)), profile)))
        for read in facts.files if not read.in_tests and "/".join(read.file.path) in paths}
