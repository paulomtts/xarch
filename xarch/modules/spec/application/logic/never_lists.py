"""The lists of `never`, each read into the names it reaches: an entry that is exactly the name of another list of the
block includes that list's names in its place, in order, however deep, and every other entry is read as
`profile_checks.never_names` reads one. A list may not take a name such an entry would read as: a package of the
language's standard library, or one the profile names. Each problem is said at the address of the list it is about,
lists in block order: its name, then its entries, then its includes."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.domain.values import Language

Steps = tuple[str, ...]


@dataclass(frozen=True)
class _Arrival:
    """A name a list reaches: its steps, the text the list whose own entries hold it writes, and that list."""
    steps: Steps
    text: str
    holder: str


@dataclass(frozen=True)
class _Expansion:
    """What a list reaches: its names in order, the first arrival of each kept, and every list it includes however
    deep, each once."""
    names: tuple[_Arrival, ...]
    lists: tuple[str, ...]


def never_lists(value: Any, problems: list[str], language: Language,
                named: Mapping[str, str]) -> dict[str, tuple[Steps, ...] | None] | None:
    """The lists of `never` by name, each the names it reaches in order; a list whose value is no list or is empty, one
    that includes itself however far, and one that includes such a list, is None. None: `never` is no mapping. named is
    each package the profile names, by the key of the first place naming it."""
    if not isinstance(value, Mapping):
        problems.append("never: must be a mapping of list names to lists of dotted names, such as "
                        "{pure: [datetime.datetime.now, socket]}")
        return None
    lists = [name for name in value if ck.text(name) and ck.PART_NAME.fullmatch(name)]
    said = {name: _name_problems(name, language, named) for name in lists}
    entries = {name: _entries(name, value[name], lists, said[name], language) for name in lists}
    edges = {name: tuple(entry for entry in found if isinstance(entry, str)) if found else ()
             for name, found in entries.items()}
    reach = {name: _reach(name, edges) for name in lists}
    looping = {name for name in lists if name in edges[name] or name in reach[name]}
    _say_loops(lists, edges, reach, said)
    order = sorted((len(reach[name]), place, name) for place, name in enumerate(lists)
                   if entries[name] is not None and name not in looping and not reach[name] & looping)
    done: dict[str, _Expansion] = {}
    for _, _, name in order:
        done[name] = _expand(name, entries[name] or (), done, said[name])
    for name in value:
        if name in said:
            problems += said[name]
        else:
            problems.append(f"never: {name!r} is not a list name: use letters, digits, '_' and '-'")
    return {name: tuple(arrival.steps for arrival in done[name].names) if name in done else None for name in lists}


def _name_problems(name: str, language: Language, named: Mapping[str, str]) -> list[str]:
    """The problem of a list's name that an entry would read as the list: the name of a package of the language's
    standard library, or of one the profile names."""
    if name in language.standard_names:
        return [f"never.{name}: a list may not take the name of a package of the {language.checked.title} standard "
                f"library, since an entry {name} would name the list: rename it"]
    if name in named:
        return [f"never.{name}: a list may not take the name of a package this profile names ({named[name]}): rename "
                "it"]
    return []


def _entries(name: str, value: Any, lists: list[str], problems: list[str],
             language: Language) -> tuple[_Arrival | str, ...] | None:
    """A list's entries in written order: an entry that is the name of a list of the block as that name, every other
    as the name it reads as, a refused one left out and said. None: the value is no list or is empty."""
    where = f"never.{name}"
    if not isinstance(value, list) or not value:
        ck.never_names(value, where, problems, language)
        return None
    rest = [item for item in value if not (isinstance(item, str) and item in lists)]
    read = iter(ck.never_names(rest, where, problems, language) or ()) if rest else iter(())
    found: list[_Arrival | str] = []
    for item in value:
        if isinstance(item, str) and item in lists:
            found.append(item)
            continue
        steps = next(read)
        if steps is not None:
            found.append(_Arrival(steps, item, name))
    return tuple(found)


def _reach(name: str, edges: Mapping[str, tuple[str, ...]]) -> set[str]:
    """Every list a list includes however far, not counting a list writing itself; the list itself when it comes back
    to itself through others. Walked without recursion, so a deep block is read whole."""
    reached: set[str] = set()
    waiting = [item for item in edges[name] if item != name]
    while waiting:
        item = waiting.pop()
        if item not in reached:
            reached.add(item)
            waiting += [after for after in edges[item] if after != item]
    return reached


def _say_loops(lists: list[str], edges: Mapping[str, tuple[str, ...]], reach: Mapping[str, set[str]],
               said: Mapping[str, list[str]]) -> None:
    """A list that writes itself, said at it; lists that include each other, said once, at the one written first."""
    covered: set[str] = set()
    for name in lists:
        if name in edges[name]:
            said[name].append(f"never.{name}: includes itself")
        if name in reach[name] and name not in covered:
            covered |= {item for item in reach[name] if name in reach[item]}
            way = _way_back(name, edges, reach)
            drop = "drop one of the two" if len(way) == 1 else "drop one of the includes"
            said[name].append(f"never.{name}: includes itself, through "
                              f"{', '.join(f'never.{item}' for item in way)}: {drop}")


def _way_back(name: str, edges: Mapping[str, tuple[str, ...]], reach: Mapping[str, set[str]]) -> tuple[str, ...]:
    """The lists after a list along the shortest way back to it, each list's includes tried in written order."""
    ways: list[tuple[str, tuple[str, ...]]] = [(name, ())]
    seen = {name}
    for here, way in ways:
        for item in edges[here]:
            if item == name and way:
                return way
            if item not in seen and name in reach[item]:
                seen.add(item)
                ways.append((item, (*way, item)))
    return ()


def _expand(name: str, found: tuple[_Arrival | str, ...], done: Mapping[str, _Expansion],
            problems: list[str]) -> _Expansion:
    """A list's names in order, each included list's names in its place; a list or a name reached twice is said here,
    where its two arrivals meet, and the first arrival kept. An included list with no names of its own adds none."""
    names: dict[Steps, _Arrival] = {}
    lists: list[str] = []
    for entry in found:
        if isinstance(entry, _Arrival):
            _arrive(name, entry, names, problems)
        elif entry in lists:
            problems.append(f"never.{name}: includes never.{entry} twice")
        elif entry in done:
            twice = [item for item in done[entry].lists if item in lists]
            problems += [f"never.{name}: includes never.{item} twice" for item in twice]
            lists += [item for item in (entry, *done[entry].lists) if item not in twice]
            for arrival in done[entry].names:
                if arrival.holder not in twice:
                    _arrive(name, arrival, names, problems)
    return _Expansion(tuple(names.values()), tuple(lists))


def _arrive(name: str, arrival: _Arrival, names: dict[Steps, _Arrival], problems: list[str]) -> None:
    """The name in the list's names when it is not there yet; else the repeat, said at the list."""
    first = names.get(arrival.steps)
    if first is None:
        names[arrival.steps] = arrival
    elif name in (first.holder, arrival.holder):
        own, other = (first, arrival) if first.holder == name else (arrival, first)
        problems.append(f"never.{name}: {own.text!r} is listed in never.{other.holder}, which never.{name} includes: "
                        "drop it here")
    else:
        problems.append(f"never.{name}: {first.text!r} is listed in never.{first.holder} and in "
                        f"never.{arrival.holder}, which never.{name} includes: drop it from one")
