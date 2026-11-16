"""Where each file found at a path given to be read sits: the files a folder stands for, and the part, the instance and
the exclusion of each, by the same places `where` and the checks use."""
from __future__ import annotations

from xarch.modules.rules.application.logic.places import excluded_by, file_place
from xarch.modules.rules.domain.values import Profile, Resolved, Sited


def below(folder: Resolved, steps: tuple[str, ...]) -> Resolved:
    """The file at steps below a folder that exists, settled as the folder is."""
    return Resolved(folder.within, folder.steps + steps, folder.path.joinpath(*steps), True,
                    "/".join((folder.shown, *steps)) if folder.shown else "/".join(steps))


def sited(profile: Profile, found: Resolved) -> Sited:
    """Where a file sits: only a file of the app lies in a part or below an excluded folder."""
    source = found.path.name.endswith(profile.language.extension)
    if found.within != "app":
        return Sited("", "", False, source)
    if excluded_by(profile, found.steps) is not None:
        return Sited("", "", True, source)
    where = file_place(profile, found.steps)
    return Sited(where.part or "" if where is not None else "", where.instance or "" if where is not None else "",
                 False, source)


def walked(profile: Profile, folder: Resolved, paths: list[tuple[str, ...]]) -> list[Resolved]:
    """The source files below a folder, each settled, but those below a folder the profile excludes, which no check
    looks at."""
    return [found for found in (below(folder, steps) for steps in paths)
            if found.within != "app" or excluded_by(profile, found.steps) is None]
