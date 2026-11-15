"""xarch where, shown: short labelled lines for a person or an agent's context, and one JSON document."""
from __future__ import annotations

import json
from typing import Any

from xarch.modules.rules.contract import Reach, TierInfo, Where

LABEL = 16
NOT_CHECKED = "not checked"
EXISTS, NEW = "exists", "new"


def where_lines(profile: str, where: Where) -> list[str]:
    """One `label: text` line per answer, in the order a reader needs them; an answer that does not apply is left out."""
    lines = [_line("path", f"{where.path} ({EXISTS if where.exists else NEW})")]
    if where.kind in ("test", "support", "fake"):
        lines += _test_lines(where)
    else:
        lines += _place_lines(where)
    if where.note:
        lines.append(_line("note", where.note))
    return lines


def _place_lines(where: Where) -> list[str]:
    if where.kind != "part":
        lines = [_line("part", f"none: {where.kind}")]
        if where.nearest:
            lines.append(_line("nearest", ", ".join(f"{n.folder} ({n.path})" for n in where.nearest)))
        if where.kind == "ungoverned" and where.nearest:
            lines.append(_line("closed-tree", "on: `xarch check` reports it" if where.closed_tree
                               else "off: `xarch check` does not read it"))
        return lines
    lines = [_line("part", _part(where)), _line("role", where.role), _line("litmus", where.litmus),
             _line("may import", where.may_import_text), _line("libraries", _libraries(where))]
    if where.forbidden:
        lines.append(_line("may not use", ", ".join(where.forbidden)))
    if where.tier is not None:
        lines.append(_line("tested by", f"{where.tier.name} tier: {where.test_folder}{where.test_file}"))
    else:
        lines.append(_line("tested by", f"nothing: {where.untested}" if where.untested else "no tier"))
    return lines


def _test_lines(where: Where) -> list[str]:
    if where.kind == "fake":
        return [_line("kind", "fake"), _line("fakes", f"live in {where.fakes_path}")]
    tier = f", {where.tier.name} tier" if where.tier is not None else ""
    lines = [_line("kind", f"{where.kind}{tier}")]
    if where.part:
        lines += [_line("mirrors", _part(where)), _line("may import", where.may_import_text)]
        if where.types_only:
            lines.append(_line("types only", ", ".join(where.types_only)))
        if where.forbidden:
            lines.append(_line("may not use", ", ".join(where.forbidden)))
    if where.tier is not None:
        lines.append(_line("fakes", f"may import {where.fakes_path}" if where.may_use_fakes else "may not import them"))
        lines += [_line("tier proves", where.tier.proves), _line("tier may touch", where.tier.may_touch),
                  _line("tier litmus", where.tier.litmus), _line("test code", f"from {where.test_code_from} only")]
    return lines


def _part(where: Where) -> str:
    return f"{where.folder} in {where.singular} '{where.instance}'" if where.instance else where.folder


def _libraries(where: Where) -> str:
    if where.libraries is None:
        return NOT_CHECKED
    return ", ".join(where.libraries) or "none"


def _line(label: str, text: str) -> str:
    return f"{label}:".ljust(LABEL) + text


def where_document(profile: str, where: Where) -> str:
    """The JSON of an answer: `ok`, `profile`, `path`, `exists`, `kind` and the fields the README lists, a field that
    does not apply null (or empty for a list)."""
    document: dict[str, Any] = {
        "ok": True, "profile": profile, "path": where.path, "exists": where.exists, "kind": where.kind,
        "part": _part_document(where), "may_import": [_reach(r) for r in where.may_import],
        "may_import_text": where.may_import_text or None, "libraries": _list(where.libraries),
        "forbidden": list(where.forbidden), "tier": _tier(where.tier),
        "tested_in": {"folder": where.test_folder, "file": where.test_file} if where.test_folder else None,
        "untested": where.untested or None,
        "nearest": [{"part": n.part, "folder": n.folder, "path": n.path} for n in where.nearest],
        "closed_tree": where.closed_tree if where.kind == "ungoverned" and where.nearest else None,
        "test": _test(where), "note": where.note or None}
    return json.dumps(document, indent=2, ensure_ascii=False)


def _part_document(where: Where) -> dict[str, str] | None:
    if not where.part:
        return None
    return {"name": where.part, "folder": where.folder, "instance": where.instance, "singular": where.singular,
            "role": where.role, "litmus": where.litmus}


def _reach(reach: Reach) -> dict[str, str]:
    return {"part": reach.part, "scope": reach.scope, "folder": reach.folder, "path": reach.path}


def _tier(tier: TierInfo | None) -> dict[str, str] | None:
    return None if tier is None else {"name": tier.name, "proves": tier.proves, "may_touch": tier.may_touch,
                                      "litmus": tier.litmus}


def _list(values: tuple[str, ...] | None) -> list[str] | None:
    return None if values is None else list(values)


def _test(where: Where) -> dict[str, Any] | None:
    if where.kind not in ("test", "support", "fake"):
        return None
    return {"may_use_fakes": where.may_use_fakes, "fakes_path": where.fakes_path or None,
            "types_only": list(where.types_only), "code_from": where.test_code_from or None}
