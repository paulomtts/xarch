"""The checks a profile writes itself, under `checks`, read as the format writes them: a map from an id of the
profile's own to a check, each a map of slots. Here the format is read and every name the profile declares is checked
(an id, a part, a tier, a place); what the words of the vocabulary mean, and whether each applies where it is written,
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
that takes no values, or a map of one entry {<kind>: <value> | [<value>, ...]}. A check comes back as the same map,
each list a tuple, a filter as its text (`not below fakes`), a target as {kind, values}, a place a Target, and `in`
and `from` with their defaults.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from xarch.kernel.violations import OWN_ID, RULES
from xarch.modules.spec.application.logic.targets_written import target
from xarch.modules.spec.domain.values import Language, Part, Tier

SLOTS = ("read", "in", "keep", "may_not", "may_only", "must_reach", "must_be_reached", "except", "mode", "message",
         "fix", "once_per", "cases", "examples")
"""Every slot of a check, in the order a check is written."""
QUANTIFIERS = ("may_not", "may_only", "must_reach", "must_be_reached")
SCOPE = ("files", "part", "tier", "where")
REACH = {"must_reach": ("targets", "through", "through_only"),
         "must_be_reached": ("from", "through", "through_only", "then_through", "by_another_file")}
CASE = ("when", "message", "fix", "once_per")
EXAMPLES = ("flagged", "clean")
NOT = "not "
STRUCTURE = "structure"
"""How `in.part` names the structure: the folders of the layout no part claims."""


def checks(value: Any, parts: Mapping[str, Part], declared: set[str], tiers: tuple[Tier, ...], language: Language,
           problems: list[str]) -> dict[str, dict[str, Any]]:
    """Every check of the map, by its id, as it comes back (see the module); one with a problem is left out, and the
    problem said at its address."""
    if not isinstance(value, Mapping):
        problems.append("checks: must be a map from an id of your own to a check, such as "
                        "{store-names: {read: class, may_only: {name: [\"*Store\"]}, message: ..., fix: ..., examples: ...}}")
        return {}
    found: dict[str, dict[str, Any]] = {}
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
        read = _check(body, where, parts, declared, {t.name for t in tiers}, language, problems)
        if len(problems) == count:
            found[name] = read
    return found


def _check(body: Any, where: str, parts: Mapping[str, Part], declared: set[str], tiers: set[str], language: Language,
           problems: list[str]) -> dict[str, Any]:
    if not isinstance(body, Mapping):
        problems.append(f"{where}: must be a map of slots: {', '.join(SLOTS)}")
        return {}
    problems += _unknown(body, SLOTS, where)
    problems += [f"{where}: missing `{slot}`" for slot in ("read", "message", "fix", "examples") if slot not in body]
    quantified = [slot for slot in QUANTIFIERS if slot in body]
    if len(quantified) != 1:
        problems.append(f"{where}: {'names no quantifier' if not quantified else 'names ' + ' and '.join(quantified)}: "
                        f"write one of {', '.join(QUANTIFIERS)}")
    scope = _scope(body.get("in", {}), f"{where}.in", declared, tiers, problems)
    owner = parts.get(scope["part"])
    read: dict[str, Any] = {"read": _names(body.get("read"), f"{where}.read", problems), "in": scope,
                            "keep": _filters(body.get("keep", []), f"{where}.keep", problems),
                            "except": _filters(body.get("except", []), f"{where}.except", problems),
                            "mode": _text(body.get("mode", "fail"), f"{where}.mode", problems),
                            "message": _sentence(body.get("message"), f"{where}.message", problems),
                            "fix": _sentence(body.get("fix"), f"{where}.fix", problems),
                            "once_per": _names(body.get("once_per", []), f"{where}.once_per", problems, empty=True),
                            "cases": _cases(body.get("cases", []), f"{where}.cases", problems),
                            "examples": _examples(body.get("examples"), f"{where}.examples", language, problems)}
    for slot in quantified[:1]:
        read[slot] = _quantified(slot, body[slot], f"{where}.{slot}", owner, parts, declared, tiers, problems)
    return read


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


def _filters(value: Any, where: str, problems: list[str]) -> tuple[str, ...]:
    """Each filter as its text: `[not ]<name>[ <value>]`."""
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
    return tuple(found)


def _scope(value: Any, where: str, declared: set[str], tiers: set[str], problems: list[str]) -> dict[str, Any]:
    scope: dict[str, Any] = {"files": "app", "part": "*", "tier": "", "where": ()}
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a map {{files, part, tier, where}}")
        return scope
    problems += _unknown(value, SCOPE, where)
    if "files" in value:
        scope["files"] = _text(value["files"], f"{where}.files", problems)
    part = value.get("part")
    if part is not None:
        if part == STRUCTURE:
            scope["part"] = ""
        elif isinstance(part, str) and part in declared:
            scope["part"] = part
        else:
            problems.append(f"{where}.part: no part named {part!r}: write one of {', '.join(sorted(declared))}, or "
                            f"{STRUCTURE}")
    tier = value.get("tier")
    if tier is not None:
        if isinstance(tier, str) and tier in tiers:
            scope["tier"] = tier
        else:
            problems.append(f"{where}.tier: no tier named {tier!r}"
                            + (f": write one of {', '.join(sorted(tiers))}" if tiers else ": the profile has no tiers"))
    scope["where"] = _filters(value.get("where", []), f"{where}.where", problems)
    return scope


def _targets(value: Any, where: str, owner: Part | None, parts: Mapping[str, Part], declared: set[str],
             problems: list[str]) -> tuple[dict[str, Any], ...]:
    items = value if isinstance(value, list) else [value]
    found: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, str) and item.strip():
            found.append({"kind": item.strip(), "values": ()})
            continue
        if not isinstance(item, Mapping) or len(item) != 1:
            problems.append(f"{where}: {item!r} is not a target: write a kind, or {{<kind>: [<value>, ...]}}")
            continue
        ((kind, given),) = item.items()
        values = [given] if isinstance(given, str) else given
        if not isinstance(kind, str) or not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            problems.append(f"{where}: {dict(item)!r}: write the values of a target as a list of text")
            continue
        if kind == "place":
            count = len(problems)
            places = tuple(t for v in values if (t := target(v, owner, dict(parts), declared, f"{where}.place",
                                                             problems)) is not None)
            if len(problems) == count:
                found.append({"kind": kind, "values": places})
            continue
        if kind == "part":
            missing = [v for v in values if v not in declared]
            if missing:
                problems.append(f"{where}.part: no part named {', '.join(map(repr, missing))}")
                continue
        found.append({"kind": kind, "values": tuple(values)})
    return tuple(found)


def _quantified(slot: str, value: Any, where: str, owner: Part | None, parts: Mapping[str, Part], declared: set[str],
                tiers: set[str], problems: list[str]) -> Any:
    if slot not in REACH:
        return _targets(value, where, owner, parts, declared, problems)
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a map {{{', '.join(REACH[slot])}}}")
        return {}
    problems += _unknown(value, REACH[slot], where)
    required = ("targets",) if slot == "must_reach" else ("from", "through")
    problems += [f"{where}: missing `{key}`" for key in required if key not in value]
    found: dict[str, Any] = {"through": _names(value.get("through"), f"{where}.through", problems),
                             "through_only": _filters(value.get("through_only", []), f"{where}.through_only", problems)}
    if slot == "must_reach":
        found["targets"] = _targets(value.get("targets", []), f"{where}.targets", owner, parts, declared, problems)
        return found
    found["from"] = _scope(value.get("from", {}), f"{where}.from", declared, tiers, problems)
    found["then_through"] = _names(value.get("then_through"), f"{where}.then_through", problems)
    elsewhere = value.get("by_another_file", False)
    if not isinstance(elsewhere, bool):
        problems.append(f"{where}.by_another_file: must be true or false")
    found["by_another_file"] = elsewhere is True
    return found


def _cases(value: Any, where: str, problems: list[str]) -> tuple[dict[str, Any], ...]:
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of {{when, message, fix, once_per}}")
        return ()
    found: list[dict[str, Any]] = []
    for index, case in enumerate(value, 1):
        at = f"{where}[{index}]"
        if not isinstance(case, Mapping):
            problems.append(f"{at}: must be a map {{when, message, fix, once_per}}")
            continue
        problems += _unknown(case, CASE, at)
        problems += [f"{at}: missing `{key}`" for key in ("when", "message", "fix") if key not in case]
        found.append({"when": _filters(case.get("when", []), f"{at}.when", problems),
                      "message": _sentence(case.get("message"), f"{at}.message", problems),
                      "fix": _sentence(case.get("fix"), f"{at}.fix", problems),
                      "once_per": _names(case.get("once_per", []), f"{at}.once_per", problems, empty=True)})
    return tuple(found)


def _examples(value: Any, where: str, language: Language, problems: list[str]) -> dict[str, tuple[tuple[str, str], ...]]:
    """The code the check must find something in (flagged) and the code it must find nothing in (clean), each a
    small project: its files by their path below the app (tests/<path> for a test), and what each says."""
    found: dict[str, tuple[tuple[str, str], ...]] = {"flagged": (), "clean": ()}
    if value is None:
        return found
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a map {{flagged: {{<path>: <code>}}, clean: {{<path>: <code>}}}}")
        return found
    problems += _unknown(value, EXAMPLES, where)
    for side in EXAMPLES:
        files = value.get(side)
        if not isinstance(files, Mapping) or not files:
            problems.append(f"{where}.{side}: must be a map of at least one file, {{<path>: <code>}}: the code the check "
                            f"must find {'something' if side == 'flagged' else 'nothing'} in")
            continue
        listed: list[tuple[str, str]] = []
        for path, code in files.items():
            steps = path.split("/") if isinstance(path, str) else []
            if not steps or any(step in ("", ".", "..") for step in steps) or not path.endswith(language.checked.extension):
                problems.append(f"{where}.{side}: {path!r} is not a path of a source file below the app (or tests/...)"
                                f", ending in {language.checked.extension}")
            elif not isinstance(code, str):
                problems.append(f"{where}.{side}.{path}: must be the code of the file, as text")
            else:
                listed.append((path, code))
        found[side] = tuple(listed)
    return found
