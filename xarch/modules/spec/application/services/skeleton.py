from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.ports.settings import Settings
from xarch.modules.spec.contract import DocFile, Docs, Entry, Skeleton
from xarch.modules.spec.domain.docs import DOCS_ROOT, doc_files
from xarch.modules.spec.domain.skeleton import (DEFAULT_PROFILE, MODULE_TREE, PROFILES, Tree, choose, profile,
                                                 top_level_tree, walk)


class SkeletonService:
    def __init__(self, settings: Settings):
        self._settings = settings

    def skeleton(self, name: str = DEFAULT_PROFILE) -> Skeleton:
        return Skeleton(top_level=_entries(top_level_tree(name)), module=_entries(MODULE_TREE),
                        entry_point=profile(name).entry_point)

    def docs(self, name: str = DEFAULT_PROFILE) -> Docs:
        return Docs(root=DOCS_ROOT, files=tuple(DocFile(path, text) for path, text in doc_files(profile(name))))

    def profiles(self) -> tuple[str, ...]:
        return tuple(PROFILES)

    def select(self, app: Path, override: str | None) -> str:
        configured = None if override is not None else self._settings.configured_profile(app)   # load
        return choose(override, configured)                                                      # decide


def _entries(tree: Tree) -> tuple[Entry, ...]:
    return tuple(Entry(path, is_dir, leaf) for path, is_dir, leaf in walk(tree))
