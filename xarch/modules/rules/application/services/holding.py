from __future__ import annotations

from pathlib import Path

from xarch.modules.rules.application.logic import governed
from xarch.modules.rules.application.logic.asked import project
from xarch.modules.rules.application.logic.elsewhere import broken, reading
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.contract import AskHolds, HoldsAsked, HoldsOf
from xarch.modules.rules.domain.parsed import SourceFile
from xarch.modules.rules.domain.profile import Profile


class HoldingService:
    """Finds, for the module that asks it, where else files given as text could lie by the profile's `holds`: the
    parts whose `holds` each would break were it to lie there."""

    def __init__(self, tree: SourceTree, profiles: Profiles):
        self._tree, self._profiles = tree, profiles

    def holds(self, cmd: AskHolds) -> HoldsAsked:
        """Each file given, read with the files of the app `check` reads at root when it is given, each file given in
        place of the one at its path; raises ChecksRefused for a profile whose own checks cannot run, ProfileUnusable
        for one that cannot be used."""
        profile = self._profiles.profile(cmd.profile)
        given = [(path, self._tree.parsed(text, profile.language.standard_modules, private=profile.language.private,
                                          special=profile.language.special))
                 for path, text in cmd.files]
        others = self._others(profile, cmd.root, {tuple(path.split("/")) for path, _ in cmd.files}) if cmd.root else ()
        found = broken(project(given, profile, cmd.app, reading(profile), others), profile,
                       frozenset(path for path, _ in cmd.files))
        return HoldsAsked(tuple(HoldsOf(path, found.get(path, ())) for path, _ in cmd.files))

    def _others(self, profile: Profile, root: Path, given: set[tuple[str, ...]]) -> tuple[SourceFile, ...]:
        """The files of the app below root that `check` reads, but those at the paths given."""
        paths = [p for p in self._tree.paths(root, profile.language.extensions)
                 if not governed.excluded(profile, p) and governed.governed(profile, p) and p not in given]
        return tuple(self._tree.read(root, paths, immutable=profile.language.immutable,
                                     interface=profile.language.interface, standard=profile.language.standard_modules,
                                     private=profile.language.private, special=profile.language.special))
