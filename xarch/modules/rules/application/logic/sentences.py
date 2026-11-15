"""How a finding of rules as data is said: a saying's message and fix are sentences with `{variable}`s, each worked
out from the finding by its name, a closed list:

    key           the key of the profile the rule expands from
    line          the line of the fact
    rule_part     the part the rule names
    part          where the file sits, as a violation names a place (see places.label)
    who           the same, or "code in no part" for a file no part governs
    tier          the tier of a test file
    hit           the target a fact matched, as a dotted name
    verb          what the file does with what it names: import, use or call
    top           the first step of what an import names
    reason        why the profile reserves it
    owners        the other parts whose libraries list it, each as `<part>/`; first_owner the first of them
    name          the name an import takes
    written       the module an import names, as the source writes it
    target        the file or package an import reaches, as a dotted name from the root package
    target_name   the same, then the name it takes when that is no file
    target_part   where it sits, as a violation names a place
    package       the package of the part it sits in, as a dotted name from the root package
    class         the class a build builds; built where it is defined; builders the parts that may build it, joined
                  by "or"; built_part the part it is defined in
    patterns      the name patterns that narrow the targets reaching an import's target, joined by "or"
    taken         what an import takes that a pattern does not allow: "not <name>", or "not the file as a whole"
    move          where the code that makes an import a part may not make could go
    permitted     the parts the file's part may import, each as `<part>/`
    callee        the callee of a call, as a dotted name
    tests_target  a test's import into the tests' package, as a dotted name from the tests' root
    own           the folder a test may import test code from, from the tests' root
    faked         the parts the fakes stand in for
    subject       the parts a test mirrors, each as `<part>/`, joined by "and"
    mirrored_keys the keys of what they may import, joined by commas
    caller_fix    what to do about a part's use of a part as more than a type: use it as a type, and leave the call
                  to a part that may make it
    tier_fix      the same, for a tier's test: drive the tier's subject, with what the tier's tests may touch
"""
from __future__ import annotations

from string import Formatter

from xarch.kernel.logic.placement import EVERYTHING
from xarch.modules.rules.application.logic.filters import narrowed
from xarch.modules.rules.application.logic.places import label, targets_of
from xarch.modules.rules.domain.rule import Facts, Found
from xarch.modules.rules.domain.values import Profile

OWNERS = 3
"""How many parts that may import or call what a finding is about a fix names before it says "or another part"."""


def said(text: str, found: Found, facts: Facts, profile: Profile) -> str:
    """The sentence with each variable worked out from the finding."""
    values = {name: value(name, found, facts, profile) for _, name, _, _ in Formatter().parse(text) if name}
    return text.format_map(values)


def value(name: str, found: Found, facts: Facts, profile: Profile) -> str:
    rule, read, fact = found.rule, found.read, found.fact
    match name:
        case "key":
            return rule.key
        case "line":
            return str(fact.line)
        case "rule_part":
            return rule.part
        case "part":
            return label(profile, read.place) if read.place is not None else ""
        case "who":
            return label(profile, read.place) if read.place is not None else "code in no part"
        case "tier":
            return read.tier
        case "hit":
            return ".".join(found.hit or ())
        case "verb":
            return {"imported": "import", "use": "use", "method": "call"}[fact.kind]
        case "top":
            return "".join(fact.path[:1])
        case "reason":
            return profile.reserved.get("".join(fact.path[:1]), "")
        case "owners":
            return ", ".join(f"{part}/" for part in _owners(found, profile))
        case "first_owner":
            return next(iter(_owners(found, profile)), "")
        case "name":
            return fact.name or ""
        case "written":
            return fact.text
        case "target":
            return ".".join((facts.root, *fact.target))
        case "target_name":
            return ".".join((facts.root, *fact.target, *([fact.name] if fact.name is not None else [])))
        case "target_part":
            return label(profile, fact.at) if fact.at is not None else ""
        case "package":
            sub = fact.at.sub if fact.at is not None else ()
            return ".".join((facts.root, *fact.target[:len(fact.target) - len(sub)]))
        case "class":
            return fact.path[-1]
        case "built":
            return label(profile, fact.at) if fact.at is not None else ""
        case "built_part":
            return (fact.at.part if fact.at is not None else None) or ""
        case "builders":
            return " or ".join(f"{p}/" for p in profile.built_by.get(value("built_part", found, facts, profile), ()))
        case "patterns":
            return " or ".join(narrowed(found, profile))
        case "taken":
            return f"not {fact.name}" if fact.name is not None else "not the file as a whole"
        case "move":
            return _move(found, profile)
        case "permitted":
            return ", ".join(f"{part}/" for part in _permitted(found, profile))
        case "callee":
            return ".".join(fact.path)
        case "subject":
            return " and ".join(f"{p}/" for p in read.mirrors)
        case "mirrored_keys":
            return ", ".join(f"parts.{p}.may_import" for p in read.mirrors)
        case "tests_target":
            return ".".join((facts.tests_root, *fact.target))
        case "own":
            return "/".join((facts.tests_root, *read.own))
        case "faked":
            return ", ".join(profile.fakes.stand_in_for) if profile.fakes is not None else ""
        case "tier_fix":
            return _tier_fix(found, profile)
        case "caller_fix":
            return _caller_fix(found, profile)
    raise ValueError(f"no variable of a saying is named {name!r}")


