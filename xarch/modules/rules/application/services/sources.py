from __future__ import annotations

from pathlib import Path

from xarch.modules.rules.application.logic.own_checks import resolved
from xarch.modules.rules.application.logic.sources import linked, sited, walked
from xarch.modules.rules.application.logic.where import candidates, resolve
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.contract import IN_PART, LINKED_OUT, ReadSources, SourceRead, SourcesRead
from xarch.modules.rules.domain.errors import OutsideProject, RootMissing
from xarch.modules.rules.domain.values import Profile, Resolved


class SourcesService:
    """Reads the app's source files at the paths given, with where the profile places each, for a module that reads the
    app's code as text."""

    def __init__(self, tree: SourceTree, profiles: Profiles):
        self._tree, self._profiles = tree, profiles

    def sources(self, cmd: ReadSources) -> SourcesRead:
        """The files at the paths, a folder standing for the source files below it, each once; raises RootMissing, with
        the folder as given, when the app folder is no folder, and OutsideProject for a path outside the project."""
        app = self._tree.resolved(cmd.cwd, cmd.app)
        if self._tree.absent([app]):
            raise RootMissing(cmd.app)
        tests = self._tree.resolved(cmd.cwd, cmd.tests) if cmd.tests is not None else None
        profile = resolved(self._profiles.profile(cmd.profile))
        found: dict[str, SourceRead] = {}
        for path in cmd.paths:
            where = resolve(path, cmd.cwd, app, tests, self._tree.existing(candidates(path, cmd.cwd, app)))
            if where is None:
                raise OutsideProject(path, app.parent)
            for file in self._files(profile, where):
                found.setdefault(file.shown, self._read(profile, file, app))
        return SourcesRead(tuple(found.values()))

    def _files(self, profile: Profile, where: Resolved) -> list[Resolved]:
        if not where.exists or self._tree.absent([where.path]):
            return [where]
        return walked(profile, where, self._tree.paths(where.path, profile.language.extension))

    def _read(self, profile: Profile, found: Resolved, app: Path) -> SourceRead:
        place = sited(profile, found)
        if place.lies != IN_PART:
            return SourceRead(found.shown, place.lies, place.part)
        target = linked(profile, found, self._tree.resolved(app, found.path), app)
        if target is None:
            return SourceRead(found.shown, LINKED_OUT)
        read = self._tree.read(app, [found.steps])[0]
        unreadable = read.error is not None and read.error.unreadable
        text = "" if unreadable else self._tree.text(found.path) or ""
        return SourceRead(found.shown, place.lies, place.part, text, read.imports, read.error, read.pieces,
                          target, tuple(comment.span for comment in read.comments))
