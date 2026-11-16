"""Spec's port for the checks a profile writes itself, filled by rules' controller: spec cannot import rules, whose
adapter already imports spec, so the two are joined here, where everything is wired. It maps rules' Result to spec's
words and decides nothing else."""
from __future__ import annotations

from collections.abc import Callable

from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.contract import CheckExamples, CheckRefused
from xarch.profile_values.checks import ChecksHeld


class RulesOwnChecks:
    """Satisfies spec's OwnChecks port with rules' controller, which bootstrap builds after spec: it is handed a way to
    get it, asked for once spec's check needs it."""

    def __init__(self, rules: Callable[[], RulesController]):
        self._rules = rules

    def held(self, location: str, app: str) -> ChecksHeld:
        match self._rules().check_examples(CheckExamples(location, app)):
            case ChecksHeld() as held:
                return held
            case CheckRefused(reason):
                return ChecksHeld((reason,), 0)
