"""The profile files a profile is based on when its based_on is a path: each read from the folder of the file that
writes it, and the loop a chain of them may close, which refuses the profile."""
from __future__ import annotations

import posixpath
from collections.abc import Sequence

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import ArchitectureSource

Link = tuple[str, str]
"""(location, based_on): a profile of a chain, where it is as said, and its based_on as written."""


def based_on_a_file(based_on: str) -> bool:
    """Whether a based_on names a profile file rather than a bundled profile; an empty one names neither."""
    return bool(based_on) and ArchitectureSource.names_a_file(based_on)


def resolved(writer: str, based_on: str) -> str:
    """Where a based_on path is read from: joined to the folder of the file that writes it, its `.` and `..` steps
    collapsed as text, no link followed."""
    return posixpath.normpath(posixpath.join(posixpath.dirname(writer), based_on))


def refuse_loop(links: Sequence[Link], target: str) -> None:
    """Raises InvalidArchitecture when target, where the last link's based_on is read from, is a profile of the chain
    already: said from the profile the loop comes back to, with the based_on of each profile between."""
    places = [posixpath.normpath(location) for location, _ in links]
    if target not in places:
        return
    back = places.index(target)
    location, based_on = links[back]
    between = [written for _, written in links[back + 1:-1]]
    through = f", through {', '.join(between)}" if between else ""
    raise InvalidArchitecture(location, [f"based_on: {based_on} is based on this profile{through}"])


def unloaded(based_on: str, problems: Sequence[str]) -> str:
    """A based_on whose file does not load, as said from the file that writes it: the loader's first problem, which
    starts with where that file is, and how many more it found."""
    more = f" (and {len(problems) - 1} more)" if len(problems) > 1 else ""
    return f"based_on: {based_on} does not load: {problems[0]}{more}"
