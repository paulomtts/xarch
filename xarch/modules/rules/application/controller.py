from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.kernel.source import Import, Unparsable
from xarch.modules.rules.application.services.app_check import AppCheckService
from xarch.modules.rules.application.services.examples import ExamplesService
from xarch.modules.rules.application.services.explaining import ExplainingService
from xarch.modules.rules.application.services.locate import LocateService
from xarch.modules.rules.application.services.source_check import SourceCheckService
from xarch.modules.rules.application.services.source_reading import SourceReadService
from xarch.modules.rules.contract import (
    CheckApp,
    CheckAppResult,
    CheckImports,
    CheckProfile,
    CheckRefused,
    CheckResult,
    ChecksCannotRun,
    ExplainRule,
    ExplainWords,
    Locate,
    LocateResult,
    NoProfileChosen,
    NoRuleShown,
    NotADirectory,
    Outside,
    ProfileCheckResult,
    ProfileUnloaded,
    RuleResult,
    WordsResult,
)
from xarch.modules.rules.domain.errors import ChecksRefused, NoProfile, OutsideProject, RootMissing, Unloaded, Unreadable


class RulesController:
    def __init__(self, service: SourceCheckService, locator: LocateService, app: AppCheckService,
                 explaining: ExplainingService, examples: ExamplesService):
        self._service, self._locator, self._app, self._explaining = service, locator, app, explaining
        self._examples = examples

    def check_profile(self, cmd: CheckProfile) -> ProfileCheckResult:
        """Validates a profile without an app: every problem at once, what spec's check of it finds and what its own
        checks find against their examples and the vocabulary, with how it differs from the bundled one it is based
        on. One that does not load comes back with the loader's problems, none chosen with the profiles known, and
        one that cannot be used is refused with why."""
        try:
            return self._examples.check(cmd.app, cmd.target)
        except Unloaded as e:
            return ProfileUnloaded(e.location, e.problems)
        except NoProfile as e:
            return NoProfileChosen(e.known)
        except DomainError as e:
            return CheckRefused(e.reason)

    def explain_words(self, cmd: ExplainWords) -> WordsResult:
        """How a check is written, a category of its words or one word, from the vocabulary the engine reads; an
        address of no word comes back with the nearest ones. A word's example is the first rule of the profiles the
        project knows that is written with it, else a check of a profile's own written for the explanation. A project
        whose profile cannot be chosen or loaded is refused with why."""
        try:
            return self._explaining.words(cmd.address, cmd.app)
        except DomainError as e:
            return CheckRefused(e.reason)

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

