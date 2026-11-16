from __future__ import annotations

from xarch.modules.spec.application.logic.profile_copy import (
    copied_document,
    copy_file,
    copy_folder,
    project_root,
    recorded,
    valid_name,
)
from xarch.modules.spec.application.logic.profile_file import source_of
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.ports.profile_format import ProfileFormat
from xarch.modules.spec.application.ports.profile_output import ProfileOutput
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.contract import NewProfile, ProfileCreated
from xarch.modules.spec.domain.errors import InvalidArchitecture, NewProfileRefused, UnknownProfile, WouldOverwrite


class ProfileCreationService:
    """Copies a bundled profile into the project as a custom one: its file, named and based on what it was copied
    from, and every file it points to, so the copy loads on its own. It checks the copy loads before writing, and never
    writes over a file."""

    def __init__(self, files: ArchitectureFiles, architectures: ArchitectureService, output: ProfileOutput,
                 form: ProfileFormat):
        self._files, self._architectures, self._output, self._form = files, architectures, output, form

    def create(self, cmd: NewProfile) -> ProfileCreated:
        """Raises NewProfileRefused, WouldOverwrite, UnknownProfile or InvalidArchitecture."""
        if not valid_name(cmd.name):
            raise NewProfileRefused(f"'{cmd.name}' is not a profile name: use letters, digits, '-' and '_', starting "
                                    "with a letter or a digit")
        if cmd.source not in self._files.bundled():
            raise UnknownProfile(cmd.source, self._files.bundled())
        source = source_of(cmd.source, self._files.bundled())
        pointed = self._architectures.pointed(cmd.source)
        text = self._form.renamed(self._files.profile_text(source), cmd.name, cmd.source)
        if text is None:
            raise NewProfileRefused(f"the bundled profile '{cmd.source}' has no `name` line to rename")
        profile = copy_file(cmd.name)
        outputs = {profile: text.encode("utf-8"), **{name: self._files.read_bytes(source, name) for name in pointed}}
        try:
            self._architectures.parse_copy(copied_document(self._files.read(source).document, cmd.name, cmd.source),
                                           profile, outputs)
        except InvalidArchitecture as e:
            raise NewProfileRefused("the copy does not load:\n" + "\n".join(f"  {p}" for p in e.problems)) from e
        root = project_root(cmd.app)
        folder = copy_folder(root, cmd.name, cmd.out)
        taken = self._output.taken(folder, outputs)
        if taken:
            raise WouldOverwrite(taken)
        self._output.write(folder, outputs)
        return ProfileCreated(folder, folder / profile, (profile, *pointed), recorded(folder / profile, root, cmd.cwd))
