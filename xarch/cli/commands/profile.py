"""xarch profile: the commands that work on a profile file itself (spec module)."""
from pathlib import Path
from typing import Annotated

import typer

from xarch.cli import profile_report as report
from xarch.cli.commands.check import Format, FormatOption, _json_refusal
from xarch.cli.terminal import AppPath, app_for, fail
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import (
    CheckProfile,
    Explain,
    FormatExplained,
    KeyExplained,
    Migrated,
    MigrateProfile,
    MigrationRefused,
    NewProfile,
    ProfileChecked,
    ProfileCreated,
    ProfileRefused,
    ProfileViewed,
    UnknownKey,
    ViewProfile,
)

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
    group = typer.Typer(help="Work on a profile file: explain the format, copy a bundled profile, check one, convert one from "
                                "format 1.", no_args_is_help=True)
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

    @group.command()
    def explain(key: Annotated[str | None, typer.Argument(
                    help="A key of the format, such as parts, parts.may_import, guards.no-duplicates or testing. "
                         "Without one, the whole format on one screen.")] = None,
                profile: Annotated[str | None, typer.Option(
                    "--profile", help="Show this profile instead of the format: its folder tree and the table of what "
                                      "each part may import. A bundled name or a path.")] = None,
                configured: Annotated[bool, typer.Option(
                    "--configured", help="Show the profile the project configures under \\[tool.xarch] instead of "
                                         "the format.")] = False,
                app_path: AppPath = None, output: FormatOption = Format.text) -> None:
        """Explain how to write a profile: with no key, the whole format as a tree of keys, the symbols and the
        smallest valid profile; with a key, what it means, accepts, whether `check` enforces it and through which rule,
        an example that loads, and the keys it holds. A key that does not exist is refused with the nearest ones. With
        --profile or --configured, the folder tree and the import table of that profile, for a human to approve."""
        refuse = _json_refusal if output is Format.json else fail
        if profile is not None or configured:
            if key is not None or (profile is not None and configured):
                raise refuse("give either a key or a profile (--profile or --configured), not both")
            match spec.view(ViewProfile(app_for(spec, app_path, refuse), profile)):
                case ProfileViewed() as seen:
                    _show(output, report.view_document(seen), report.view_lines(seen))
                case ProfileRefused(reason):
                    raise refuse(reason)
            return
        match spec.explain(Explain(key)):
            case FormatExplained() as whole:
                _show(output, report.overview_document(whole), report.overview_lines(whole))
            case KeyExplained() as found:
                _show(output, report.key_document(found), report.key_lines(found))
            case UnknownKey() as unknown:
                if output is Format.json:
                    typer.echo(report.unknown_document(unknown))
                    raise typer.Exit(2)
                raise fail(report.unknown_message(unknown))

    @group.command()
    def new(name: Annotated[str, typer.Argument(help="What the new profile is called: letters, digits, - and _.")],
            source: Annotated[str, typer.Option("--from", help="The bundled profile to copy.")],
            out: Annotated[Path | None, typer.Option(
                "--out", help="The folder to write to; no file in it may exist already. Default: "
                              "architecture/<name>/ beside the app folder.")] = None,
            app_path: AppPath = None) -> None:
        """Copy a bundled profile into the project as a custom one: its yaml, named <name> and based_on the bundled
        profile, and every file it points to (templates, docs pages, files, example folders), so the copy loads on its
        own and passes `xarch profile check` as it is. Nothing is overwritten: when any file exists nothing is written
        and the ones that exist are named. pyproject.toml is not edited: the line to put the copy in force is printed."""
        root = app_for(spec, app_path).parent
        match spec.new_profile(NewProfile(name, source, root, out)):
            case ProfileCreated() as done:
                for line in report.created_lines(done, source):
                    typer.echo(line)
            case ProfileRefused(reason):
                raise fail(reason)

    @group.command()
    def check(target: Annotated[str | None, typer.Argument(
                  help="A bundled profile's name, or a path to a profile file. Default: the profile configured under "
                       "\\[tool.xarch] in pyproject.toml.")] = None,
              app_path: AppPath = None, output: FormatOption = Format.text) -> None:
        """Validate a profile without an app: it loads (every problem at once, which includes every file it points to
        existing), its examples import only what their part may, and how it differs from the bundled profile it is
        based on is shown as information. Exit 0 when the profile is valid, 1 when it has problems, 2 when no profile
        can be chosen."""
        refuse = _json_refusal if output is Format.json else fail
        match spec.check_profile(CheckProfile(app_for(spec, app_path, refuse), target)):
            case ProfileChecked() as checked:
                _show(output, report.check_document(checked), report.check_lines(checked))
                if not checked.ok:
                    raise typer.Exit(1)
            case ProfileRefused(reason):
                raise refuse(reason)


def _show(output: Format, document: str, lines: list[str]) -> None:
    for line in [document] if output is Format.json else lines:
        typer.echo(line)
