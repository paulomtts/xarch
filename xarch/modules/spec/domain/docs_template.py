"""Filling a docs template from an architecture: the author writes the prose, the file supplies the structure.

A template is markdown with placeholders, each `{{name}}` or `{{name:argument}}`, replaced by text built from the
architecture. Prose, diagrams and code examples stay as the author wrote them; only these are generated:

    {{tree}}               the layout, one line per folder and file, below a root line the template writes itself;
                           a part's line carries its role, any other line its note from `notes`
    {{rules_table}}        the dependency rules as a table: one row per part, in the order of `parts`, saying what
                           the part may import (its own part is implied, so it is not listed)
    {{layers:<name>}}      the chain `layers.<name>` as `a/` → `b/` → ..., each part by its path
    {{placement}}          the `placement` order as `a` → `b` → ..., each part by its name
    {{litmus:<part>}}      the part's litmus test, as a "> [!TIP]" block
    {{naming}}             the `naming` rows as a table
    {{entry}}              the entry point's path, e.g. web
    {{driver_proves}}      what a test of the entry point proves
    {{driver_test}}        the entry point's example test, as its file holds it

A placeholder the template does not use is fine. One that is unknown, or that needs what the architecture does not
define (a part, a layer, an entry point, a placement), fails the whole template with every problem listed.
"""
from __future__ import annotations

import re
from collections.abc import Callable

from xarch.modules.spec.domain.errors import InvalidTemplate
from xarch.modules.spec.domain.values import EACH, EVERYTHING, Architecture, Layout, Part, Target

PLACEHOLDER = re.compile(r"\{\{(.*?)\}\}")
MODULE = "<module>"                    # how the tree shows the folder every module gets
NOTE_GAP = 3                           # spaces between the longest line of the tree and its note
ARROW = " → "


def fill(template: str, architecture: Architecture, source: str, driver_test: str | None = None) -> str:
    """The template with every placeholder replaced; raises InvalidTemplate listing every problem."""
    problems: list[str] = []

    def replace(match: re.Match[str]) -> str:
        name, _, argument = match[1].strip().partition(":")
        render = _RENDERERS.get(name)
        if render is None or (argument == "") == (name in _WITH_ARGUMENT):
            problems.append(f"unknown placeholder {match[0]}: use {', '.join(_KNOWN)}")
            return match[0]
        try:
            return render(architecture, argument.strip(), driver_test)
        except _Missing as missing:
            problems.append(f"{match[0]}: {missing}")
            return match[0]

    text = PLACEHOLDER.sub(replace, template)
    if problems:
        raise InvalidTemplate(source, problems)
    return text


class _Missing(Exception):
    """What a placeholder needs and the architecture does not define."""


def _tree(architecture: Architecture, _: str, __: str | None) -> str:
    roles = {part.path: part.role for part in architecture.parts.values()}
    lines = list(_tree_lines(architecture.layout, (), "", {**architecture.notes, **roles}))
    width = max((len(label) for label, note in lines if note), default=0) + NOTE_GAP
    return "\n".join(f"{label:<{width}}{note}" if note else label for label, note in lines)


def _tree_lines(tree: Layout, path: tuple[str, ...], indent: str,
                notes: dict[tuple[str, ...], str]) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []
    for i, (name, sub) in enumerate(tree.items()):
        last = i == len(tree) - 1
        here = path + (name,)
        shown = (MODULE if name == EACH else name) + ("" if sub is None else "/")
        lines.append((f"{indent}{'└── ' if last else '├── '}{shown}", notes.get(here, "")))
        if sub:
            lines += _tree_lines(sub, here, indent + ("    " if last else "│   "), notes)
    return lines


def _rules_table(architecture: Architecture, _: str, __: str | None) -> str:
    rows = [f"| `{_shown(architecture, part)}` | {_may_import(architecture, part)} |"
            for part in architecture.parts.values()]
    return "\n".join(["| Part | May import |", "|---|---|", *rows])


