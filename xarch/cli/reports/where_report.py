"""xarch where, shown: short labelled lines for a person or an agent's context, and one JSON document."""
from __future__ import annotations

from typing import Any

from xarch.cli.reports.document import document
from xarch.kernel.placement import EVERYTHING
from xarch.modules.rules.contract import (
    ALL,
    ANY,
    CoveringTest,
    Fake,
    InPart,
    InStructure,
    InTests,
    Litmus,
    NearestView,
    PartShown,
    ReachView,
    TierInfoView,
    Ungoverned,
    Untested,
    WhereAnswer,
)

LABEL = 16
NOT_CHECKED = "not checked"
EXISTS, NEW = "exists", "new"


def where_lines(where: WhereAnswer) -> list[str]:
    """One `label: text` line per answer, in the order a reader needs them; an answer that does not apply is left out."""
    lines = [_line("path", f"{where.path} ({EXISTS if where.exists else NEW})")]
    match where:
        case InPart():
            lines += _part_lines(where)
        case InStructure():
            lines += _none_lines(where.kind, where.nearest)
        case Ungoverned():
            lines += _none_lines(where.kind, where.nearest)
            if where.closed_tree is not None:
                lines.append(_line("closed-tree", "on: `xarch check` reports it" if where.closed_tree
                                   else "off: `xarch check` does not read it"))
        case InTests():
            lines += _test_lines(where)
        case Fake():
            lines += [_line("kind", where.kind), _line("fakes", f"live in {where.fakes_path}")]
    lines += [_line("counterparts", f"{pair.id}: needs {pair.needs} (for {pair.source})") for pair in where.counterparts]
    note = _note(where)
    if note:
        lines.append(_line("note", note))
    return lines


def _none_lines(kind: str, nearest: tuple[NearestView, ...]) -> list[str]:
    lines = [_line("part", f"none: {kind}")]
    if nearest:
        lines.append(_line("nearest", ", ".join(f"{n.folder} ({n.path})" for n in nearest)))
    return lines


def _part_lines(where: InPart) -> list[str]:
    lines = [_line("part", _part(where.part)), _line("role", where.part.role),
             *([_line("optional", "yes: structure does not ask for it")] if where.part.optional else []),
             *_litmus_lines("litmus", where.part.litmus or "none", where.part.litmus_list),
             _line("may import", where.may_import_text), _line("libraries", _libraries(where.libraries))]
    if where.uses_never:
        lines.append(_line("never uses", ", ".join(where.uses_never)))
    match where.tested:
        case CoveringTest(tier=tier, path=path):
            lines.append(_line("tested by", f"{tier.name} tier: {path}"))
        case Untested(reason):
            lines.append(_line("tested by", f"nothing: {reason}"))
        case None:
            lines.append(_line("tested by", "no tier"))
    lines += [_line("accepted", f"{entry.written}: {entry.why} (parts.{where.part.name}.imports.accepted)")
              for entry in where.accepted]
    return lines


def _test_lines(where: InTests) -> list[str]:
    tier = f", {where.tier.name} tier" if where.tier is not None else ""
    lines = [_line("kind", f"{where.kind}{tier}")]
    if where.mirrors is not None:
        lines += [_line("mirrors", _part(where.mirrors)), _line("may import", where.may_import_text)]
        if where.types_only:
            lines.append(_line("types only", ", ".join(where.types_only)))
        if where.uses_never:
            lines.append(_line("never uses", ", ".join(where.uses_never)))
    if where.tier is not None:
        lines.append(_line("fakes", f"may import {where.fakes_path}" if where.may_use_fakes else "may not import them"))
        lines += [_line("tier proves", where.tier.proves), _line("tier may touch", where.tier.may_touch),
                  *_litmus_lines("tier litmus", where.tier.litmus, where.tier.litmus_list),
                  _line("test code", _code_from(where))]
    return lines


def _litmus_lines(label: str, text: str, entries: tuple[Litmus, ...]) -> list[str]:
    """A litmus of one text on its line; a list as what makes code belong on its line, then one line per entry, its
    label and mode before its question, its lines joined."""
    if not entries:
        return [_line(label, text)]
    modes = {entry.mode for entry in entries}
    said = ("at least one `any` entry and every `all` entry answers yes:" if modes == {ANY, ALL}
            else "at least one of these answers yes:" if modes == {ANY} else "each of these answers yes:")
    return [_line(label, said), *(" " * LABEL + f"{entry.label} ({entry.mode}): " + " ".join(entry.ask.split())
                                  for entry in entries)]


