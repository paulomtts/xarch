"""A profile in format 1 converted to format 2, as a document, with the files that go with it.

Each fact moves to where format 2 states it: the layout, `rules`, `libraries`, `forbidden`, `placement`, the tiers'
`subject` and the guard `package-only` become facts of the parts; `tests` and the framework names the guards held become
`testing`; `naming`, `entry`, the docs and the examples go under `docs`. What changes meaning is listed in `changes`; what
has no form in format 2 is listed in `by_hand`, each with what to write; nothing is dropped without being listed.
"""
from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from xarch.kernel.logic.placement import EVERYTHING, Target, with_itself
from xarch.modules.spec.application.logic.migrate_examples import Gathered, gather, rewrite_examples
from xarch.modules.spec.application.logic.profile_v1 import EACH, read_v1
from xarch.modules.spec.domain.migration import Copy, OldPart, OldProfile, Tree

__all__ = ["Converted", "Copy", "convert", "rewrite_examples"]

_TARGET = re.compile(r"(?P<part>[^@/]*)(?:@(?P<scope>[^/]*))?(?:/(?P<sub>.*))?")
_TIER_DOCS = ("subject_text", "may_touch", "one_file_per", "cases_from", "data")
_DOCS_NAME = {"subject_text": "subject"}


@dataclass(frozen=True)
class Converted:
    """document: the profile in format 2; copies: the files of the converted folder other than the profile; names: each
    example's old name with its path; changes: what now means something else; by_hand: what has no form in format 2."""
    document: dict[str, Any]
    copies: tuple[Copy, ...]
    names: dict[str, str]
    changes: tuple[str, ...]
    by_hand: tuple[str, ...]


def convert(document: Any, source: str, presets: Mapping[str, Any], files: Collection[str]) -> Converted:
    """The conversion of a profile in format 1; raises InvalidArchitecture when the document cannot be read as one.
    files are the files next to it that it names, and every file below the folders it names (see referenced_v1)."""
    old = read_v1(document, source)
    changes: list[str] = []
    by_hand = [f"`{key}`: not a key of format 1, so nothing of it is converted: write it by hand if it still matters"
               for key in old.extra]
    order = _order(old)
    tiers = [tier for tier in old.get("tiers", []) if isinstance(tier, dict)] if isinstance(old.get("tiers"), list) else []
    rows = _rows(old)
    if old.get("libraries") is None:
        changes.append("libraries: the profile had no `libraries`, so no outside package was checked: every part is "
                       "written `libraries: everything`, which leaves them unchecked; list the packages of each part to "
                       "check them")
    assigned = _assigned(tiers, old, changes, by_hand)
    folders = _folders(old, by_hand)
    lists, forbidden_of = _forbidden(old)
    gathered = gather(old.raw, tiers, files, changes, by_hand)
    package_only = _package_only(old)
    parts = {name: _part(old, name, rows, assigned, folders, forbidden_of, package_only, changes, by_hand)
             for name in order}
    out: dict[str, Any] = {"xarch": 2, "name": old.name, "language": "python"}
    testing = _testing(old, presets)
    if testing is not None:
        out["testing"] = testing
    out["parts"] = parts
    if lists:
        out["forbidden"] = lists
    if old.get("layers"):
        out["layers"] = deepcopy(old.get("layers"))
    if tiers:
        out["tiers"] = {str(tier["name"]): _tier(tier, old, rows, gathered, changes) for tier in tiers}
    if isinstance(old.get("fakes"), dict):
        out["fakes"] = _fakes(old.get("fakes"))
    guards = _guards(old)
    if guards:
        out["guards"] = guards
    for key in ("excluded", "hints"):
        if old.get(key):
            out[key] = deepcopy(old.get(key))
    if gathered.files:
        out["files"] = gathered.files
    docs = _docs(old, gathered)
    if docs:
        out["docs"] = docs
    return Converted(out, tuple(gathered.copies), dict(gathered.names), tuple(changes), tuple(by_hand))


def _order(old: OldProfile) -> list[str]:
    placement = old.get("placement")
    first = [name for name in placement if name in old.parts] if isinstance(placement, list) else []
    return first + [name for name in old.parts if name not in first]


def _shown(old: OldProfile, steps: tuple[str, ...]) -> str:
    return "/".join(f"<{old.singular}>" if step == EACH else step for step in steps)


def _inside(old: OldProfile, name: str) -> bool:
    return EACH in old.parts[name].path


