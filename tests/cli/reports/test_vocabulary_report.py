"""How `xarch profile explain` shows the words a check is written in, on hand-made results: how a check reads, a
category, a word with its example, the rules of a key, and a word that does not exist, in text and in JSON."""
import json

from xarch.cli.reports.vocabulary_report import (
    category_document,
    category_lines,
    checks_document,
    checks_lines,
    no_rule_message,
    rule_document,
    rule_lines,
    unknown_document,
    unknown_message,
    unset_document,
    unset_lines,
    word_document,
    word_lines,
)
from xarch.modules.rules.contract import (
    CategoryShown,
    ChecksShown,
    FieldShown,
    KeyFacts,
    KeyUnset,
    NoRuleShown,
    RuleShown,
    Slot,
    UnknownWords,
    WordLine,
    WordShown,
    WordsShown,
)

FILTERS = CategoryShown("filters", "what must be true", (WordLine("public", "the name is public"),))
CHECK = "checks:\n  names:\n    read: class\n"
WORD = WordShown("filters.public", "filters", "public", "the name is public", "fact", ("class", "function"), "", "",
                 example_key="parts.store.names", example_profile="web", example=CHECK, about_said="the fact")


def test_how_a_check_reads_shows_its_slots_its_categories_and_an_example():
    shown = ChecksShown("each fact is read", (Slot("read", "the kinds", "<kind>"),), (FILTERS,), "parts.names",
                        "web", CHECK)
    lines = checks_lines(shown)
    assert lines[:2] == ["how a check reads", "  each fact is read"]
    assert "  read  the kinds: <kind>" in lines and "  filters       1  what must be true" in lines
    assert "example: the rule parts.names of web expands to" in lines and "    names:" in lines
    assert json.loads(checks_document(shown))["example"] == {"key": "parts.names", "profile": "web", "check": CHECK}


def test_a_category_is_its_words_one_line_each():
    assert category_lines(WordsShown(FILTERS))[:4] == ["filters", "  what must be true", "",
                                                       "  public                 the name is public"]
    assert json.loads(category_document(WordsShown(FILTERS))) == {
        "ok": True, "category": "filters", "meaning": "what must be true",
        "words": [{"name": "public", "meaning": "the name is public"}]}


def test_a_word_says_what_it_is_about_and_applies_to_and_its_example_or_that_it_has_none():
    lines = word_lines(WORD)
    assert lines[:4] == ["filters.public", "  what: the name is public", "  about: the fact",
                         "  applies to: class, function"]
    assert "  example: the rule parts.store.names of web expands to" in lines and "        read: class" in lines
    assert word_lines(WordShown("targets.text", "targets", "text", "it says"))[-1] == (
        "  example: none of the profiles' own rules uses it")
    document = json.loads(word_document(WORD))
    assert (document["about"], document["side"], document["example"]["profile"]) == ("fact", None, "web")


def test_a_kind_shows_its_fields_and_when_one_is_carried_only_sometimes():
    kind = WordShown("kinds.call", "kinds", "call", "each call", fields=(
        FieldShown("line", "the line", ""), FieldShown("place", "where it sits", "target-placed")), needs=("call",),
        verb="call")
    lines = word_lines(kind)
    assert "    place  where it sits (when target-placed holds)" in lines and "  verb: call" in lines
    assert json.loads(word_document(kind))["fields"][1] == {"name": "place", "meaning": "where it sits",
                                                           "when": "target-placed"}


def test_the_rules_of_a_key_are_said_as_checks_and_a_key_of_none_says_why():
    shown = RuleShown("parts.names", "web", CHECK, 1, ("class",))
    assert rule_lines(shown)[0] == "parts.names expands to 1 rule in web, written as checks:"
    assert json.loads(rule_document(shown)) == {"ok": True, "key": "parts.names", "profile": "web", "rules": 1,
                                                "checks": CHECK, "needs": ["class"]}
    assert no_rule_message(NoRuleShown("parts.path", "web", "no rule")) == "parts.path in web: no rule"


def test_a_key_set_nowhere_says_where_it_would_be_set_and_how_a_profile_writes_it():
    unset = KeyUnset("parts.types_only", "web", KeyFacts("parts:\n  a: {}\n", "types_only", "part"))
    assert unset_lines(unset) == [
        "parts.types_only in web: the profile sets types_only on no part, so it expands to no rule", "",
        "a profile writes it so:", "  parts:", "    a: {}"]
    assert unset_lines(KeyUnset("guards.closed-tree", "web", KeyFacts("", "closed-tree"))) == [
        "guards.closed-tree in web: the profile does not set it, so it expands to no rule"]
    assert json.loads(unset_document(unset)) == {"ok": True, "key": "parts.types_only", "profile": "web", "rules": 0,
                                                 "checks": "", "set": False, "example": "parts:\n  a: {}\n"}


def test_a_word_that_does_not_exist_is_said_with_the_nearest_ones():
    found = UnknownWords("filters.publik", ("filters.public",))
    assert unknown_message(found) == "no word `filters.publik` of a check: the nearest are filters.public"
    assert json.loads(unknown_document(found))["nearest"] == ["filters.public"]
