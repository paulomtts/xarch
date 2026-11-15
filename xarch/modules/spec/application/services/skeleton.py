from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.ports.settings import Settings
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.contract import Entry, Skeleton
from xarch.modules.spec.domain.skeleton import choose, walk
from xarch.modules.spec.domain.values import Layout


class SkeletonService:
    """The skeleton of an architecture, and which architecture is in force for an app."""

    def __init__(self, settings: Settings, architectures: ArchitectureService,
                 files: ArchitectureFiles):
        self._settings, self._architectures, self._files = settings, architectures, files

    def skeleton(self, location: str) -> Skeleton:
        architecture = self._architectures.load(location)
        entry = architecture.entry
        return Skeleton(top_level=_entries(architecture.top_level_tree()), each_root=architecture.instance_root(),
                        each=_entries(architecture.instance_tree()), entry_point=entry.path[0] if entry is not None else "",
                        each_word=architecture.singular)

    def select(self, app: Path, override: str | None, tests: Path | None = None) -> tuple[str, Path | None]:
        """The location in force, once its architecture loads, and the tests root: the explicit one, else the
        configured one, else None; raises NoProfile, UnknownProfile, UnreadableSettings or InvalidArchitecture."""
        configured = None if override is not None else self._settings.configured_profile(app)
        location = choose(override, configured, self._files.bundled())
        self._architectures.load(location)
        return location, tests if tests is not None else self._settings.configured_tests(app)


def _entries(tree: Layout) -> tuple[Entry, ...]:
    return tuple(Entry(path, is_dir, leaf) for path, is_dir, leaf in walk(tree))
