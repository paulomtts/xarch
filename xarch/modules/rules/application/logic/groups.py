"""The files a rule counts together, by what it counts them per: each file alone (file); the files of each part
(part), a test's part the parts its folder mirrors; the files of each instance of a repeating folder (instance), a
file in no instance with the files of its part in none; or every file of its scope (all). A file in no part is a
group of its own under part and instance."""
from __future__ import annotations

from collections.abc import Hashable

from xarch.kernel.logic.placement import root_of
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.rule import Read
from xarch.profile_values.checks import PER_ALL, PER_FILE, PER_PART


def group(per: str, read: Read, profile: Profile) -> Hashable:
    """What the file is counted with under per: the files of the same group have the same key."""
    if per == PER_ALL:
        return ()
    alone = ("file", read.in_tests, read.file.path)
    if per == PER_FILE:
        return alone
    parts = read.mirrors if read.in_tests else (read.place.part,) if read.place is not None else ()
    parts = tuple(part for part in parts if part is not None)
    if not parts:
        return alone
    instance = read.instance if read.in_tests else read.place.instance if read.place is not None else None
    if per == PER_PART or instance is None:
        return ("part", parts)
    folder = root_of(profile.parts.get(parts[0], ()))
    return ("instance", folder, instance)
