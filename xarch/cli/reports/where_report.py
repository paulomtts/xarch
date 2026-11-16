"""xarch where, shown: short labelled lines for a person or an agent's context, and one JSON document."""
from __future__ import annotations

from typing import Any

from xarch.cli.reports.document import document
from xarch.kernel.placement import EVERYTHING
from xarch.modules.rules.contract import (
    CoveringTest,
    Fake,
    InPart,
    InStructure,
    InTests,
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
    lines = [_line("part", _part(where.part)), _line("role", where.part.role), _line("litmus", where.part.litmus),
             _line("may import", where.may_import_text), _line("libraries", _libraries(where.libraries))]
    if where.forbidden:
        lines.append(_line("may not use", ", ".join(where.forbidden)))
    match where.tested:
        case CoveringTest(tier=tier, path=path):
            lines.append(_line("tested by", f"{tier.name} tier: {path}"))
        case Untested(reason):
            lines.append(_line("tested by", f"nothing: {reason}"))
        case None:
            lines.append(_line("tested by", "no tier"))
    return lines


def _test_lines(where: InTests) -> list[str]:
    tier = f", {where.tier.name} tier" if where.tier is not None else ""
    lines = [_line("kind", f"{where.kind}{tier}")]
    if where.mirrors is not None:
        lines += [_line("mirrors", _part(where.mirrors)), _line("may import", where.may_import_text)]
        if where.types_only:
            lines.append(_line("types only", ", ".join(where.types_only)))
        if where.forbidden:
            lines.append(_line("may not use", ", ".join(where.forbidden)))
    if where.tier is not None:
        lines.append(_line("fakes", f"may import {where.fakes_path}" if where.may_use_fakes else "may not import them"))
        lines += [_line("tier proves", where.tier.proves), _line("tier may touch", where.tier.may_touch),
                  _line("tier litmus", where.tier.litmus), _line("test code", f"from {where.code_from} only")]
    return lines


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
        "part": None, "may_import": [], "may_import_text": None, "libraries": None, "forbidden": [], "tier": None,
        "tested_in": None, "untested": None, "nearest": [], "closed_tree": None, "test": None, "note": None}
    match where:
        case InPart():
            shown |= {"part": _part_document(where.part), "may_import": [_reach(r) for r in where.may_import],
                         "may_import_text": where.may_import_text or None, "libraries": _list(where.libraries),
                         "forbidden": list(where.forbidden)}
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
                         "may_import_text": where.may_import_text or None, "forbidden": list(where.forbidden),
                         "tier": _tier(where.tier) if where.tier is not None else None,
                         "test": {"may_use_fakes": where.may_use_fakes, "fakes_path": where.fakes_path or None,
                                  "types_only": list(where.types_only), "code_from": where.code_from or None},
                         "note": where.note or None}
        case Fake():
            shown |= {"test": {"may_use_fakes": False, "fakes_path": where.fakes_path or None, "types_only": [],
                                  "code_from": where.code_from or None}, "note": where.note or None}
    return document(shown)


def _part_document(part: PartShown) -> dict[str, str]:
    return {"name": part.name, "folder": part.folder, "instance": part.instance, "singular": part.singular,
            "role": part.role, "litmus": part.litmus}


def _reach(reach: ReachView) -> dict[str, str]:
    return {"part": reach.part, "scope": reach.scope, "folder": reach.folder, "path": reach.path}


def _near(near: NearestView) -> dict[str, str]:
    return {"part": near.part, "folder": near.folder, "path": near.path}


def _tier(tier: TierInfoView) -> dict[str, str]:
    return {"name": tier.name, "proves": tier.proves, "may_touch": tier.may_touch, "litmus": tier.litmus}


def _list(values: tuple[str, ...] | None) -> list[str] | None:
    return None if values is None else list(values)
