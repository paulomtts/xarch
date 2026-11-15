"""xarch profile: the commands that work on a profile file itself (spec module)."""
from pathlib import Path
from typing import Annotated

import typer

from xarch.cli.terminal import fail
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import Migrated, MigrateProfile, MigrationRefused

COMMENTS = "YAML comments are not carried over: the converted file has none, so copy the ones you need by hand."


def _migrated(done: Migrated) -> list[str]:
    where = done.folder.as_posix()
    lines = [f"{'dry run, nothing written: would write' if done.dry_run else 'wrote'} to {where}/"]
    for file in done.files:
        notes = []
        if file.source is not None:
            notes.append(f"from {file.source}")
        if file.rewritten:
            notes.append(f"{file.rewritten} example placeholder{'s' if file.rewritten > 1 else ''} rewritten")
        lines.append(f"  {file.path}" + (f"  ({', '.join(notes)})" if notes else ""))
    if done.changes:
        lines += ["changed:", *(f"  {item}" for item in done.changes)]
    if done.by_hand:
        lines += ["by hand:", *(f"  {item}" for item in done.by_hand)]
    lines.append(COMMENTS)
    lines.append("the old profile and its files are untouched; check the new one with `xarch check --profile "
                 f"{done.profile.as_posix()}`")
    return lines


def register(app: typer.Typer, spec: SpecController) -> None:
    group = typer.Typer(help="Work on a profile file: convert one from format 1.", no_args_is_help=True)
    app.add_typer(group, name="profile")

    @group.command()
    def migrate(path: Annotated[Path, typer.Argument(help="A profile file in format 1 (`xarch: 1`).")],
                out: Annotated[Path | None, typer.Option(
                    "--out", help="The folder to write to; no file in it may exist already. Default: a folder beside "
                                  "the file, named for it with -v2. The old profile is never changed.")] = None,
                dry_run: Annotated[bool, typer.Option(
                    "--dry-run", help="Report what would be written, and write nothing.")] = False) -> None:
        """Convert a profile of format 1 to format 2, in a new folder: the converted profile, and every file it names,
        copied to where format 2 reads it (an example file goes to the path it illustrates, and the templates quote it
        by that path). The result is validated before it is written, and nothing is ever overwritten. What cannot be
        converted is listed with what to write by hand."""
        match spec.migrate(MigrateProfile(path, out, dry_run)):
            case Migrated() as done:
                for line in _migrated(done):
                    typer.echo(line)
            case MigrationRefused(reason):
                raise fail(reason)
