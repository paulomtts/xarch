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

The profile may accept a group by its nodes (`cycles.accepted`): a group whose nodes are exactly an entry's is not
reported, and the enforcement section names it instead. It may leave a node out of the graph (`cycles.left_out`), such
as a composition root that may import everything: no dependency runs from it or to it, so a group is what is left once
it is gone, and each node left out that a group of the whole graph holds is named instead. An entry of either list
that accepts nothing (a group no group is, a node in no group of the whole graph) is itself a cycles violation, at the
folder of its first node, so both lists can only shrink.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.imports import dotted, targets
from xarch.modules.rules.application.logic.places import repeat_child
from xarch.modules.rules.domain.outcomes import Sifted
from xarch.modules.rules.domain.parsed import SourceFile
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import Excused
from xarch.profile_values.placement import AcceptedCycle, Repeat

Edge = tuple[str, int, str]
"""An import that makes one node depend on another: the file, its line, and what it imports, dotted."""

Graph = dict[str, dict[str, list[Edge]]]
"""Each node, the nodes it depends on, and the imports that make each dependency, by file then line."""


ACCEPTED = "cycles.accepted"
LEFT_OUT = "cycles.left_out"


def violations(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation]:
    """Each group not accepted, then each entry of cycles.accepted and cycles.left_out that accepts nothing."""
    found = checked(files, profile, root)
    return [*(v for v in found.kept if isinstance(v, Violation)), *found.stale]


def checked(files: Iterable[SourceFile], profile: Profile, root: str) -> Sifted:
    """The groups of the graph once the nodes left out are gone, each one cycles.accepted names taken out and named;
    each entry of either list that accepts nothing, as a violation; and each node left out that a group held, named."""
    edges = _edges(files, profile, root)
    whole = _groups(edges)
    out = {"/".join(entry.node): entry for entry in profile.cycles_left_out}
    kept = {a: {b: imports for b, imports in deps.items() if b not in out} for a, deps in edges.items() if a not in out}
    accepted = [({"/".join(node) for node in entry.group}, entry) for entry in profile.cycles_accepted]
    found: list[Violation] = []
    excused: list[Excused] = []
    used: set[int] = set()
    for group in _groups(kept):
        violation = _violation(group, kept)
        index = next((i for i, (nodes, _) in enumerate(accepted) if nodes == set(group)), None)
        if index is None:
            found.append(violation)
            continue
        used.add(index)
        excused.append(Excused("cycles", violation.file, violation.line, ACCEPTED, violation.message,
                               accepted[index][1].why))
    stale = [_unaccepted(entry, root) for i, (_, entry) in enumerate(accepted) if i not in used]
    for node, entry in out.items():
        group = next((group for group in whole if node in group), None)
        if group is None:
            stale.append(Violation(f"{root}/{node}", 0, f"{LEFT_OUT} leaves out {node}, which is in no cycle "
                                                        f"({LEFT_OUT})", "cycles", f"drop the entry of {node} from {LEFT_OUT}"))
        else:
            excused.append(Excused("cycles", f"{root}/{node}", 0, LEFT_OUT,
                                   f"{node} is left out of cycles, though it is in a cycle of {_and(group)}", entry.why))
    return Sifted(tuple(found), tuple(stale), tuple(excused))


def _unaccepted(entry: AcceptedCycle, root: str) -> Violation:
    named = _and(["/".join(node) for node in entry.group])
    return Violation(f"{root}/{'/'.join(entry.group[0])}", 0,
                     f"{ACCEPTED} accepts a cycle of {named}, and cycles finds none ({ACCEPTED})", "cycles",
                     f"drop the entry of {named} from {ACCEPTED}, or write its group as a cycles finding names it")


def _edges(files: Iterable[SourceFile], profile: Profile, root: str) -> Graph:
    """Each node, the nodes it depends on, and the imports that make each dependency (see Graph)."""
    if not profile.repeats:
        return {}
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
    return edges


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
