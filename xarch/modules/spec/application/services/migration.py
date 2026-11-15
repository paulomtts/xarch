from __future__ import annotations

from xarch.modules.spec.application.logic.migrate_examples import referenced_v1, rewritten_template
from xarch.modules.spec.application.logic.migrate_output import converted_folder, converted_name, not_format_1
from xarch.modules.spec.application.logic.migrate_profile import Converted, convert
from xarch.modules.spec.application.logic.profile_listing import listing
from xarch.modules.spec.application.logic.taken_paths import taken_phrase
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.ports.profile_format import ProfileFormat
from xarch.modules.spec.application.ports.profile_output import ProfileOutput
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.contract import MigrateProfile
from xarch.modules.spec.domain.errors import InvalidArchitecture, UnmigratableProfile
from xarch.modules.spec.domain.migration import Conversion
from xarch.modules.spec.domain.values import ArchitectureSource


class MigrationService:
    """Converts a profile of format 1 to format 2 in a new folder: the profile, and the files it names, copied to where
    format 2 reads them. Validates the result with the loader of format 2 before writing, and never writes over a file."""

    def __init__(self, files: ArchitectureFiles, architectures: ArchitectureService, output: ProfileOutput,
                 form: ProfileFormat):
        self._files, self._architectures, self._output, self._form = files, architectures, output, form

    def migrate(self, cmd: MigrateProfile) -> Conversion:
        """Raises UnmigratableProfile, or InvalidArchitecture when the file cannot be read."""
        location = str(cmd.path)
        source = ArchitectureSource(location, bundled=False)
        raw = self._files.read(source)
        refusal = not_format_1(raw.document, location)
        if refusal is not None:
            raise UnmigratableProfile(refusal)
        named, folders = referenced_v1(raw.document)
        files = listing((name for name in named if self._files.has_file(source, name)),
                        {folder: self._files.files_under(source, folder) for folder in folders})
        converted = convert(raw.document, location, self._files.testing_presets(), files)
        name = converted_name(cmd.path)
        contents, rewritten, by_hand = self._contents(source, converted)
        by_hand = (*converted.by_hand, *by_hand)
        outputs = {name: self._form.written(converted.document), **contents}
        try:
            self._architectures.parse_copy(converted.document, location, outputs)
        except InvalidArchitecture as e:
            lines = ["the converted profile does not load:", *(f"  {problem}" for problem in e.problems)]
            if by_hand:
                lines += ["not converted:", *(f"  {item}" for item in by_hand)]
            raise UnmigratableProfile("\n".join(lines)) from e
        folder = converted_folder(cmd.path, cmd.out)
        taken = taken_phrase(self._output.taken(folder, outputs))
        if taken:
            raise UnmigratableProfile(f"{taken}: migrate writes only new files; pass `--out <folder>` to write somewhere "
                                      "else")
        if not cmd.dry_run:
            self._output.write(folder, outputs)
        shown = ((name, None, 0), *((c.destination, c.source, rewritten.get(c.destination, 0)) for c in converted.copies))
        return Conversion(folder, folder / name, shown, converted.changes, by_hand, cmd.dry_run)

    def _contents(self, source: ArchitectureSource, converted: Converted) -> tuple[dict[str, bytes], dict[str, int],
                                                                                      list[str]]:
        contents: dict[str, bytes] = {}
        rewritten: dict[str, int] = {}
        by_hand: list[str] = []
        for copy in converted.copies:
            if not copy.rewritten:
                contents[copy.destination] = self._files.read_bytes(source, copy.source)
                continue
            text, count, left = rewritten_template(copy.destination, self._files.read_text(source, copy.source),
                                                   converted.names)
            contents[copy.destination] = text.encode("utf-8")
            rewritten[copy.destination] = count
            by_hand += left
        return contents, rewritten, by_hand