def _split(item: str) -> tuple[str, str, str]:
    match = _TARGET.fullmatch(item)
    return (match["part"], match["scope"] or "", match["sub"] or "") if match else (item, "", "")


def _rows(old: OldProfile) -> dict[str, list[Target]]:
    rules = old.get("rules")
    rows: dict[str, list[Target]] = {}
    for name, row in (rules.items() if isinstance(rules, dict) else ()):
        found: list[Target] = []
        for item in row if isinstance(row, list) else ():
            if item == EVERYTHING:
                found.append(Target(EVERYTHING))
                continue
            part, scope, sub = _split(str(item))
            found.append(Target(part, scope or "none", tuple(sub.split("/")) if sub else ()))
        rows[str(name)] = found
    return rows


def _target_text(old: OldProfile, target: Target, owner: str | None, label: str, changes: list[str]) -> str:
    text = target.part
    inside = owner is not None and _inside(old, owner)
    scope = target.scope
    if scope == "own" and not inside:
        scope = "any"
        changes.append(f"{label}: '{target.part}@own' is written '{target.part}@any': the importer is not in the "
                       "repeating folder, so there is no own instance")
    if _inside(old, target.part) and scope != "own" or (_inside(old, target.part) and not inside):
        text += "@any"
    elif scope == "any":
        text += "@any"
    if target.sub:
        text += "/" + "/".join(target.sub)
    return text


def _may_import(old: OldProfile, name: str, rows: dict[str, list[Target]], changes: list[str]) -> Any:
    targets = rows.get(name, [])
    label = f"parts.{name}.may_import"
    if any(target.part == EVERYTHING for target in targets):
        if len(targets) > 1:
            changes.append(f"{label}: the other targets are left out: everything holds them")
        return "everything"
    found = [_target_text(old, target, name, label, changes) for target in targets
             if not (target.part == name and target.scope != "any")]
    return found


def _forbidden(old: OldProfile) -> tuple[dict[str, list[str]], dict[str, str]]:
    value = old.get("forbidden")
    if not isinstance(value, dict):
        return {}, {}
    groups: dict[tuple[str, ...], list[str]] = {}
    for part, names in value.items():
        groups.setdefault(tuple(names), []).append(str(part))
    lists: dict[str, list[str]] = {}
    named: dict[str, str] = {}
    shared = 0
    for names, parts in groups.items():
        if len(parts) > 1:
            shared += 1
            label = "shared-names" if shared == 1 else f"shared-names-{shared}"
        else:
            label = parts[0]
        lists[label] = list(names)
        named.update({part: label for part in parts})
    return lists, named


def _package_only(old: OldProfile) -> set[str]:
    guards = old.get("guards")
    value = guards.get("package-only") if isinstance(guards, dict) else None
    return {str(part) for part in value} if isinstance(value, list) else set()


def _assigned(tiers: list[dict[str, Any]], old: OldProfile, changes: list[str], by_hand: list[str]) -> dict[str, str]:
    entries: dict[str, list[tuple[int, str]]] = {}
    for i, tier in enumerate(tiers):
        for item in tier.get("subject", []) if isinstance(tier.get("subject"), list) else []:
            part, _, sub = str(item).partition("/")
            entries.setdefault(part, []).append((i, sub))
    assigned: dict[str, str] = {}
    for part, found in entries.items():
        if part not in old.parts:
            continue
        whole = [i for i, sub in found if not sub]
        chosen = whole[0] if whole else found[0][0]
        name = str(tiers[chosen]["name"])
        assigned[part] = name
        if not whole:
            changes.append(f"parts.{part}.tier: tested only below '{part}/{found[0][1]}' by tier '{name}': format 2 gives "
                           f"the whole part to tier '{name}'")
        for i, sub in found:
            if sub and i < chosen:
                by_hand.append(f"tiers.{tiers[i]['name']}.subject: '{part}/{sub}' is tested by tier "
                               f"'{tiers[i]['name']}' and the rest of '{part}' by tier '{name}': format 2 gives a part one "
                               f"tier; make '{part}/{sub}' a part of its own to keep it")
        later = [str(tiers[i]["name"]) for i in sorted({i for i, sub in found if not sub and i > chosen})
                 if not tiers[i].get("folder")]
        if later:
            changes.append(f"parts.{part}.tier: '{part}' is in the subject of tiers '{name}' and "
                           f"{', '.join(repr(t) for t in later)}: tier '{name}' is kept, the first, as in format 1")
    return assigned


