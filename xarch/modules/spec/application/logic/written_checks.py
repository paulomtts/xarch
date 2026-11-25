"""The checks a profile writes itself, under `checks`, read as the format writes them: a map from an id of the
profile's own to a check, each a map of slots. Here the format is read and every name the profile declares is checked
(an id, a part, a tier); what the words of the vocabulary mean, and whether each applies where it is written,
is the rules module's, which reads what this gives back.

    <id>:                         lowercase words joined by `-`, no id of a check xarch has
      read: <kind> | [<kind>, ...]
      in: {files: app | tests | all, part: <part> | structure, tier: <tier>, where: [<filter>, ...]}
      keep: [<filter>, ...]
      may_not | may_only: <target> | [<target>, ...]
      must_reach: {targets: <target> | [<target>, ...], through: <kind> | [<kind>, ...], through_only: [<filter>, ...]}
      must_be_reached: {from: <scope as in>, through: ..., through_only: [...], then_through: <kind> | [...], by_another_file: true}
      except: [<filter>, ...]
      mode: fail | list
      message: <sentence>         with {<variable>}s
      fix: <sentence>
      once_per: [<variable>, ...]
      cases: [{when: [<filter>, ...], message, fix, once_per}, ...]
      examples: {flagged: {<path>: <code>, ...}, clean: {<path>: <code>, ...}}

A filter is a name, `not <name>`, or a map of one entry {<name>: <value>} ({not <name>: <value>}); a target is a kind
that takes no values, or a map of one entry {<kind>: <value> | [<value>, ...]}. A check comes back as a WrittenCheck
of profile_values: each list a tuple, a filter a Condition, a target its kind and its values as written, and `in` and
`from` with their defaults.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from xarch.kernel.logic.conditions import condition
from xarch.kernel.logic.placement import stem
from xarch.kernel.violations import OWN_ID, RULES
from xarch.modules.spec.domain.values import (
    CASE_SLOTS,
    EXAMPLE_SLOTS,
    REACH_SLOTS,
    SCOPE_SLOTS,
    SLOTS,
    STRUCTURE_WORD,
    Language,
    Tier,
)
from xarch.profile_values.checks import (
    ANY,
    APP,
    QUANTIFIER_SLOTS,
    STRUCTURE,
    Condition,
    Quantified,
    Saying,
    Scope,
    WrittenCheck,
    WrittenTarget,
)


def checks(value: Any, declared: set[str], tiers: tuple[Tier, ...], language: Language,
           problems: list[str]) -> dict[str, WrittenCheck]:
    """Every check of the map, by its id, as it comes back (see the module); one with a problem is left out, and the
    problem said at its address."""
    if not isinstance(value, Mapping):
        problems.append("checks: must be a map from an id of your own to a check, such as "
                        "{store-names: {read: class, may_only: {name: [\"*Store\"]}, message: ..., fix: ..., examples: ...}}")
        return {}
    found: dict[str, WrittenCheck] = {}
    for name, body in value.items():
        where = f"checks.{name}"
        count = len(problems)
        if not isinstance(name, str) or not OWN_ID.fullmatch(name):
            problems.append(f"checks: {name!r} is not an id: write lowercase words joined by `-`, such as store-names")
            continue
        if name in RULES:
            problems.append(f"{where}: {name} is the id of a check xarch has: give your check an id of its own, such as "
                            f"my-{name}")
            continue
        read = _check(body, where, declared, {t.name for t in tiers}, language, problems)
        if len(problems) == count and read is not None:
            found[name] = read
    return found


def _check(body: Any, where: str, declared: set[str], tiers: set[str], language: Language,
           problems: list[str]) -> WrittenCheck | None:
    if not isinstance(body, Mapping):
        problems.append(f"{where}: must be a map of slots: {', '.join(SLOTS)}")
        return None
    problems += _unknown(body, SLOTS, where)
    problems += [f"{where}: missing `{slot}`" for slot in ("read", "message", "fix", "examples") if slot not in body]
    quantified = [slot for slot in QUANTIFIER_SLOTS if slot in body]
    if len(quantified) != 1:
        problems.append(f"{where}: {'names no quantifier' if not quantified else 'names ' + ' and '.join(quantified)}: "
                        f"write one of {', '.join(QUANTIFIER_SLOTS)}")
    within = scope(body.get("in", {}), f"{where}.in", declared, tiers, problems)
    read = _names(body.get("read"), f"{where}.read", problems)
    keep = filters(body.get("keep", []), f"{where}.keep", problems)
    exempt = filters(body.get("except", []), f"{where}.except", problems)
    mode = _text(body.get("mode", "fail"), f"{where}.mode", problems)
    own = Saying(_sentence(body.get("message"), f"{where}.message", problems),
                 _sentence(body.get("fix"), f"{where}.fix", problems), (),
                 _names(body.get("once_per", []), f"{where}.once_per", problems, empty=True))
    cases = _cases(body.get("cases", []), f"{where}.cases", problems)
    flagged, clean = _examples(body.get("examples"), f"{where}.examples", language, problems)
    if len(quantified) != 1:
        return None
    slot = quantified[0]
    return WrittenCheck(read, within, _quantified(slot, body[slot], f"{where}.{slot}", declared, tiers, problems),
                        (*cases, own), keep, exempt, mode, flagged, clean)


def _unknown(body: Mapping[Any, Any], known: tuple[str, ...], where: str) -> list[str]:
    unknown = [str(key) for key in body if key not in known]
    return [f"{where}: unknown key{'s' if len(unknown) > 1 else ''} {', '.join(f'`{k}`' for k in unknown)}: use "
            f"{', '.join(known)}"] if unknown else []


def _text(value: Any, where: str, problems: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        problems.append(f"{where}: must be a word")
        return ""
    return value


def _sentence(value: Any, where: str, problems: list[str]) -> str:
    if value is None:
        return ""
    if not isinstance(value, str) or not value.strip():
        problems.append(f"{where}: must be a sentence, with {{<variable>}}s for what it names")
        return ""
    return value


def _names(value: Any, where: str, problems: list[str], empty: bool = False) -> tuple[str, ...]:
    """A name, or a list of names, as a tuple."""
    if value is None:
        return ()
    items = [value] if isinstance(value, str) else value
    if not isinstance(items, list) or not all(isinstance(item, str) and item.strip() for item in items) or (
            not items and not empty):
        problems.append(f"{where}: must be a name or a list of names")
        return ()
    return tuple(items)


def filters(value: Any, where: str, problems: list[str]) -> tuple[Condition, ...]:
    """Each filter, written `[not ]<name>[ <value>]` or {<[not ]name>: <value>}."""
    items = value if isinstance(value, list) else [value]
    found: list[str] = []
    for item in items:
        if isinstance(item, str) and item.strip() and len(item.split()) <= 2:
            found.append(item.strip())
        elif isinstance(item, Mapping) and len(item) == 1:
            ((name, given),) = item.items()
            if isinstance(name, str) and isinstance(given, str) and given.strip() and " " not in given.strip():
                found.append(f"{name.strip()} {given.strip()}")
            else:
                problems.append(f"{where}: {dict(item)!r}: write a filter that takes a value as {{<name>: <value>}}")
        else:
            problems.append(f"{where}: {item!r} is not a filter: write a name, `not <name>`, or {{<name>: <value>}}")
    return tuple(condition(text) for text in found)


def scope(value: Any, where: str, declared: set[str], tiers: set[str], problems: list[str]) -> Scope:
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a map {{files, part, tier, where}}")
        return Scope()
    problems += _unknown(value, SCOPE_SLOTS, where)
    files = _text(value["files"], f"{where}.files", problems) if "files" in value else APP
    part = value.get("part")
    chosen = ANY
    if part is not None:
        if part == STRUCTURE_WORD:
            chosen = STRUCTURE
        elif isinstance(part, str) and part in declared:
            chosen = part
        else:
            problems.append(f"{where}.part: no part named {part!r}: write one of {', '.join(sorted(declared))}, or "
                            f"{STRUCTURE_WORD}")
    tier = value.get("tier")
    named = ""
    if tier is not None:
        if isinstance(tier, str) and tier in tiers:
            named = tier
        else:
            problems.append(f"{where}.tier: no tier named {tier!r}"
                            + (f": write one of {', '.join(sorted(tiers))}" if tiers else ": the profile has no tiers"))
    return Scope(files, chosen, named, filters(value.get("where", []), f"{where}.where", problems))


def _targets(value: Any, where: str, problems: list[str]) -> tuple[WrittenTarget, ...]:
    items = value if isinstance(value, list) else [value]
    found: list[WrittenTarget] = []
    for item in items:
        if isinstance(item, str) and item.strip():
            found.append(WrittenTarget(item.strip()))
            continue
        if not isinstance(item, Mapping) or len(item) != 1:
            problems.append(f"{where}: {item!r} is not a target: write a kind, or {{<kind>: [<value>, ...]}}")
            continue
        ((kind, given),) = item.items()
        values = [given] if isinstance(given, str) else given
        if not isinstance(kind, str) or not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            problems.append(f"{where}: {dict(item)!r}: write the values of a target as a list of text")
            continue
        found.append(WrittenTarget(kind, tuple(values)))
    return tuple(found)


def _quantified(slot: str, value: Any, where: str, declared: set[str], tiers: set[str],
                problems: list[str]) -> Quantified:
    if slot not in REACH_SLOTS:
        return Quantified(slot, _targets(value, where, problems))
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a map {{{', '.join(REACH_SLOTS[slot])}}}")
        return Quantified(slot)
    problems += _unknown(value, REACH_SLOTS[slot], where)
    required = ("targets",) if slot == "must_reach" else ("from", "through")
    problems += [f"{where}: missing `{key}`" for key in required if key not in value]
    through = _names(value.get("through"), f"{where}.through", problems)
    only = filters(value.get("through_only", []), f"{where}.through_only", problems)
    if slot == "must_reach":
        return Quantified(slot, _targets(value.get("targets", []), f"{where}.targets", problems), through, only)
    elsewhere = value.get("by_another_file", False)
    if not isinstance(elsewhere, bool):
        problems.append(f"{where}.by_another_file: must be true or false")
    return Quantified(slot, (), through, only, scope(value.get("from", {}), f"{where}.from", declared, tiers, problems),
                      _names(value.get("then_through"), f"{where}.then_through", problems), elsewhere is True)


def _cases(value: Any, where: str, problems: list[str]) -> tuple[Saying, ...]:
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of {{when, message, fix, once_per}}")
        return ()
    found: list[Saying] = []
    for index, case in enumerate(value, 1):
        at = f"{where}[{index}]"
        if not isinstance(case, Mapping):
            problems.append(f"{at}: must be a map {{when, message, fix, once_per}}")
            continue
        problems += _unknown(case, CASE_SLOTS, at)
        problems += [f"{at}: missing `{key}`" for key in ("when", "message", "fix") if key not in case]
        found.append(Saying(_sentence(case.get("message"), f"{at}.message", problems),
                            _sentence(case.get("fix"), f"{at}.fix", problems),
                            filters(case.get("when", []), f"{at}.when", problems),
                            _names(case.get("once_per", []), f"{at}.once_per", problems, empty=True)))
    return tuple(found)


def _examples(value: Any, where: str, language: Language,
              problems: list[str]) -> tuple[tuple[tuple[str, str], ...], tuple[tuple[str, str], ...]]:
    """The code the check must find something in (flagged) and the code it must find nothing in (clean), each a
    small project: its files by their path below the app (tests/<path> for a test), and what each says."""
    found: dict[str, tuple[tuple[str, str], ...]] = {"flagged": (), "clean": ()}
    if value is None:
        return (), ()
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a map {{flagged: {{<path>: <code>}}, clean: {{<path>: <code>}}}}")
        return (), ()
    problems += _unknown(value, EXAMPLE_SLOTS, where)
    for side in EXAMPLE_SLOTS:
        files = value.get(side)
        if not isinstance(files, Mapping) or not files:
            problems.append(f"{where}.{side}: must be a map of at least one file, {{<path>: <code>}}: the code the check "
                            f"must find {'something' if side == 'flagged' else 'nothing'} in")
            continue
        listed: list[tuple[str, str]] = []
        for path, code in files.items():
            steps = path.split("/") if isinstance(path, str) else []
            if not steps or any(step in ("", ".", "..") for step in steps) or stem(steps[-1], language.checked.marks) is None:
                problems.append(f"{where}.{side}: {path!r} is not a path of a source file below the app (or tests/...)"
                                f", ending in {language.checked.extension}")
            elif not isinstance(code, str):
                problems.append(f"{where}.{side}.{path}: must be the code of the file, as text")
            else:
                listed.append((path, code))
        found[side] = tuple(listed)
    return found["flagged"], found["clean"]
