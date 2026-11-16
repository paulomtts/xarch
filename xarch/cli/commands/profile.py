"""xarch profile: the commands that work on a profile file itself (spec module)."""
from dataclasses import replace
from pathlib import Path
from typing import Annotated

import typer

from xarch.cli.reports import profile_report as report
from xarch.cli.reports import vocabulary_report as words
from xarch.cli.reports.refusal_report import reason
from xarch.cli.terminal import AppPath, Format, FormatOption, app_for, echo, fail, in_full, refusal
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.contract import (
    CATEGORIES,
    CheckExamples,
    ChecksShown,
    ExplainRule,
    ExplainWords,
    KeyUnset,
    NoRuleShown,
    RuleShown,
    UnknownWords,
    WordShown,
    WordsShown,
)
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import (
    CHECKS,
    CheckProfile,
    Explain,
    FormatExplained,
    KeyExplained,
    Migrated,
    MigrateProfile,
    MigrationRefused,
    NewProfile,
    NoProfileChosen,
    Problem,
    ProfileChecked,
    ProfileCreated,
    ProfileRefused,
    ProfileSelected,
    ProfileViewed,
    SelectProfile,
    UnknownKey,
    ViewProfile,
)


def register(app: typer.Typer, spec: SpecController, rules: RulesController) -> None:
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
                echo(report.migrated_lines(done))
            case MigrationRefused(why):
                raise fail(why)

    @group.command()
    def explain(key: Annotated[str | None, typer.Argument(
                    help="A key of the format, such as parts, parts.may_import, guards.no-duplicates or testing; or "
                         "checks, how a check is written, or a category of its words (kinds, quantifiers, targets, "
                         "filters, variables) or one of them, such as filters.public. Without one, the whole format on "
                         "one screen.")] = None,
                profile: Annotated[str | None, typer.Option(
                    "--profile", help="Show this profile instead of the format: its folder tree and the table of what "
                                      "each part may import. A bundled name or a path. With --rule, the profile whose "
                                      "rules are shown.")] = None,
                configured: Annotated[bool, typer.Option(
                    "--configured", help="Show the profile the project configures under \\[tool.xarch] instead of "
                                         "the format.")] = False,
                rule: Annotated[bool, typer.Option(
                    "--rule", help="Show the rules the key expands to, written as checks a profile could write: in the "
                                   "profile given by --profile, else the one the project configures.")] = False,
                app_path: AppPath = None, output: FormatOption = Format.text) -> None:
        """Explain how to write a profile: with no key, the whole format as a tree of keys, the symbols and the
        smallest valid profile; with a key, what it means, accepts, whether `check` enforces it and through which rule,
        an example that loads, and the keys it holds. `checks` and the categories of words of a check (kinds,
        quantifiers, targets, filters, variables) explain what a check is written in, a word in full with an example
        from a profile's own rules. A key or a word that does not exist is refused with the nearest ones. With --rule,
        the rules a key expands to, written as checks. With --profile or --configured, the folder tree and the import
        table of that profile, for a human to approve."""
        refuse = refusal(output)
        if rule:
            if key is None or configured:
                raise refuse("--rule shows the rules of a key: give a key, such as parts.names, and --profile or a "
                             "configured profile")
            location = profile if profile is not None else _configured(spec, app_for(spec, app_path, refuse), refuse)
            match rules.explain_rule(ExplainRule(key, location)):
                case RuleShown() as shown:
                    _show(output, words.rule_document(shown), words.rule_lines(shown))
                case KeyUnset() as unset:
                    explained = spec.explain(Explain(unset.address))
                    example = explained.example if isinstance(explained, KeyExplained) else ""
                    _show(output, words.unset_document(unset, example), words.unset_lines(unset, example))
                case NoRuleShown() as none:
                    raise refuse(words.no_rule_message(none))
            return
        if key is not None and profile is None and not configured and key.strip(".").split(".")[0] in CATEGORIES:
            _words(rules, spec, key, app_path, output)
            return
        if profile is not None or configured:
            if key is not None or (profile is not None and configured):
                raise refuse("give either a key or a profile (--profile or --configured), not both")
            match spec.view(ViewProfile(in_full(app_for(spec, app_path, refuse)), profile)):
                case ProfileViewed() as seen:
                    _show(output, report.view_document(seen), report.view_lines(seen))
                case NoProfileChosen() | ProfileRefused() as refused:
                    raise refuse(reason(refused))
            return
        match spec.explain(Explain(key)):
            case FormatExplained() as whole:
                _show(output, report.overview_document(whole), report.overview_lines(whole))
            case KeyExplained() as found:
                _show(output, report.key_document(found), report.key_lines(found))
            case UnknownKey() as unknown:
                nearest = _nearest_words(rules, unknown.key)
                if output is Format.json:
                    typer.echo(report.unknown_document(unknown, nearest))
                    raise typer.Exit(2)
                raise fail(report.unknown_message(unknown, nearest))

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
        match spec.new_profile(NewProfile(name, source, root, in_full(Path()), out)):
            case ProfileCreated() as done:
                echo(report.created_lines(done, source))
            case ProfileRefused(why):
                raise fail(why)

    @group.command()
    def check(target: Annotated[str | None, typer.Argument(
                  help="A bundled profile's name, or a path to a profile file. Default: the profile configured under "
                       "\\[tool.xarch] in pyproject.toml.")] = None,
              app_path: AppPath = None, output: FormatOption = Format.text) -> None:
        """Validate a profile without an app: it loads (every problem at once, which includes every file it points to
        existing), its examples import only what their part may, each check of its own is written in words that apply
        and finds something in the code its examples flag and nothing in their clean code, and how it differs from
        the bundled profile it is based on is shown as information. Exit 0 when the profile is valid, 1 when it has
        problems, 2 when no profile can be chosen."""
        refuse = refusal(output)
        app = app_for(spec, app_path, refuse)
        match spec.check_profile(CheckProfile(in_full(app), target)):
            case ProfileChecked() as checked:
                count = 0
                if checked.origin is not None:
                    held = rules.check_examples(CheckExamples(checked.location, app.name))
                    checked, count = replace(checked, problems=(*checked.problems, *(
                        Problem(CHECKS, text) for text in held.problems))), held.checks
                _show(output, report.check_document(checked), report.check_lines(checked, count))
                if not checked.ok:
                    raise typer.Exit(1)
            case NoProfileChosen() | ProfileRefused() as refused:
                raise refuse(reason(refused))


