"""How a finding of rules as data is said: a saying's message and fix are sentences with `{variable}`s, each worked
out from the finding by its name (see the vocabulary for what each prints). A rule is refused when it names a variable
that does not exist or does not apply to what it says, so a variable here prints what it means for every finding it
is asked of.
"""
from __future__ import annotations

from collections.abc import Callable
from string import Formatter

from xarch.kernel.placement import EVERYTHING
from xarch.modules.rules.application.logic.places import label, narrowed, targets_of
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.rule import Facts, Found, Match
from xarch.modules.rules.domain.vocabulary import KINDS

OWNERS = 3
"""How many parts that may import or call what a finding is about a fix names before it says "or another part"."""
SHOWN = 3
"""How many parts that hold the other kind a fix of holds names."""


def said(text: str, found: Found, facts: Facts, profile: Profile) -> str:
    """The sentence with each variable worked out from the finding."""
    values = {name: value(name, found, facts, profile) for _, name, _, _ in Formatter().parse(text) if name}
    return text.format_map(values)


def value(name: str, found: Found, facts: Facts, profile: Profile) -> str:
    worked = _VALUES.get(name)
    if worked is None:
        raise ValueError(f"no variable of a saying is named {name!r}")
    return worked(found, facts, profile)


def _place_of(found: Found, profile: Profile) -> str:
    return label(profile, found.read.place) if found.read.place is not None else "code in no part"


def _target_part(found: Found, profile: Profile) -> str:
    return label(profile, found.fact.at) if found.fact.at is not None else ""


def _target_part_name(found: Found) -> str:
    return (found.fact.at.part if found.fact.at is not None else None) or ""


def _target(found: Found, facts: Facts) -> str:
    root = facts.tests_root if found.fact.kind == "import-into-tests" else facts.root
    return ".".join((root, *found.fact.target))


def _top(found: Found) -> str:
    return "".join(found.fact.path[:1])


def _targets(found: Found) -> str:
    return " or ".join(shown for match in found.rule.targets for shown in _shown(match))


def _shown(match: Match) -> list[str]:
    if match.places:
        return list(dict.fromkeys(f"{t.part}/" for t in match.places))
    if match.kind == "part":
        return [f"{p}/" for p in match.words]
    return [*match.words, *(".".join(n) if n[0] else f".{n[1]}" for n in match.names)]


def _disallowed_name(found: Found) -> str:
    return f"not {found.fact.name}" if found.fact.name is not None else "not the file as a whole"


def _qualified(found: Found) -> str:
    return ".".join(found.fact.path) if found.fact.kind == "function" else found.fact.name or ""


_VALUES: dict[str, Callable[[Found, Facts, Profile], str]] = {
    "key": lambda found, facts, profile: found.rule.key,
    "scope_part": lambda found, facts, profile: found.rule.scope.named_part,
    "targets": lambda found, facts, profile: _targets(found),
    "hit": lambda found, facts, profile: ".".join(found.hit or ()),
    "file": lambda found, facts, profile: found.read.file.name,
    "line": lambda found, facts, profile: str(found.fact.line),
    "where": lambda found, facts, profile: _place_of(found, profile),
    "tier": lambda found, facts, profile: found.read.tier,
    "mirrored_parts": lambda found, facts, profile: " and ".join(f"{p}/" for p in found.read.mirrors),
    "mirrored_may_import": lambda found, facts, profile: _mirrored_may_import(found, profile),
    "own_folder": lambda found, facts, profile: "/".join((facts.tests_root, *found.read.own)),
    "tests_folder": lambda found, facts, profile: "/".join((facts.tests_root, *found.read.file.path[:-1])),
    "language": lambda found, facts, profile: profile.language.title or "source",
    "importable_parts": lambda found, facts, profile: ", ".join(f"{part}/" for part in _permitted(found, profile)),
    "faked_parts": lambda found, facts, profile: ", ".join(profile.fakes.stand_in_for) if profile.fakes else "",
    "parts_holding_functions": lambda found, facts, profile: _holding(profile, "functions"),
    "parts_holding_classes": lambda found, facts, profile: _holding(profile, "classes"),
    "name": lambda found, facts, profile: found.fact.name or "",
    "qualified_name": lambda found, facts, profile: _qualified(found),
    "path": lambda found, facts, profile: ".".join(found.fact.path),
    "package": lambda found, facts, profile: _top(found),
    "reserved_reason": lambda found, facts, profile: profile.reserved.get(_top(found), ""),
    "library_owners": lambda found, facts, profile: ", ".join(f"{part}/" for part in _owners(found, profile)),
    "first_library_owner": lambda found, facts, profile: next(iter(_owners(found, profile)), ""),
    "written": lambda found, facts, profile: found.fact.text,
    "text": lambda found, facts, profile: found.fact.text,
    "target": lambda found, facts, profile: _target(found, facts),
    "target_name": lambda found, facts, profile: ".".join(
        (_target(found, facts), *([found.fact.name] if found.fact.name is not None else []))),
    "target_part": lambda found, facts, profile: _target_part(found, profile),
    "target_part_name": lambda found, facts, profile: _target_part_name(found),
    "target_package": lambda found, facts, profile: _package(found, facts),
    "built_by": lambda found, facts, profile: " or ".join(
        f"{p}/" for p in profile.built_by.get(_target_part_name(found), ())),
    "allowed_names": lambda found, facts, profile: " or ".join(
        narrowed(found.read.place, found.fact.at, profile)),
    "disallowed_name": lambda found, facts, profile: _disallowed_name(found),
    "move_fix": lambda found, facts, profile: _move(found, profile),
    "type_only_fix": lambda found, facts, profile: _caller_fix(found, profile),
    "tier_type_only_fix": lambda found, facts, profile: _tier_fix(found, profile),
    "forwarded": lambda found, facts, profile: found.fact.text,
    "returned": lambda found, facts, profile: ".".join(found.fact.target),
    "verb": lambda found, facts, profile: _VERBS.get(found.fact.kind, ""),
    "function": lambda found, facts, profile: found.fact.path[0] if found.fact.path else "",
}
"""What each variable prints of a finding, by its name."""