def _part(old: OldProfile, name: str, rows: dict[str, list[Target]], assigned: dict[str, str],
          folders: dict[str, Any], forbidden_of: dict[str, str], package_only: set[str], changes: list[str],
          by_hand: list[str]) -> dict[str, Any]:
    part: OldPart = old.parts[name]
    out: dict[str, Any] = {"path": _shown(old, part.path), "role": part.role}
    if part.litmus:
        out["litmus"] = part.litmus
    may_import = _may_import(old, name, rows, changes)
    if may_import:
        out["may_import"] = may_import
    libraries = old.get("libraries")
    if libraries is None:
        out["libraries"] = "everything"
    elif isinstance(libraries, dict) and libraries.get(name):
        out["libraries"] = list(libraries[name])
    if name in forbidden_of:
        out["forbidden"] = forbidden_of[name]
    if name in assigned:
        out["tier"] = assigned[name]
    if part.untested:
        out["untested"] = part.untested
    if name in package_only:
        out["package_only"] = True
    if name in folders:
        out["folders"] = folders[name]
    _file_or_folder(old, part, by_hand)
    return out


def _file_or_folder(old: OldProfile, part: OldPart, by_hand: list[str]) -> None:
    here: Tree | None = old.layout
    for step in part.path:
        here = here.get(step) if isinstance(here, dict) and step in here else {}
    last = part.path[-1]
    if here is None and "." not in last:
        by_hand.append(f"parts.{part.name}.path: '{'/'.join(part.path)}' is a file in the layout, but format 2 reads a "
                       "path as a file only when its last step holds a dot: rename it or the part")
    elif here is not None and "." in last and last != EACH:
        by_hand.append(f"parts.{part.name}.path: '{'/'.join(part.path)}' is a folder in the layout, but its last step "
                       "holds a dot, which format 2 reads as a file: rename the folder or the part")


def _folders(old: OldProfile, by_hand: list[str]) -> dict[str, Any]:
    owners = {part.path: part.name for part in old.parts.values()}
    found: dict[str, list[tuple[str, bool, str]]] = {}
    orphans: list[tuple[str, ...]] = []

    def walk(tree: Tree, prefix: tuple[str, ...]) -> None:
        for step, sub in tree.items():
            path = (*prefix, step)
            note = old.notes.get(path, "")
            if path in owners:
                pass
            elif (above := [p for p in owners if path[:len(p)] == p and len(path) > len(p)]):
                owner = owners[max(above, key=len)]
                if sub is None:
                    by_hand.append(f"layout '{'/'.join(path)}': a file below part '{owner}': format 2 lists only folders "
                                   "below a part; make it a part of its own")
                elif note or not sub:
                    rel = "/".join(path[len(old.parts[owner].path):])
                    found.setdefault(owner, []).append((rel, not sub, note))
            elif any(p[:len(path)] == path for p in owners):
                if note:
                    by_hand.append(f"notes '{'/'.join(path)}': a folder that holds parts has no note in format 2: "
                                   f"write \"{note}\" in the docs where it is needed")
            elif not any(path[:len(o)] == o for o in orphans):
                orphans.append(path)
                said = f", whose note is \"{note}\"" if note else ""
                by_hand.append(f"layout '{'/'.join(path)}'{said}: in no part and below none, and format 2 lays out only "
                               "the parts and the folders below them: make it a part, or list it under `folders` of the "
                               "part above it")
            if sub:
                walk(sub, path)

    walk(old.layout, ())
    result: dict[str, Any] = {}
    for owner, entries in found.items():
        noted = {rel: note for rel, _, note in entries if note}
        if noted and len(noted) == len(entries):
            result[owner] = noted
        else:
            result[owner] = [rel for rel, _, _ in entries]
            by_hand.extend(f"notes '{rel}': format 2 holds the notes of `folders` for all of them or for none, so "
                           f"\"{note}\" of part '{owner}' is not converted" for rel, note in noted.items())
    return result