def _show(output: Format, document: str, lines: list[str]) -> None:
    echo([document] if output is Format.json else lines)


def _configured(spec: SpecController, app: Path, refuse) -> str:
    """The profile the project configures; refused when it configures none."""
    match spec.select(SelectProfile(in_full(app), None, None)):
        case ProfileSelected(name, _):
            return name
        case NoProfileChosen() | ProfileRefused() as refused:
            raise refuse(reason(refused))


def _examples_from(spec: SpecController, app_path: Path | None) -> tuple[str, ...]:
    """The profiles whose rules are examples of a word: the one the project configures, if any, then the bundled."""
    match spec.select(SelectProfile(in_full(app_for(spec, app_path)), None, None)):
        case ProfileSelected(name, _):
            return (name, *spec.bundled())
    return spec.bundled()


def _words(rules: RulesController, spec: SpecController, key: str, app_path: Path | None, output: Format) -> None:
    match rules.explain_words(ExplainWords(key, _examples_from(spec, app_path))):
        case ChecksShown() as shown:
            _show(output, words.checks_document(shown), words.checks_lines(shown))
        case WordsShown() as shown:
            _show(output, words.category_document(shown), words.category_lines(shown))
        case WordShown() as shown:
            _show(output, words.word_document(shown), words.word_lines(shown))
        case UnknownWords() as unknown:
            if output is Format.json:
                typer.echo(words.unknown_document(unknown))
                raise typer.Exit(2)
            raise fail(words.unknown_message(unknown))


def _nearest_words(rules: RulesController, typed: str) -> tuple[str, ...]:
    """The words of a check whose names read like a key that does not exist."""
    match rules.explain_words(ExplainWords(typed)):
        case UnknownWords(_, nearest) if set(nearest) != set(CATEGORIES[1:]):
            return nearest
    return ()
