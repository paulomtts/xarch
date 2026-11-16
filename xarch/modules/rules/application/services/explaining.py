from __future__ import annotations

from pathlib import Path

from xarch.kernel.errors import DomainError
from xarch.modules.rules.application.logic import expansion, explained
from xarch.modules.rules.application.logic.expandable import expands
from xarch.modules.rules.application.logic.explained import keyed, uses
from xarch.modules.rules.application.logic.own_checks import resolved
from xarch.modules.rules.application.logic.written import check_of, written, written_own
from xarch.modules.rules.application.ports.check_format import CheckFormat
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.contract import (
    CategoryShown,
    ChecksShown,
    FieldShown,
    KeyUnset,
    NoRuleShown,
    NoWords,
    RuleShown,
    UnknownWords,
    WordLine,
    WordShown,
    WordsResult,
    WordsShown,
)
from xarch.modules.rules.domain.published import CHECKS
from xarch.modules.rules.domain.rule import OwnCheck, Rule
from xarch.modules.rules.domain.vocabulary import READING, SLOTS
from xarch.profile_values.language import CheckedLanguage


class ExplainingService:
    """What `profile explain` shows of how a check is written: the words of the vocabulary, each with an example (the
    first rule of the profiles given that is written with it, else a check of a profile's own written for the
    explanation), and the rules a key of a profile expands to, written as checks."""

    def __init__(self, profiles: Profiles, form: CheckFormat):
        self._profiles, self._form = profiles, form

    def words(self, address: str, app: Path | None) -> WordsResult:
        """How a check is written, a category of its words or one word, from the vocabulary the engine reads, each
        example drawn from the profiles the project holding app knows, the one in force first (none for no app); an
        address of no word comes back with the nearest ones. Raises ProfileUnusable when the profile configured for
        the project cannot be chosen or loaded."""
        typed = address.strip().strip(".")
        if not explained.names_words(typed):
            return NoWords(typed, explained.close(typed))
        examples_from = explained.searched(self._profiles.known(app)) if app is not None else ()
        language = self.language(examples_from)
        if typed == CHECKS:
            categories = tuple(_category(name) for name in explained.CATEGORIES)
            key, location, example = self._example("", "", (), language, explained.fallback(CHECKS, CHECKS))
            return ChecksShown(READING, SLOTS, categories, key, location, example)
        if explained.category_at(typed):
            return WordsShown(_category(typed))
        slot = explained.slot_at(typed)
        if slot is not None:
            key, location, example = self._example("quantifiers", slot.name, examples_from, language,
                                                   explained.fallback(CHECKS, slot.name))
            return WordShown(typed, CHECKS, slot.name, f"{slot.meaning}: {slot.accepts}", value=slot.takes,
                             example_key=key, example_profile=location, example=example)
        at = explained.word_at(typed)
        if at is None:
            return UnknownWords(typed, explained.nearest(typed))
        category, word = at
        key, location, example = self._example(category, word.name, examples_from, language,
                                               explained.fallback(category, word.name))
        facets = explained.facets(word)
        return WordShown(typed, category, word.name, word.meaning, facets.about, explained.applies(word), facets.side,
                         facets.value, tuple(FieldShown(*f) for f in facets.fields), facets.needs, facets.verb, key,
                         location, example, explained.about(word))

    def _example(self, category: str, name: str, locations: tuple[str, ...], language: CheckedLanguage,
                 own: OwnCheck | None) -> tuple[str, str, str]:
        """The key, the profile ("" for a check written for the explanation, own) and the text of a word's example."""
        found = self.example(category, name, locations)
        if found is not None:
            location, rule = found
            return rule.key or rule.id, location, self._form.written({rule.id: check_of(rule)})
        return (own.rule.key, "", self._form.written(written_own((own,), language))) if own is not None else ("", "", "")

    def example(self, category: str, name: str, locations: tuple[str, ...]) -> tuple[str, Rule] | None:
        """The first rule of the first profile that uses the word, with that profile; a profile that cannot be read
        is passed over."""
        for location in locations:
            for rule in self._rules(location):
                if uses(rule, category, name):
                    return location, rule
        return None

    def language(self, locations: tuple[str, ...]) -> CheckedLanguage:
        """The language of the first of the profiles that can be read; none when none can."""
        for location in locations:
            try:
                return resolved(self._profiles.profile(location)).language
            except DomainError:
                continue
        return CheckedLanguage()

    def rules_of(self, address: str, location: str) -> list[Rule]:
        """The rules of the profile at location that the key at address expands to; raises DomainError when the
        profile cannot be read."""
        profile = resolved(self._profiles.profile(location))
        return keyed([*(rule for rules in expansion.book(profile).values() for rule in rules),
                      *(check.rule for check in profile.checks)], address)

    def rule(self, address: str, location: str) -> RuleShown | KeyUnset | NoRuleShown:
        """The rules the key at address of the profile at location expands to, written as checks; a key the engine
        expands that the profile sets nowhere is unset, and any other key that expands to none says why; raises
        DomainError when the profile cannot be read."""
        rules = self.rules_of(address, location)
        if not rules and expands(address):
            return KeyUnset(address, location, self._profiles.key(address))
        if not rules:
            return NoRuleShown(address, location, explained.NO_RULE)
        return RuleShown(address, location, self._form.written(written(rules)), len(rules),
                         tuple(dict.fromkeys(need for rule in rules for need in rule.needs)))

    def _rules(self, location: str) -> list[Rule]:
        try:
            profile = resolved(self._profiles.profile(location))
        except DomainError:
            return []
        return [rule for rules in expansion.book(profile).values() for rule in rules]



def _category(name: str) -> CategoryShown:
    return CategoryShown(name, explained.MEANINGS[name],
                         tuple(WordLine(word.name, word.meaning) for word in explained.CATEGORIES[name]))