def _tier_fix(found: Found, profile: Profile) -> str:
    """Use the part as a type only and drive the tier's subject, else leave what it does to a tier that may call it;
    with the tier's own words for what it may touch."""
    tier = next(t for t in profile.tiers if t.name == found.read.tier)
    part = found.fact.at.part if found.fact.at is not None else None
    driven = ", ".join(f"{s.part}/" for s in tier.subject)
    fix = (f"use {part}/ here only as a type, and drive what you test through {driven}" if driven else
           f"use {part}/ here only as a type, and test what it does from a tier that may call it")
    return f"{fix} ({tier.name} tests may touch: {tier.may_touch})" if tier.may_touch else fix


def _caller_fix(found: Found, profile: Profile) -> str:
    """Use the part as a type only and leave the call to a part that may make it: one that may import it and does
    not list it as a type only, named from the profile."""
    src, dst = found.rule.part, found.fact.at.part if found.fact.at is not None else None
    owners = [name for name, targets in profile.rules.items() if name not in (src, dst)
              and any(t.part == dst for t in targets) and dst not in profile.types_only.get(name, ())]
    shown = [f"{name}/" for name in owners[:OWNERS]]
    if not shown:
        return f"use {dst}/ here only as a type, and leave the call to code outside {src}/"
    listed = shown[0] if len(shown) == 1 else f"{', '.join(shown[:-1])} or {shown[-1]}"
    more = " or another part" if len(owners) > OWNERS else ""
    return f"use {dst}/ here only as a type, and leave the call to {listed}{more}, which may make it"


def _owners(found: Found, profile: Profile) -> list[str]:
    top = found.fact.path[0]
    return [name for name, packages in (profile.libraries or {}).items() if top in packages and name != found.rule.part]


def _permitted(found: Found, profile: Profile) -> list[str]:
    part = found.read.place.part if found.read.place is not None else None
    return list(dict.fromkeys(t.part for t in (targets_of(profile, part) if part is not None else ())
                              if t.part != EVERYTHING))


def _move(found: Found, profile: Profile) -> str:
    """Where the code could go: the parts, other than the file's and the target's, whose rules name the target's
    part, at most OWNERS of them; else a part that may import it."""
    src = found.read.place.part if found.read.place is not None else None
    dst = found.fact.at.part if found.fact.at is not None else None
    owners = [name for name, targets in profile.rules.items()
              if name not in (src, dst) and any(t.part == dst for t in targets)]
    shown = ", ".join(f"{name}/" for name in owners[:OWNERS])
    if 0 < len(owners) <= OWNERS:
        return f"move this code to {shown}, which may import it"
    if owners:
        return f"move this code to {shown} or another part that may import it"
    return f"move this code to a part that may import {label(profile, found.fact.at) if found.fact.at else ''}"
