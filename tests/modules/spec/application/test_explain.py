"""Use case: explain the format of a profile, the whole of it or one key, with the names xarch ships as choices."""
from dataclasses import fields

import pytest

from tests.modules.spec.application.builders import spec_controller
from xarch.modules.spec.contract import Explain, FormatExplained, KeyExplained, Shown, Symbol, UnknownKey
from xarch.modules.spec.domain.profile_keys import SMALLEST, SYMBOLS

BUNDLED = {"base": {}, "other": {}}


def held(result) -> tuple:
    return tuple(getattr(result, field.name) for field in fields(result))


def explained(key: str):
    return spec_controller(BUNDLED)[0].explain(Explain(key))


BASED_ON = explained("based_on")
FORMAT = spec_controller(BUNDLED)[0].explain(Explain())


@pytest.mark.parametrize("given, when, then", [
    pytest.param(BUNDLED, Explain(), FormatExplained(*held(FORMAT)), id="with no key the whole format is explained"),
    pytest.param(BUNDLED, Explain("based_on"), KeyExplained(*held(BASED_ON)),
                 id="a key that names a bundled profile offers the ones xarch ships"),
    pytest.param(BUNDLED, Explain("parts.may_imports"),
                 UnknownKey("parts.may_imports", ("parts.may_import", "parts.must_import", "tiers.may_import")),
                 id="a key the format does not have is refused with the nearest keys"),
])
def test_explain(given, when, then):
    spec, _ = spec_controller(given)
    assert spec.explain(when) == then


def test_the_whole_format_is_the_keys_of_the_file_their_symbols_and_the_smallest_profile():
    assert FORMAT.version == 2 and FORMAT.smallest == SMALLEST
    assert FORMAT.symbols == tuple(Symbol(symbol, meaning) for symbol, meaning in SYMBOLS)
    assert FORMAT.shape[0] == Shown("xarch", 0, "the format version", True, False)
    assert Shown("parts.may_import", 1, "what the part may import besides itself", False, True) in FORMAT.shape
    assert "xarch profile explain parts.may_import" in FORMAT.deeper


def test_a_key_says_what_it_accepts_whether_check_enforces_it_through_which_rule_and_what_it_holds():
    key = explained("parts.may_import")
    assert (key.key, key.where, key.required, key.enforced, key.rules) == (
        "parts.may_import", "parts.<part>", False, True, ("rules",))
    assert "@any" in key.accepts and "may_import: [core]" in key.example and key.keys == ()
    assert [(held_key.key, held_key.required) for held_key in explained("fakes").keys] == [
        ("fakes.folder", True), ("fakes.for", True), ("fakes.prefix", False)]


def test_the_choices_are_the_bundled_profiles_and_the_testing_presets_the_files_hold():
    assert BASED_ON.choices == ("base", "other") and "based_on: base" in BASED_ON.example
    assert explained("testing").choices == ("pytest",)
    assert explained("parts").choices == ()
