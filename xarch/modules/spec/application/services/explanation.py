from __future__ import annotations

from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.domain.profile_keys import CHOICE_BUNDLED, CHOICE_PRESETS, Key


class ExplainService:
    """The names xarch ships that a key of the profile format may be set to."""

    def __init__(self, files: ArchitectureFiles):
        self._files = files

    def choices(self, key: Key) -> tuple[str, ...]:
        """The bundled profiles, or the `testing` presets, for a key that names one of them; else none."""
        if key.choices == CHOICE_BUNDLED:
            return self._files.bundled()
        return tuple(self._files.testing_presets()) if key.choices == CHOICE_PRESETS else ()
