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
from xarch.modules.rules.domain.rule import Rule
from xarch.modules.rules.domain.vocabulary import READING, SLOTS, Kind
from xarch.modules.rules.domain.worked import WORKED
from xarch.profile_values.language import CheckedLanguage


class ExplainingService:
    """What `profile explain` shows of how a check is written: the words of the vocabulary, each with an example (the
    first rule of the profiles given that is written with it, else a check of a profile's own written for the
    explanation), and the rules a key of a profile expands to, written as checks."""

    def __init__(self, profiles: Profiles, form: CheckFormat):
        self._profiles, self._form = profiles, form

    def words(self, address: str, app: Path | None) -> WordsResult:
        """How a check is written, a category of its words or one word, from the vocabulary the engine reads, each
        example drawn from the profiles the project holding app knows (none for no app); an address of no word comes
        back with the nearest ones."""
        typed = address.strip().strip(".")
        if not explained.names_words(typed):
            return NoWords(typed, explained.close(typed))
        examples_from = self._profiles.known(app) if app is not None else ()
        language = self.language(examples_from)
        if typed == CHECKS:
            categories = tuple(_category(name) for name in explained.CATEGORIES)
            return ChecksShown(READING, SLOTS, categories, WORKED[0].rule.key, "",
                               self._form.written(written_own(WORKED[:1], language)))
        if explained.category_at(typed):
            return WordsShown(_category(typed))
        slot = explained.slot_at(typed)
        if slot is not None:
            key, location, example = self._example("quantifiers", slot.name, examples_from, language)
            if not example:
                key, location, example = WORKED[0].rule.key, "", self._form.written(written_own(WORKED[:1], language))
            return WordShown(typed, CHECKS, slot.name, f"{slot.meaning}: {slot.accepts}", value=slot.takes,
                             example_key=key, example_profile=location, example=example)
        at = explained.word_at(typed)
        if at is None:
            return UnknownWords(typed, explained.nearest(typed))
        category, word = at
        key, location, example = self._example(category, word.name, examples_from, language)
        kind = word if isinstance(word, Kind) else None
        return WordShown(typed, category, word.name, word.meaning, getattr(word, "about", ""), explained.applies(word),
                         getattr(word, "side", ""), getattr(word, "value", "") or getattr(word, "values", ""),
                         tuple(FieldShown(*f) for f in explained.fields(kind)) if kind else (),
                         explained.needs(kind) if kind else (), kind.verb if kind else "", key, location, example,
                         explained.about(word))

    def _example(self, category: str, name: str, locations: tuple[str, ...],
                 language: CheckedLanguage) -> tuple[str, str, str]:
        """The key, the profile ("" for a check written for the explanation) and the text of a word's example."""
        found = self.example(category, name, locations)
        if found is not None:
            location, rule = found
            return rule.key or rule.id, location, self._form.written({rule.id: check_of(rule)})
        own = next((check for check in WORKED if explained.uses(check.rule, category, name)), None)
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
            return NoRuleShown(address, location, "it expands to no rule of the engine here: the profile does not set "
                                                  "it, or it is checked by a check of its own")
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