NAMES = tuple(_VALUES)
"""The name of every variable the engine says."""

_VERBS = {kind.name: kind.verb for kind in KINDS if kind.verb}
"""What a file does with what a fact of each kind names."""


def _package(found: Found, facts: Facts) -> str:
    sub = found.fact.at.sub if found.fact.at is not None else ()
    return ".".join((facts.root, *found.fact.target[:len(found.fact.target) - len(sub)]))


def _holding(profile: Profile, kind: str) -> str:
    """A part that holds the kind, naming the first SHOWN of those the profile has."""
    parts = [f"{name}/" for name, holds in profile.holds.items() if holds == kind][:SHOWN]
    return f"a part that holds {kind}: {', '.join(parts)}" if parts else f"a part that holds {kind}"


def _mirrored_may_import(found: Found, profile: Profile) -> str:
    """The keys of what the parts a test mirrors may import, then of what its tier's tests may also import, if set."""
    tier = next((t for t in profile.tiers if t.name == found.read.tier), None)
    parts = ", ".join(f"parts.{p}.may_import" for p in found.read.mirrors)
    return f"{parts}; tiers.{tier.name}.may_also_import" if tier is not None and tier.may_also_import else parts


def _tier_fix(found: Found, profile: Profile) -> str:
    """Use the part as a type only and drive the tier's subject, else leave what it does to a tier that may call it;
    with the tier's own words for what it may touch."""
    tier = next((t for t in profile.tiers if t.name == found.read.tier), None)
    part = found.fact.at.part if found.fact.at is not None else None
    driven = ", ".join(f"{s.part}/" for s in tier.subject) if tier is not None else ""
    fix = (f"use {part}/ here only as a type, and drive what you test through {driven}" if driven else
           f"use {part}/ here only as a type, and test what it does from a tier that may call it")
    return f"{fix} ({tier.name} tests may touch: {tier.may_touch})" if tier is not None and tier.may_touch else fix


def _caller_fix(found: Found, profile: Profile) -> str:
    """Use the part as a type only and leave the call to a part that may make it: one that may import it and does
    not list it as a type only, named from the profile."""
    src, dst = found.rule.scope.named_part, found.fact.at.part if found.fact.at is not None else None
    owners = [name for name, targets in profile.rules.items() if name not in (src, dst)
              and any(t.part == dst for t in targets) and dst not in profile.types_only.get(name, ())]
    shown = [f"{name}/" for name in owners[:OWNERS]]
    if not shown:
        return f"use {dst}/ here only as a type, and leave the call to code outside {src}/"
    listed = shown[0] if len(shown) == 1 else f"{', '.join(shown[:-1])} or {shown[-1]}"
    more = " or another part" if len(owners) > OWNERS else ""
    return f"use {dst}/ here only as a type, and leave the call to {listed}{more}, which may make it"


def _owners(found: Found, profile: Profile) -> list[str]:
    top = _top(found)
    own = found.read.place.part if found.read.place is not None else None
    return [name for name, packages in (profile.libraries or {}).items() if top in packages and name != own]


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
