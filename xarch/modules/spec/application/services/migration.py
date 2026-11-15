from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.application.logic.migrate_examples import PLACEHOLDER, referenced_v1, rewrite_examples
from xarch.modules.spec.application.logic.migrate_profile import Converted, convert
from xarch.modules.spec.application.logic.profile_file import parse_profile
from xarch.modules.spec.application.logic.profile_listing import listing
from xarch.modules.spec.application.logic.yaml_text import dump
from xarch.modules.spec.application.ports.architecture_files import ArchitectureFiles
from xarch.modules.spec.application.ports.profile_output import ProfileOutput
from xarch.modules.spec.application.services.profile_writer import ProfileWriter
from xarch.modules.spec.contract import Migrated, MigratedFile, MigrateProfile
from xarch.modules.spec.domain.errors import InvalidArchitecture, UnmigratableProfile
from xarch.modules.spec.domain.values import ArchitectureSource

SUFFIX = "-v2"
"""What the folder of a conversion made without `--out` adds to the name of the file."""


class MigrationService:
    """Converts a profile of format 1 to format 2 in a new folder: the profile, and the files it names, copied to where
    format 2 reads them. Validates the result with the loader of format 2 before writing, and never writes over a file."""

    def __init__(self, files: ArchitectureFiles, output: ProfileOutput):
        self._files, self._writer = files, ProfileWriter(output)

    def migrate(self, cmd: MigrateProfile) -> Migrated:
        """Raises UnmigratableProfile, or InvalidArchitecture when the file cannot be read."""
        location = str(cmd.path)
        source = ArchitectureSource(location, bundled=False)
        raw = self._files.read(source)
        self._version(raw.document, location)
        named, folders = referenced_v1(raw.document)
        files = listing((name for name in named if self._files.has_file(source, name)),
                        {folder: self._files.files_under(source, folder) for folder in folders})
        converted = convert(raw.document, location, self._files.testing_presets(), files)
        name = f"{cmd.path.stem}.yaml"
        contents, rewritten, by_hand = self._contents(source, converted)
        by_hand = (*converted.by_hand, *by_hand)
        text = dump(converted.document)
        outputs = {name: text.encode("utf-8"), **contents}
        self._validate(converted, location, outputs, by_hand)
        folder = cmd.out if cmd.out is not None else cmd.path.parent / f"{cmd.path.stem}{SUFFIX}"
        self._refuse_overwriting(folder, outputs)
        if not cmd.dry_run:
            self._writer.write(folder, outputs)
        shown = (MigratedFile(name, None, 0),
                 *(MigratedFile(c.destination, c.source, rewritten.get(c.destination, 0)) for c in converted.copies))
        return Migrated(folder, folder / name, shown, converted.changes, by_hand, cmd.dry_run)

    def _version(self, document: object, location: str) -> None:
        version = document.get("xarch") if isinstance(document, dict) else None
        if version == 1 and type(version) is int:
            return
        if version == 2 and type(version) is int:
            raise UnmigratableProfile(f"{location}: already in format 2: nothing to migrate")
        said = f"it says `xarch: {version}`" if isinstance(document, dict) and "xarch" in document else "it has no `xarch`"
        raise UnmigratableProfile(f"{location}: not a profile of format 1: {said}")

    def _contents(self, source: ArchitectureSource, converted: Converted) -> tuple[dict[str, bytes], dict[str, int],
                                                                                      list[str]]:
        names = converted.names
        contents: dict[str, bytes] = {}
        rewritten: dict[str, int] = {}
        by_hand: list[str] = []
        for copy in converted.copies:
            if not copy.rewritten:
                contents[copy.destination] = self._files.read_bytes(source, copy.source)
                continue
            text, unknown = rewrite_examples(self._files.read_text(source, copy.source), names)
            contents[copy.destination] = text.encode("utf-8")
            rewritten[copy.destination] = len(PLACEHOLDER.findall(text)) - len(unknown)
            by_hand += [f"{copy.destination}: {{{{example:{name}}}}} names no example: left as written, write the path of "
                        "the example" for name in unknown]
        return contents, rewritten, by_hand

    def _validate(self, converted: Converted, location: str, outputs: dict[str, bytes], by_hand: tuple[str, ...]) -> None:
        try:
            parse_profile(converted.document, location, tuple(outputs), self._files.testing_presets(),
                          self._files.bundled())
        except InvalidArchitecture as e:
            lines = ["the converted profile does not load:", *(f"  {problem}" for problem in e.problems)]
            if by_hand:
                lines += ["not converted:", *(f"  {item}" for item in by_hand)]
            raise UnmigratableProfile("\n".join(lines)) from e

    def _refuse_overwriting(self, folder: Path, outputs: dict[str, bytes]) -> None:
        taken = self._writer.taken(folder, outputs)
        if taken:
            raise UnmigratableProfile(f"{taken}: migrate writes only new files; pass `--out <folder>` to write somewhere "
                                      "else")
