from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.kernel.source import Import, Unparsable
from xarch.modules.rules.application.logic import explained
from xarch.modules.rules.application.logic.written import written, written_own
from xarch.modules.rules.application.services.app_check import AppCheckService
from xarch.modules.rules.application.services.examples import ExamplesService
from xarch.modules.rules.application.services.explaining import ExplainingService
from xarch.modules.rules.application.services.locate import LocateService
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.application.services.source_reading import SourceReadService
from xarch.modules.rules.contract import (
    CategoryShown,
    CheckApp,
    CheckAppResult,
    CheckExamples,
    CheckImports,
    CheckRefused,
    CheckResult,
    ChecksCannotRun,
    ChecksShown,
    ExamplesChecked,
    ExplainRule,
    ExplainWords,
    FieldShown,
    Locate,
    LocateResult,
    NoRuleShown,
    NotADirectory,
    Outside,
    RuleResult,
    UnknownWords,
    WordLine,
    WordShown,
    WordsResult,
    WordsShown,
)
from xarch.modules.rules.domain.errors import ChecksRefused, OutsideProject, RootMissing, Unreadable
from xarch.modules.rules.domain.vocabulary import READING, SLOTS, Kind
from xarch.modules.rules.domain.worked import WORKED
from xarch.profile_values.language import CheckedLanguage


class RulesController:
    def __init__(self, service: SourceCheckService, locator: LocateService, app: AppCheckService,
                 explaining: ExplainingService, examples: ExamplesService):
        self._service, self._locator, self._app, self._explaining = service, locator, app, explaining
        self._examples = examples

    def check_examples(self, cmd: CheckExamples) -> ExamplesChecked:
        """The profile's own checks held to their examples, and to the vocabulary; every problem at once."""
        problems, count = self._examples.problems(cmd.profile, cmd.app)
        return ExamplesChecked(tuple(problems), count)

    def explain_words(self, cmd: ExplainWords) -> WordsResult:
        """How a check is written, a category of its words or one word, from the vocabulary the engine reads; an
        address of no word comes back with the nearest ones. A word's example is the first rule of the profiles named
        that is written with it, else a check of a profile's own written for the explanation."""
        typed = cmd.address.strip().strip(".")
        language = self._explaining.language(cmd.examples_from)
        if typed == CHECKS:
            categories = tuple(_category(name) for name in explained.CATEGORIES)
            return ChecksShown(READING, SLOTS, categories,
                               WORKED[0].rule.key, "", written_own(WORKED[:1], language))
        if explained.category_at(typed):
            return WordsShown(_category(typed))
        slot = explained.slot_at(typed)
        if slot is not None:
            key, location, example = self._example("quantifiers", slot.name, cmd.examples_from, language)
            if not example:
                key, location, example = WORKED[0].rule.key, "", written_own(WORKED[:1], language)
            return WordShown(typed, CHECKS, slot.name, f"{slot.meaning}: {slot.accepts}", value=slot.takes,
                             example_key=key, example_profile=location, example=example)
        at = explained.word_at(typed)
        if at is None:
            return UnknownWords(typed, explained.nearest(typed))
        category, word = at
        key, location, example = self._example(category, word.name, cmd.examples_from, language)
        kind = word if isinstance(word, Kind) else None
        return WordShown(typed, category, word.name, word.meaning, getattr(word, "about", ""), explained.applies(word),
                         getattr(word, "side", ""), getattr(word, "value", "") or getattr(word, "values", ""),
                         tuple(FieldShown(*f) for f in explained.fields(kind)) if kind else (),
                         explained.needs(kind) if kind else (), kind.verb if kind else "", key, location, example)

    def _example(self, category: str, name: str, locations: tuple[str, ...],
                 language: CheckedLanguage) -> tuple[str, str, str]:
        """The key, the profile ("" for a check written for the explanation) and the text of a word's example."""
        found = self._explaining.example(category, name, locations)
        if found is not None:
            location, rule = found
            return rule.key or rule.id, location, written((rule,), (rule.id,))
        own = next((check for check in WORKED if explained.uses(check.rule, category, name)), None)
        return (own.rule.key, "", written_own((own,), language)) if own is not None else ("", "", "")

    def explain_rule(self, cmd: ExplainRule) -> RuleResult:
        """The rules a key of a profile expands to, written as checks; a key the engine expands that the profile sets
        nowhere comes back as unset, and any other key that expands to none with why."""
        try:
            return self._explaining.rule(cmd.address, cmd.profile)
        except DomainError as e:
            return NoRuleShown(cmd.address, cmd.profile, e.reason)

    def check_app(self, cmd: CheckApp) -> CheckAppResult:
        """The whole check of an app; a root or tests folder that is no folder is refused, and so are a profile whose
        own checks cannot run and one that cannot be used."""
        try:
            return self._app.check(cmd.root, cmd.profile, cmd.tests, cmd.cwd, cmd.strict)
        except RootMissing as e:
            return NotADirectory(e.root)
        except ChecksRefused as e:
            return ChecksCannotRun(e.problems)
        except DomainError as e:
            return CheckRefused(e.reason)

    def check(self, cmd: CheckImports) -> CheckResult:
        """The check of the imports below a root; refused as check_app refuses."""
        try:
            return self._service.imports(cmd.root, cmd.package, cmd.profile, cmd.tests)
        except RootMissing as e:
            return NotADirectory(e.root)
        except ChecksRefused as e:
            return ChecksCannotRun(e.problems)
        except DomainError as e:
            return CheckRefused(e.reason)

    def locate(self, cmd: Locate) -> LocateResult:
        """A path outside the project is refused with why, and so is a profile that cannot be used."""
        try:
            return self._locator.locate(cmd)
        except OutsideProject as e:
            return Outside(e.reason)
        except ChecksRefused as e:
            return ChecksCannotRun(e.problems)
        except DomainError as e:
            return CheckRefused(e.reason)


class ReaderController:
    """Reads source text with the reader of the app's language, for a module that holds source as data, such as spec
    its examples: it answers in kernel values, so that such a module reads through it without importing rules. It
    needs no profile, so it is built before the modules that read profiles."""

    def __init__(self, reading: SourceReadService):
        self._reading = reading

    def imports(self, text: str) -> tuple[Import, ...] | Unparsable:
        """What a text that is in no file imports, in order; one that does not parse comes back as where and why."""
        try:
            return self._reading.imports(text)
        except Unreadable as e:
            return e.found


CHECKS = "checks"
"""The address of how a check is written."""


def _category(name: str) -> CategoryShown:
    return CategoryShown(name, explained.MEANINGS[name],
                         tuple(WordLine(word.name, word.meaning) for word in explained.CATEGORIES[name]))
