"""What `cycles` says of the cycles graph, each entry refused at its address when it is written wrong:

    cycles:
      accepted: [{group: [<node>, <node>, ...], why}, ...]   the groups of nodes accepted importing each other
      left_out: [{path: <node>, why}, ...]                   the nodes left out of the graph, such as a composition root

A node is a folder below the app that lies in the folder of a repeating folder: an instance of it, or a folder the
layout names beside the instances. A group lists two nodes or more, each once.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.profile_values.placement import AcceptedCycle, LeftOut, Repeat

KEY = "cycles"
"""The key the entries are written under."""


def cycles(value: Any, repeats: tuple[Repeat, ...], problems: list[str]) -> tuple[tuple[AcceptedCycle, ...],
                                                                                   tuple[LeftOut, ...]]:
    """The groups the profile accepts and the nodes it leaves out, each in the order written; an entry refused adds
    its problem, addressed by its index, and is not read."""
    if not isinstance(value, Mapping):
        problems.append(f"{KEY}: must be a map {{accepted, left_out}}")
        return (), ()
    problems += ck.unknown_keys(value, ("accepted", "left_out"), KEY)
    accepted = _listed(value, "accepted", "{group, why}", "[{group: [<node>, <node>], why: <the reason>}]", problems)
    left = _listed(value, "left_out", "{path, why}", "[{path: <node>, why: <the reason>}]", problems)
    return (tuple(found for index, entry in enumerate(accepted)
                  if (found := _group(entry, f"{KEY}.accepted.{index}", repeats, problems)) is not None),
            tuple(found for index, entry in enumerate(left)
                  if (found := _left(entry, f"{KEY}.left_out.{index}", repeats, problems)) is not None))


def _listed(value: Mapping[Any, Any], key: str, shape: str, such: str, problems: list[str]) -> list[Any]:
    if key not in value:
        return []
    listed = value[key]
    if not isinstance(listed, list) or not listed:
        problems.append(f"{KEY}.{key}: must be a list of {shape}, such as {such}")
        return []
    return listed


def _entry(entry: Any, at: str, keys: tuple[str, str], problems: list[str]) -> bool:
    """Whether the entry at at is a map of keys, each there, and its why one line; each problem said."""
    if not isinstance(entry, Mapping):
        problems.append(f"{at}: must be a map {{{', '.join(keys)}}}")
        return False
    count = len(problems)
    problems += ck.unknown_keys(entry, keys, at)
    problems += [f"{at}: missing `{key}`" for key in keys if key not in entry]
    if "why" in entry and not ck.line(entry["why"]):
        problems.append(f"{at}.why: must be one line of text: why it is accepted")
    return len(problems) == count


def _group(entry: Any, at: str, repeats: tuple[Repeat, ...], problems: list[str]) -> AcceptedCycle | None:
    if not _entry(entry, at, ("group", "why"), problems):
        return None
    written = entry["group"]
    if not isinstance(written, list):
        problems.append(f"{at}.group: must be a list of nodes, such as [{_such(repeats)}, ...]")
        return None
    count = len(problems)
    nodes = [_node(node, f"{at}.group.{index}", repeats, problems) for index, node in enumerate(written)]
    if len(problems) > count:
        return None
    if len(nodes) < 2 or len(set(nodes)) < len(nodes):
        problems.append(f"{at}.group: must list two nodes or more, each once: a cycle runs between nodes")
        return None
    return AcceptedCycle(tuple(node for node in nodes if node is not None), entry["why"])


def _left(entry: Any, at: str, repeats: tuple[Repeat, ...], problems: list[str]) -> LeftOut | None:
    if not _entry(entry, at, ("path", "why"), problems):
        return None
    node = _node(entry["path"], f"{at}.path", repeats, problems)
    return None if node is None else LeftOut(node, entry["why"])


def _node(value: Any, at: str, repeats: tuple[Repeat, ...], problems: list[str]) -> tuple[str, ...] | None:
    """A node by its path below the app; None, said, when it is no path or lies in no repeating folder's folder."""
    steps = ck.below_app(value, at, problems)
    if steps is None:
        return None
    if not any(steps[:-1] == repeat.root for repeat in repeats):
        problems.append(f"{at}: {'/'.join(steps)} is no node of the cycles graph: a node is an instance of a repeating "
                        f"folder, or a folder the layout names beside them, such as {_such(repeats)}")
        return None
    return steps


def _such(repeats: tuple[Repeat, ...]) -> str:
    return " or ".join(f"{'/'.join(repeat.root)}/<{repeat.word}>" for repeat in repeats) or "<folder>/<instance>"
