from __future__ import annotations

from pathlib import Path

from app.modules.rules.application.logic.cycles import cycles
from app.modules.rules.application.logic.imports import forbidden_imports, seen_imports
from app.modules.rules.application.ports.profile import Profile
from app.modules.rules.application.ports.source_tree import SourceTree
from app.modules.rules.contract import AppChecked, CycleView


class AppCheckService:
    def __init__(self, profile: Profile, tree: SourceTree):
        self._profile, self._tree = profile, tree

    def check(self, root: Path, location: str) -> AppChecked:
        loaded = self._profile.load(location)
        seen = [one for file in self._tree.files(root, loaded.language.extension)
                for one in seen_imports(file, self._tree.imports(root, file), loaded.patterns, root.name)]
        violations = forbidden_imports(seen, loaded.rules)
        rings = cycles(loaded.wraps)
        return AppChecked(violations, tuple(CycleView(ring) for ring in rings), loaded.name)
