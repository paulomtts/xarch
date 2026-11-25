"""The data file of the texts of the profile format: read into a catalogue, its fragments put in and the defaults of the
guards filled in, or refused naming the file with every problem."""
import pytest

from tests.modules.spec.format_files import KEYS_DOCUMENT
from xarch.modules.spec.application.logic.key_catalogue import catalogue_of
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import KeyText

SOURCE = "presets/format/keys.yaml"
WORDS = ("%language%, %extension%, %package_file%, %private%, %interface%, %interface_path%, %namespace%, %comment%, %directives%, "
         "%nothing%, %min_statements%, %min_fields%, %line%, %max_ask%, %fewest_examples%")
FRAGMENTS = {"part": "parts:\n  documents/:\n    role: the documents\n"}
TEXT = {"meaning": "the documents", "accepts": "a name", "example": "documents: {}"}
ROLE = "parts.<part>.role"


def keyed(texts: dict | None = None) -> dict:
    """A text for every key of the table, each address given in place of its own; one given as None is left out."""
    found = {key.address: TEXT for key in KEYS} | (texts or {})
    return {address: text for address, text in found.items() if text is not None}


def document(**sections) -> dict:
    """A data file that loads, each section given in place of its own; one given as None is left out."""
    found = {"fragments": FRAGMENTS, "smallest": "name: n\n", "symbols": {"store": "a part"}, "keys": keyed(),
             "slots": {key.address: TEXT for key in SLOTS}}
    found.update(sections)
    return {name: value for name, value in found.items() if value is not None}


def problems(given) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        catalogue_of(given)
    return [problem.removeprefix(f"{SOURCE}: ") for problem in caught.value.problems]


def test_the_shipped_file_gives_a_text_for_every_key_of_the_table_and_no_other():
    catalogue = catalogue_of(KEYS_DOCUMENT)
    assert list(catalogue.texts) == [key.address for key in KEYS]
    assert catalogue.smallest.startswith("name: documents-app\n") and catalogue.symbols[0][0] == "<folder>/"
    assert catalogue.texts["guards.no-duplicates.min_statements"].accepts == "a whole number, 4 when left out"
    assert catalogue.texts["guards.no-twins.min_fields"].accepts == "a whole number, 3 when left out"


def test_a_line_that_names_a_fragment_stands_for_its_text_and_the_defaults_of_the_guards_are_filled_in():
    catalogue = catalogue_of(document(keys=keyed({
        ROLE: {"meaning": "its role", "accepts": "one line of text", "example": "<<part>>\n    role: saves them\n"},
        "guards.no-twins": TEXT | {"accepts": "{min_fields: <number>}, %min_fields% when left out: %min_statements%"}})))
    assert catalogue.texts[ROLE] == KeyText("its role", "one line of text", FRAGMENTS["part"] + "    role: saves them\n")
    assert catalogue.texts["guards.no-twins"].accepts == "{min_fields: <number>}, 3 when left out: 4"


def test_a_fragment_may_hold_another_and_the_lines_around_it_stay():
    fragments = FRAGMENTS | {"tiered": "<<part>>\n    tests: unit\n"}
    catalogue = catalogue_of(document(fragments=fragments, keys=keyed({
        ROLE: TEXT | {"example": "tiers:\n  unit: {}\n<<tiered>>\n"}})))
    assert catalogue.texts[ROLE].example == "tiers:\n  unit: {}\n" + FRAGMENTS["part"] + "    tests: unit\n"


@pytest.mark.parametrize("given, found", [
    pytest.param("keys", ["must be a mapping of fragments, smallest, symbols, keys, slots"], id="a document that is no mapping"),
    pytest.param(document(format=1, symbols=None),
                 ["unknown key 'format': use fragments, smallest, symbols, keys, slots", "missing `symbols`"],
                 id="a section the format has not, and one left out"),
    pytest.param(document(keys=keyed({ROLE: None, "parts.<part>.colour": TEXT})),
                 ["keys: the format has no key 'parts.<part>.colour'", "keys: missing the text of 'parts.<part>.role'"],
                 id="the texts are of the keys of the table, one each"),
    pytest.param(document(keys=keyed({"name": TEXT | {"meaning": "", "note": "n"}, "based_on": "x"})),
                 ["keys.name: unknown key 'note': use meaning, accepts, example",
                  "keys.name.meaning: must be a non-empty string",
                  "keys.based_on: must be a mapping of meaning, accepts, example"],
                 id="a text is a meaning, what the key accepts and an example, none of them empty"),
    pytest.param(document(keys=keyed({ROLE: TEXT | {"example": "<<parts>>\n"}})),
                 ["keys.parts.<part>.role.example: no fragment 'parts': use part"],
                 id="an example names a fragment that is not there"),
    pytest.param(document(fragments={"a": "<<b>>\n", "b": "<<a>>\n", "c": "tests: unit"}),
                 ["fragments.b: the fragments include each other in a loop: a -> b -> a",
                  "fragments.a: the fragments include each other in a loop: b -> a -> b",
                  "fragments.c: must end with a line break"],
                 id="fragments that include each other, and one that does not end its last line"),
    pytest.param(document(smallest="", symbols={"store": 3}, keys=keyed({"name": TEXT | {"meaning": "a %colour% name"}})),
                 ["smallest: must be a non-empty string", "symbols.store: must be a non-empty string",
                  f"keys.name.meaning: unknown word %colour%: use {WORDS}"],
                 id="an empty profile or symbol, and a word no language says"),
    pytest.param(document(fragments=[], symbols="x", keys="y"),
                 ["fragments: must be a mapping of names to text", "symbols: must be a mapping of names to text",
                  "keys: must be a mapping of each key's address to {meaning, accepts, example}"],
                 id="sections that are no mappings"),
])
def test_a_broken_data_file_is_refused_naming_it_with_every_problem(given, found):
    assert problems(given) == found


def test_the_numbers_review_s_keys_say_are_filled_in_from_the_values_spec_holds():
    catalogue = catalogue_of(document(keys=keyed({"evals.placement.lines": TEXT | {
        "accepts": "%line% when left out; at most %max_ask% characters; at least %fewest_examples% of each"}})))
    assert catalogue.texts["evals.placement.lines"].accepts == (
        "0.3 when left out; at most 400 characters; at least 2 of each")


@pytest.mark.parametrize("address", [
    pytest.param("parts.<part>.holds", id="holds"),
    pytest.param("parts.<part>.holds.classes.names", id="names"),
    pytest.param("guards.private-imports", id="private-imports"),
])
def test_the_texts_that_say_a_public_name_say_it_by_the_reader_and_never_by_the_prefix(address):
    text = catalogue_of(KEYS_DOCUMENT).texts[address]
    said = f"{text.meaning} {text.accepts}"
    assert "%private%" not in said
    assert "the language's reader says" in said
