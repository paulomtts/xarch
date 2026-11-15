from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.logic.profile_copy import copied_text, recorded, valid_name
from xarch.modules.spec.application.logic.profile_file import parse_profile, source_of
from xarch.modules.spec.application.logic.profile_files import listing_in, pointed_files
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.ports.profile_output import ProfileOutput
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.profile_writer import ProfileWriter
from xarch.modules.spec.contract import NewProfile, ProfileCreated
from xarch.modules.spec.domain.errors import InvalidArchitecture, NewProfileRefused, UnknownProfile
from xarch.modules.spec.domain.values import ArchitectureSource

DEFAULT_FOLDER = "architecture"
"""Where a new profile goes by default, below the folder holding the app folder: in a folder of its own, named for it."""
SUFFIX = ".yaml"


class ProfileCreation:
    """Copies a bundled profile into the project as a custom one: its file, named and based on what it was copied
    from, and every file it points to, so the copy loads on its own. It checks the copy loads before writing, and never
    writes over a file."""

    def __init__(self, files: ArchitectureFiles, architectures: ArchitectureService, output: ProfileOutput):
        self._files, self._architectures, self._writer = files, architectures, ProfileWriter(output)

    def create(self, cmd: NewProfile) -> ProfileCreated:
        """Raises NewProfileRefused, UnknownProfile or InvalidArchitecture."""
        if not valid_name(cmd.name):
            raise NewProfileRefused(f"'{cmd.name}' is not a profile name: use letters, digits, '-' and '_', starting "
                                    "with a letter or a digit")
        if cmd.source not in self._files.bundled():
            raise UnknownProfile(cmd.source, self._files.bundled())
        source = source_of(cmd.source, self._files.bundled())
        architecture = self._architectures.load(cmd.source)
        text = copied_text(self._files.read_text(source, f"{cmd.source}{SUFFIX}"), cmd.name, cmd.source)
        if text is None:
            raise NewProfileRefused(f"the bundled profile '{cmd.source}' has no `name` line to rename")
        pointed = pointed_files(architecture, lambda folder: self._files.files_under(source, folder))
        profile = f"{cmd.name}{SUFFIX}"
        outputs = {profile: text.encode("utf-8"), **{name: self._files.read_bytes(source, name) for name in pointed}}
        self._validate(cmd, source, outputs)
        folder = cmd.out if cmd.out is not None else cmd.root / DEFAULT_FOLDER / cmd.name
        taken = self._writer.taken(folder, outputs)
        if taken:
            raise NewProfileRefused(f"{taken}: nothing was written; `new` writes only new files, so pass "
                                    "`--out <folder>` to write somewhere else, or choose another name")
        self._writer.write(folder, outputs)
        return ProfileCreated(folder, folder / profile, tuple(outputs), recorded(folder / profile, cmd.root, Path.cwd()))

    def _validate(self, cmd: NewProfile, source: ArchitectureSource, outputs: dict[str, bytes]) -> None:
        document = self._files.read(source).document
        copy = {**document, "name": cmd.name, "based_on": cmd.source}
        try:
            parse_profile(copy, f"{cmd.name}{SUFFIX}", lambda relative: relative in outputs,
                          lambda relative: listing_in(outputs, relative), self._files.testing_presets(),
                          self._files.bundled())
        except InvalidArchitecture as e:
            raise NewProfileRefused("the copy does not load:\n" + "\n".join(f"  {p}" for p in e.problems)) from e
