"""Where each file found at a path given to be read lies: the files a folder stands for, and where each lies and its
part, by the same places `where` and the checks use."""
from __future__ import annotations

from xarch.modules.rules.application.logic.places import excluded_by, file_place
from xarch.modules.rules.domain.published import EXCLUDED, IN_NO_PART, IN_PART, IN_PROJECT, IN_TESTS, NOT_SOURCE, NOT_THERE
from xarch.modules.rules.domain.values import Profile, Resolved, Sited


def below(folder: Resolved, steps: tuple[str, ...]) -> Resolved:
    """The file at steps below a folder that exists, settled as the folder is."""
    return Resolved(folder.within, folder.steps + steps, folder.path.joinpath(*steps), True,
                    "/".join((folder.shown, *steps)) if folder.shown else "/".join(steps))


def sited(profile: Profile, found: Resolved) -> Sited:
    """Where a file lies, the first of these that holds: not there, no source file of the app's language, below the
    tests root, in the project outside the app, below a folder the profile excludes, in no part, else in its part."""
    if not found.exists:
        return Sited(NOT_THERE, "")
    if not found.path.name.endswith(profile.language.extension):
        return Sited(NOT_SOURCE, "")
    if found.within != "app":
        return Sited(IN_TESTS if found.within == "tests" else IN_PROJECT, "")
    if excluded_by(profile, found.steps) is not None:
        return Sited(EXCLUDED, "")
    where = file_place(profile, found.steps)
    return Sited(IN_PART, where.part) if where is not None and where.part is not None else Sited(IN_NO_PART, "")


def walked(profile: Profile, folder: Resolved, paths: list[tuple[str, ...]]) -> list[Resolved]:
    """The source files below a folder, each settled, but those below a folder the profile excludes, which no check
    looks at."""
    return [found for found in (below(folder, steps) for steps in paths)
            if found.within != "app" or excluded_by(profile, found.steps) is None]
