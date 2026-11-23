"""Use case: explain how a check is written, a category of its words, or one word, from the vocabulary the engine
reads, an example being the first rule of the profiles named that is written with the word; an address of no word
comes back with the nearest ones."""
from pathlib import Path

import pytest

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import profile
from xarch.modules.rules.contract import (
    CheckRefused,
    ChecksShown,
    ExplainWords,
    NoWords,
    UnknownWords,
    WordShown,
    WordsShown,
)
from xarch.modules.rules.domain.errors import ProfileUnusable
from xarch.modules.rules.domain.outcomes import Known

APP = Path("/src/app")
NAMED = profile(names={"services": {"classes": ("*Service",)}})


def explain(given: FakeProfiles):
    return controller(FakeSourceTree(None, {}), given).explain_words


APPLIES = ("syntax-error", "file", "names-mentioned", "import", "imported-name", "use", "method-call", "call",
           "construction", "function-reference", "import-into-app", "import-into-tests", "comment", "class", "function",
           "callback")
"""Every kind of fact, which a quantifier applies to."""
WORKED = ("no-todo: reads comment\nno-todo.flagged: documents/notes: ' TODO: split this file\\n'\n"
          "no-todo.clean: documents/notes: ' split by kind\\n'\n")
"""The first check written for the explanation, as the fake format writes it, in a language that names no tokens."""


@pytest.mark.parametrize("given, when, then", [
    pytest.param(FakeProfiles({}), ExplainWords("checks.keep"),
                 WordShown("checks.keep", "checks", "keep", "the filters a fact must pass, all of them, to be read: "
                                                            "[<filter>, ...]", value="filters",
                           example_key="checks.no-todo", example=WORKED),
                 id="a slot of a check is what it accepts, with a check written for the explanation"),
    pytest.param(FakeProfiles({"named": NAMED}), ExplainWords("quantifiers.may_only", APP),
                 WordShown("quantifiers.may_only", "quantifiers", "may_only",
                           "a kept fact that matches none of the targets is a finding", applies_to=APPLIES,
                           example_key="parts.kernel.imports.may", example_profile="named",
                           example="may-import: reads import-into-app\n"),
                 id="a word is explained in full, with a rule of the profile the project knows that uses it"),
    pytest.param(FakeProfiles({"bundled": profile(), "mine": NAMED}, known=Known("mine", ("bundled",))),
                 ExplainWords("quantifiers.may_only", APP),
                 WordShown("quantifiers.may_only", "quantifiers", "may_only",
                           "a kept fact that matches none of the targets is a finding", applies_to=APPLIES,
                           example_key="parts.kernel.imports.may", example_profile="mine",
                           example="may-import: reads import-into-app\n"),
                 id="the profile in force is searched for an example before the bundled ones"),
    pytest.param(FakeProfiles({}, known=ProfileUnusable(f"cannot read {APP.parent}/pyproject.toml: bad")),
                 ExplainWords("filters.public", APP), CheckRefused(f"cannot read {APP.parent}/pyproject.toml: bad"),
                 id="a project whose profile cannot be chosen or loaded is refused with why"),
    pytest.param(FakeProfiles({}), ExplainWords("filters.publik"), UnknownWords("filters.publik", ("filters.public", "filters.below",
                                                                                     "filters.placed")),
                 id="an address of no word comes back with the nearest ones"),
    pytest.param(FakeProfiles({}), ExplainWords("parts.may_import"), NoWords("parts.may_import", ("variables.mirrored_may_import",)),
                 id="an address that names no category of words comes back with the words that read like it"),
])
def test_words(given, when, then):
    assert explain(given)(when) == then


def test_a_category_is_its_words_each_in_a_line():
    found = explain(FakeProfiles({}))(ExplainWords("filters"))
    assert type(found) is WordsShown
    assert (found.category.name, found.category.words[0].name, len(found.category.words)) == ("filters", "test", 42)


def test_a_word_s_example_is_the_first_rule_of_the_first_profile_written_with_it():
    found = explain(FakeProfiles({"none": profile(), "named": NAMED}))(ExplainWords("filters.public", APP))
    assert (found.example_key, found.example_profile) == ("parts.services.holds.classes.names", "named")
    assert found.example.splitlines() == ["names: reads class"]


def test_a_word_no_rule_of_the_profiles_uses_has_a_check_written_for_the_explanation_as_its_example():
    found = explain(FakeProfiles({"none": profile()}))(ExplainWords("targets.text", APP))
    assert (found.example_key, found.example_profile, found.applies_to, found.value) == (
        "checks.no-todo", "", ("syntax-error", "comment"), "patterns")
    assert "no-todo.flagged: documents/notes.py: '# TODO: split this file\\n'" in found.example.splitlines()


def test_a_kind_is_explained_with_its_fields_what_it_needs_of_the_language_and_its_verb():
    found = explain(FakeProfiles({}))(ExplainWords("kinds.method-call"))
    assert [f.name for f in found.fields] == ["line", "method", "name", "on-own-object"]
    assert (found.needs, found.verb) == (("method_call",), "call")


def test_how_a_check_is_written_lists_every_slot_and_every_category_with_its_words():
    found = explain(FakeProfiles({"named": NAMED}))(ExplainWords("checks", APP))
    assert type(found) is ChecksShown
    assert [slot.name for slot in found.slots][:3] == ["read", "in", "keep"]
    assert [c.name for c in found.categories] == ["kinds", "quantifiers", "targets", "filters", "variables"]
    assert (found.example_key, found.example_profile) == ("checks.no-todo", "")
    assert found.example.splitlines()[0] == "no-todo: reads comment"


def test_a_slot_of_a_check_is_explained_with_what_it_accepts_and_a_check_written_with_it():
    found = explain(FakeProfiles({}))(ExplainWords("checks.keep"))
    assert (found.name, found.value, found.example_key) == ("keep", "filters", "checks.no-todo")
    assert found.meaning.startswith("the filters a fact must pass, all of them, to be read: [<filter>, ...]")
    assert explain(FakeProfiles({}))(ExplainWords("checks.kep")) == UnknownWords(
        "checks.kep", ("checks.keep", "checks.except", "checks.read"))
    found = explain(FakeProfiles({"any": profile()}))(ExplainWords("checks.may_only", APP))
    assert found.example_key == "parts.kernel.imports.may"