def _litmus_document(text: str, entries: tuple[Litmus, ...]) -> str | list[dict[str, str]]:
    """A litmus in the JSON: its one text, else each entry of its list, {ask, label, mode}."""
    return [{"ask": entry.ask, "label": entry.label, "mode": entry.mode} for entry in entries] if entries else text


def _code_from(where: InTests) -> str:
    shared = f" and the shared {', '.join(where.shared)}" if where.shared else ""
    return f"from {where.code_from}{shared} only"


def _note(where: WhereAnswer) -> str:
    return "" if isinstance(where, (InPart, InStructure)) else where.note


def _part(part: PartShown) -> str:
    return f"{part.folder} in {part.singular} '{part.instance}'" if part.instance else part.folder


def _libraries(libraries: tuple[str, ...] | None) -> str:
    if libraries is None:
        return NOT_CHECKED
    if EVERYTHING in libraries:
        return "any outside package"
    return ", ".join(libraries) or "none"


def _line(label: str, text: str) -> str:
    return f"{label}:".ljust(LABEL) + text


def where_document(profile: str, where: WhereAnswer) -> str:
    """The JSON of an answer: `ok`, `profile`, `path`, `exists`, `kind` and the fields the README lists, a field that
    does not apply null (or empty for a list)."""
    shown: dict[str, Any] = {
        "ok": True, "profile": profile, "path": where.path, "exists": where.exists, "kind": where.kind,
        "part": None, "may_import": [], "may_import_text": None, "libraries": None, "never_uses": [], "tier": None,
        "tested_in": None, "untested": None, "nearest": [], "closed_tree": None, "test": None, "note": None}
    match where:
        case InPart():
            shown |= {"part": _part_document(where.part), "may_import": [_reach(r) for r in where.may_import],
                         "may_import_text": where.may_import_text or None, "libraries": _list(where.libraries),
                         "never_uses": list(where.uses_never)}
            if where.accepted:
                shown["accepted_imports"] = [{"import": entry.written, "why": entry.why} for entry in where.accepted]
            match where.tested:
                case CoveringTest(tier=tier, folder=folder, file=file):
                    shown |= {"tier": _tier(tier), "tested_in": {"folder": folder, "file": file}}
                case Untested(reason):
                    shown["untested"] = reason
        case InStructure():
            shown["nearest"] = [_near(n) for n in where.nearest]
        case Ungoverned():
            shown |= {"nearest": [_near(n) for n in where.nearest], "closed_tree": where.closed_tree,
                         "note": where.note or None}
        case InTests():
            shown |= {"part": _part_document(where.mirrors) if where.mirrors is not None else None,
                         "may_import": [_reach(r) for r in where.may_import],
                         "may_import_text": where.may_import_text or None, "never_uses": list(where.uses_never),
                         "tier": _tier(where.tier) if where.tier is not None else None,
                         "test": {"may_use_fakes": where.may_use_fakes, "fakes_path": where.fakes_path or None,
                                  "types_only": list(where.types_only), "code_from": where.code_from or None,
                                  **({"shared": list(where.shared)} if where.shared else {})},
                         "note": where.note or None}
        case Fake():
            shown |= {"test": {"may_use_fakes": False, "fakes_path": where.fakes_path or None, "types_only": [],
                                  "code_from": where.code_from or None}, "note": where.note or None}
    if where.counterparts:
        shown["counterparts"] = [{"id": pair.id, "for": pair.source, "has": pair.has, "needs": pair.needs}
                                 for pair in where.counterparts]
    return document(shown)


def _part_document(part: PartShown) -> dict[str, Any]:
    return {"name": part.name, "folder": part.folder, "instance": part.instance, "singular": part.singular,
            "role": part.role, "litmus": _litmus_document(part.litmus, part.litmus_list),
            **({"optional": True} if part.optional else {})}


def _reach(reach: ReachView) -> dict[str, str]:
    return {"part": reach.part, "scope": reach.scope, "folder": reach.folder, "path": reach.path}


def _near(near: NearestView) -> dict[str, str]:
    return {"part": near.part, "folder": near.folder, "path": near.path}


def _tier(tier: TierInfoView) -> dict[str, Any]:
    return {"name": tier.name, "proves": tier.proves, "may_touch": tier.may_touch,
            "litmus": _litmus_document(tier.litmus, tier.litmus_list)}


def _list(values: tuple[str, ...] | None) -> list[str] | None:
    return None if values is None else list(values)