def _tier(tier: dict[str, Any], old: OldProfile, rows: dict[str, list[Target]], gathered: Gathered,
          changes: list[str]) -> dict[str, Any]:
    name = str(tier["name"])
    out: dict[str, Any] = {}
    for key in ("proves", "litmus"):
        if key in tier:
            out[key] = str(tier[key]).strip("\n") if key == "litmus" else tier[key]
    if tier.get("forbidden") is True:
        out["apply_forbidden"] = True
    if tier.get("types_only"):
        out["types_only"] = list(tier["types_only"])
    if tier.get("folder"):
        out["folder"] = tier["folder"]
        out["may_import"] = _allowance(tier, old, rows, f"tiers.{name}.may_import", changes)
    docs: dict[str, Any] = {_DOCS_NAME.get(key, key): tier[key] for key in _TIER_DOCS if key in tier}
    example, helpers = gathered.tiers.get(name, (None, []))
    if example:
        docs["example"] = example
    if helpers:
        docs["helpers"] = helpers
    if docs:
        out["docs"] = docs
    return out


def _allowance(tier: dict[str, Any], old: OldProfile, rows: dict[str, list[Target]], label: str,
               changes: list[str]) -> Any:
    found: list[Target] = []
    for item in tier.get("subject", []) if isinstance(tier.get("subject"), list) else []:
        part, _, sub = str(item).partition("/")
        if part not in old.parts:
            continue
        own = Target(part, "own" if _inside(old, part) else "none", tuple(sub.split("/")) if sub else ())
        for target in (own, *with_itself(part, old.parts[part].path, rows.get(part, []))):
            if target not in found:
                found.append(target)
    if any(target.part == EVERYTHING for target in found):
        return "everything"
    texts: list[str] = []
    for target in found:
        text = target.part + ("@any" if _inside(old, target.part) else "") + (
            "/" + "/".join(target.sub) if target.sub else "")
        if target.scope == "own":
            changes.append(f"{label}: '{target.part}@own' is written '{target.part}@any': the tests in the folder are "
                           "in no instance of the repeating folder")
        if text not in texts:
            texts.append(text)
    return texts


def _testing(old: OldProfile, presets: Mapping[str, Any]) -> Any:
    tests = old.get("tests")
    if not isinstance(tests, dict):
        return None
    testing = deepcopy(tests)
    guards = old.get("guards") if isinstance(old.get("guards"), dict) else {}
    scenario = guards.get("scenario-coverage")
    if isinstance(scenario, dict) and "table" in scenario:
        testing["table"] = deepcopy(scenario["table"])
    stand_ins = guards.get("stand-ins")
    if isinstance(stand_ins, dict) and stand_ins:
        mocks: dict[str, Any] = {}
        for old_key, new_key in (("mocks", "calls"), ("autospec", "autospec"), ("spec", "spec_keywords")):
            if old_key in stand_ins:
                mocks[new_key] = list(stand_ins[old_key])
        if "fixtures" in stand_ins:
            mocks["fixtures"] = {param: _fixture(spec) for param, spec in stand_ins["fixtures"].items()}
        testing["mocks"] = mocks
    return next((name for name, preset in presets.items() if preset == testing), testing)


def _fixture(spec: dict[str, Any]) -> dict[str, Any]:
    out = {"calls": list(spec.get("mocks", []))}
    if "autospec" in spec:
        out["autospec"] = list(spec["autospec"])
    return out


def _guards(old: OldProfile) -> dict[str, Any]:
    guards = old.get("guards")
    out: dict[str, Any] = {}
    for name, spec in (guards.items() if isinstance(guards, dict) else ()):
        if name == "package-only":
            continue
        if name == "scenario-coverage" and isinstance(spec, dict):
            out[name] = {key: value for key, value in spec.items() if key != "table"}
        elif name == "stand-ins":
            out[name] = {}
        else:
            out[name] = spec
    return out


def _fakes(value: dict[str, Any]) -> dict[str, Any]:
    steps = str(value.get("path", "")).strip("/").split("/")
    out = {"folder": "/".join(steps[1:]), "for": list(value.get("for", []))}
    if "prefix" in value:
        out["prefix"] = value["prefix"]
    return out


def _docs(old: OldProfile, gathered: Gathered) -> dict[str, Any]:
    docs: dict[str, Any] = {}
    entry = next((name for name, part in old.parts.items() if part.entry), None)
    if entry:
        docs["entry"] = entry
    if gathered.pages:
        docs["pages"] = gathered.pages
    if old.get("naming"):
        docs["naming"] = deepcopy(old.get("naming"))
    if gathered.root:
        docs["examples"] = [gathered.root]
    if gathered.notes:
        docs["example_notes"] = gathered.notes
    return docs

