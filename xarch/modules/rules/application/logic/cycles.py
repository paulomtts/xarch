"""The cycles check: no instance of a repeating folder imports, through the others, from itself.

The instances of every repeating folder are the nodes of one graph: a module and a plugin may depend on each other.
Instance A depends on instance B when a file below A imports from below B, absolutely or relatively, whatever the
parts (under the bundled rules only an adapter can, importing B's contract). Every elementary cycle of that graph is
one violation: its instances in order, starting from the one first by name, each followed by the import that makes it
depend on the next (the first such import, by file then line), reported at the first of those imports. A file in no
instance is not this check's business, and an import within one instance is no dependency.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.logic.placement import Repeat
from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.imports import dotted, targets
from xarch.modules.rules.domain.values import Profile, SourceFile

Edge = tuple[str, int, str]
"""An import that makes one instance depend on another: the file, its line, and what it imports, dotted."""


def violations(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation]:
    if not profile.repeats:
        return []
    parsed = [(f, *dotted(f.path)) for f in files]
    known = {steps for _, steps, _ in parsed}
    edges: dict[str, dict[str, Edge]] = {}
    for file, steps, is_package in sorted(parsed, key=lambda p: p[0].name):
        source = _instance(profile.repeats, steps)
        if source is None:
            continue
        for line, target in sorted(targets(file.imports, steps if is_package else steps[:-1], known, root)):
            depends = _instance(profile.repeats, target)
            if depends is not None and depends != source:
                edges.setdefault(source, {}).setdefault(depends, (file.name, line, ".".join((root, *target))))
    return [_violation(cycle, edges) for cycle in _cycles(edges)]


def _instance(repeats: tuple[Repeat, ...], steps: tuple[str, ...]) -> str | None:
    """The instance a path lies in, as the folder holding it and its name, e.g. "modules/docs"."""
    for repeat in repeats:
        if len(steps) > len(repeat.root) and steps[:len(repeat.root)] == repeat.root:
            return "/".join(steps[:len(repeat.root) + 1])
    return None


def _cycles(edges: dict[str, dict[str, Edge]]) -> list[list[str]]:
    """Every elementary cycle once, as its instances from the least by name."""
    found: list[list[str]] = []
    for start in sorted(edges):
        stack = [(start, [start])]
        while stack:
            node, path = stack.pop()
            for nxt in sorted(edges.get(node, {}), reverse=True):
                if nxt == start:
                    found.append(path)
                elif nxt > start and nxt not in path:
                    stack.append((nxt, [*path, nxt]))
    return sorted(found)


def _violation(cycle: list[str], edges: dict[str, dict[str, Edge]]) -> Violation:
    hops = [edges[a][b] for a, b in zip(cycle, [*cycle[1:], cycle[0]])]
    shown = " → ".join([*cycle, cycle[0]])
    why = "; ".join(f"{file}:{line} imports {target}" for file, line, target in hops)
    first = hops[0]
    fix = (f"break the cycle: remove the import of {first[2]} at {first[0]}:{first[1]}, or move what it needs to a "
           "part that both may import")
    return Violation(first[0], first[1], f"{shown} import each other in a cycle: {why} (cycles)", "cycles", fix)