def _may_import(architecture: Architecture, part: Part) -> str:
    """What a part may import, in the order of its rule: consecutive parts in one scope share their phrase."""
    targets = [t for t in architecture.rules.get(part.name, ()) if t.part != part.name]
    if any(t.part == EVERYTHING for t in targets):
        return "everything"
    phrases: list[tuple[str, list[str]]] = []          # (scope phrase, the targets it covers)
    for target in targets:
        scope = {"own": "its own module's ", "any": "any module's "}.get(target.scope, "")
        shown = f"`{_target(architecture, target)}`"
        if scope and phrases and phrases[-1][0] == scope:
            phrases[-1][1].append(shown)
        else:
            phrases.append((scope, [shown]))
    return ", ".join(scope + _and(names) for scope, names in phrases) or "nothing"


def _target(architecture: Architecture, target: Target) -> str:
    shown = _shown(architecture, architecture.parts[target.part])
    return shown.removesuffix("/") + "/" + "/".join(target.sub) if target.sub else shown


def _layers(architecture: Architecture, name: str, _: str | None) -> str:
    if name not in architecture.layers:
        known = ", ".join(architecture.layers) or "none"
        raise _Missing(f"the architecture has no layer '{name}' (its layers: {known})")
    return ARROW.join(f"`{_shown(architecture, architecture.parts[part])}`" for part in architecture.layers[name])


def _placement(architecture: Architecture, _: str, __: str | None) -> str:
    if not architecture.placement:
        raise _Missing("the architecture has no `placement`")
    return ARROW.join(f"`{name}`" for name in architecture.placement)


def _litmus(architecture: Architecture, name: str, _: str | None) -> str:
    part = _part(architecture, name)
    if not part.litmus:
        raise _Missing(f"part '{name}' has no litmus test")
    return f"> [!TIP]\n> **Litmus test.** {part.litmus}"


def _naming(architecture: Architecture, _: str, __: str | None) -> str:
    if not architecture.naming:
        raise _Missing("the architecture has no `naming`")
    rows = [f"| {row.kind} | {_ticked(row.where)} | {row.pattern} | {_ticked(row.example)} |"
            for row in architecture.naming]
    return "\n".join(["| Kind | Where | Pattern | Example |", "|---|---|---|---|", *rows])


def _entry(architecture: Architecture, _: str, __: str | None) -> str:
    return "/".join(_entry_part(architecture).path)


def _driver_proves(architecture: Architecture, _: str, __: str | None) -> str:
    entry = _entry_part(architecture)
    if not entry.driver_proves:
        raise _Missing(f"the entry point '{entry.name}' has no `driver_proves`")
    return entry.driver_proves


def _driver_test(architecture: Architecture, _: str, driver_test: str | None) -> str:
    entry = _entry_part(architecture)
    if driver_test is None:
        raise _Missing(f"the entry point '{entry.name}' has no `driver_test`")
    return driver_test


def _entry_part(architecture: Architecture) -> Part:
    if architecture.entry is None:
        raise _Missing("no part is the entry point: mark one `entry: true`")
    return architecture.entry


def _part(architecture: Architecture, name: str) -> Part:
    if name not in architecture.parts:
        raise _Missing(f"the architecture defines no part '{name}'")
    return architecture.parts[name]


def _shown(architecture: Architecture, part: Part) -> str:
    """A part as the docs name it: its path below the module for a module's part, ending in / for a folder."""
    root = architecture.module_root()
    path = part.path[len(root) + 1:] if part.in_module and root is not None else part.path
    return "/".join(path) + ("" if architecture.is_file(part.path) else "/")


def _ticked(names: tuple[str, ...]) -> str:
    return ", ".join(f"`{name}`" for name in names)


def _and(items: list[str]) -> str:
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}"


_RENDERERS: dict[str, Callable[[Architecture, str, str | None], str]] = {
    "tree": _tree, "rules_table": _rules_table, "layers": _layers, "placement": _placement, "litmus": _litmus,
    "naming": _naming, "entry": _entry, "driver_proves": _driver_proves, "driver_test": _driver_test,
}
_WITH_ARGUMENT = {"layers", "litmus"}
_KNOWN = [f"{{{{{name}:<{'part' if name == 'litmus' else 'name'}>}}}}" if name in _WITH_ARGUMENT
          else f"{{{{{name}}}}}" for name in _RENDERERS]
