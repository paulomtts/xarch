"""The cycles check: no instance of a repeating folder imports, through the others, from itself.

The instances of every repeating folder are the nodes of one graph: a module and a plugin may depend on each other.
So is each folder the layout names beside the instances, in the repeating folder's own folder (adapters/web/ beside
adapters/<adapter>/): it is no instance, for placement, `where` and every other check, but a cycle may run through
it. A file lying in that folder is no node, nor is a part the layout names anywhere else. Node A depends on node B
when a file below A imports from below B, absolutely or relatively, whatever the parts (under the bundled rules only
an adapter can, importing B's contract). Each group of nodes that all reach each other (a strongly connected group of
two or more) is one violation, however many cycles run through it: its nodes by name, how many dependencies run
between them, and the dependencies to cut, each with every import that makes it (once per file and line, by file
then line).

The dependencies to cut are those that go back in an order of the group's nodes chosen so that few imports go back
(the greedy order of Eades, Lin and Smyth, each dependency weighing as many imports as make it): a node no other one
left in the group depends on goes first, one that depends on none left goes last, and else the one whose imports out
weigh most over its imports in goes first, the first by name among equals. Cutting them all leaves the group with no
cycle. The violation is reported at the first import of the first of them by name. A file in no node is not this
check's business, and an import within one node is no dependency.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.imports import dotted, targets
from xarch.modules.rules.application.logic.places import repeat_child
from xarch.modules.rules.domain.parsed import SourceFile
from xarch.modules.rules.domain.profile import Profile
from xarch.profile_values.placement import Repeat

Edge = tuple[str, int, str]
"""An import that makes one node depend on another: the file, its line, and what it imports, dotted."""

Graph = dict[str, dict[str, list[Edge]]]
"""Each node, the nodes it depends on, and the imports that make each dependency, by file then line."""


def violations(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation]:
    if not profile.repeats:
        return []
    parsed = [(f, *dotted(f.path, profile.language.marks)) for f in files]
    known = {steps for _, steps, _ in parsed}
    files = frozenset(steps for _, steps, is_package in parsed if not is_package)
    edges: Graph = {}
    for file, steps, is_package in sorted(parsed, key=lambda p: p[0].name):
        source = _node(profile.repeats, steps, files)
        if source is None:
            continue
        for line, target in sorted(set(targets(file.imports, steps if is_package else steps[:-1], known, root))):
            depends = _node(profile.repeats, target, files)
            if depends is not None and depends != source:
                edges.setdefault(source, {}).setdefault(depends, []).append((file.name, line, ".".join((root, *target))))
    return [_violation(group, edges) for group in _groups(edges)]


def _node(repeats: tuple[Repeat, ...], steps: tuple[str, ...], files: frozenset[tuple[str, ...]]) -> str | None:
    """The node a path lies in, as the folder holding it and its name, e.g. "modules/docs": an instance, or a folder
    the parts write by name beside the instances; none for a file of the app lying beside them."""
    folder = repeat_child(repeats, steps, files)
    return None if folder is None else "/".join(folder)


def _reach(start: str, edges: Graph) -> set[str]:
    seen: set[str] = set()
    todo = [start]
    while todo:
        for nxt in edges.get(todo.pop(), {}):
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return seen


def _groups(edges: Graph) -> list[list[str]]:
    """Each strongly connected group of two or more nodes once, its nodes by name, the groups by their first."""
    reach = {node: _reach(node, edges) for node in edges}
    found: list[list[str]] = []
    for node in sorted(edges):
        group = sorted(other for other in reach[node] if node in reach.get(other, set()))
        if node in group and group[0] == node:
            found.append(group)
    return found


def _order(group: list[str], weight: dict[tuple[str, str], int]) -> list[str]:
    """The group's nodes in the greedy order that leaves few imports going back (see the module's text)."""
    left = set(group)
    first: list[str] = []
    last: list[str] = []

    def moves(u: str) -> tuple[int, int]:
        return (sum(n for (a, b), n in weight.items() if a == u and b in left),
                sum(n for (a, b), n in weight.items() if b == u and a in left))

    while left:
        while (ends := [u for u in sorted(left) if moves(u)[0] == 0]) or (
                starts := [u for u in sorted(left) if moves(u)[1] == 0]):
            if ends:
                last.insert(0, ends[0])
                left.remove(ends[0])
            else:
                first.append(starts[0])
                left.remove(starts[0])
        if left:
            best = max(sorted(left), key=lambda u: moves(u)[0] - moves(u)[1])
            first.append(best)
            left.remove(best)
    return first + last


def _cuts(group: list[str], edges: Graph) -> list[tuple[str, str]]:
    """The dependencies of the group that go back in its greedy order, by name."""
    inside = set(group)
    weight = {(a, b): len(imports) for a in group for b, imports in edges.get(a, {}).items() if b in inside}
    place = {node: index for index, node in enumerate(_order(group, weight))}
    return sorted((a, b) for a, b in weight if place[a] > place[b])


def _violation(group: list[str], edges: Graph) -> Violation:
    inside = set(group)
    count = sum(1 for a in group for b in edges.get(a, {}) if b in inside)
    cuts = _cuts(group, edges)
    shown = "; ".join(f"{a} → {b}: " + ", ".join(f"{file}:{line} imports {target}" for file, line, target in edges[a][b])
                      for a, b in cuts)
    named = _and([f"{a} → {b}" for a, b in cuts])
    first = edges[cuts[0][0]][cuts[0][1]][0]
    message = (f"{_and(group)} import each other in a cycle, through {count} dependencies; "
               f"{'the one' if len(cuts) == 1 else f'the {len(cuts)}'} to cut: {shown} (cycles)")
    fix = (f"break the cycle: remove the imports of {named} the message lists, or move what they need to a part "
           "that both may import" if len(cuts) == 1 else
           f"break the cycles: remove the imports of {named} the message lists, or move what each needs to a part "
           "that both of its ends may import")
    return Violation(first[0], first[1], message, "cycles", fix)


def _and(items: list[str]) -> str:
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}"
