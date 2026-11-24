"""The table of profile keys explains every key the loader accepts, and only those: the texts of the format's data file,
as xarch ships it, give each key its meaning, what it accepts and an example, and every example loads through the loader
once merged into the smallest profile."""
from copy import deepcopy
from dataclasses import replace

import pytest
import yaml

from tests.modules.spec.format_files import CATALOGUE
from tests.modules.spec.languages import BRACE, PERCENT, PYTHON, READS_EVERY_FACT
from tests.modules.spec.profiles import PRESETS, parsed, problems
from xarch.kernel.violations import RULES
from xarch.modules.spec.application.logic.explain import said
from xarch.modules.spec.application.logic.key_lookup import keys_of, plain
from xarch.modules.spec.application.logic.profile_listing import referenced
from xarch.modules.spec.domain.guards import ORDER
from xarch.modules.spec.domain.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import (
    CHOICE_BUNDLED,
    CHOICE_LANGUAGES,
    CHOICE_PRESETS,
    GUARD,
    PART_IMPORTS_MAY,
    PROFILE,
    SCOPES,
    Key,
)
from xarch.modules.spec.domain.values import Language
from xarch.profile_values.language import InterfaceMark

BASE = {"name": "example", "parts": {"documents": {"path": "documents", "role": "the documents"}}}
LISTING = ("src/documents.py", "tests/documents/check_documents.py", "tests/documents/builders.py")
BUNDLED = ("base",)
SUBSTITUTIONS = {"<bundled>": "base", "<preset>": "pytest", "<language>": "python"}


def filled(example: str) -> str:
    for token, name in SUBSTITUTIONS.items():
        example = example.replace(token, name)
    return said(example, PYTHON)


def merged(base: dict, extra: dict) -> dict:
    result = deepcopy(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merged(result[key], value)
        else:
            result[key] = value
    return result


def document_of(key: Key) -> dict:
    return merged(BASE, yaml.safe_load(filled(CATALOGUE.texts[key.address].example)))


def every_folder(document: dict) -> dict[str, tuple[str, ...]]:
    """LISTING as the files below every folder the document names."""
    return dict.fromkeys(referenced(document)[1], LISTING)


def load(document: dict):
    """The document parsed under Python, its reader read as supplying every fact: an example shows its key loading,
    whatever Python's own reader reads."""
    return parsed(document, bundled=BUNDLED, folders=every_folder(document), languages={"python": READS_EVERY_FACT})


def containers(node, steps: list[str]):
    """Every mapping the steps of a scope's address lead to: `<x>` is any entry, `name[]` the items of a list."""
    if not steps:
        if isinstance(node, dict):
            yield node
        elif isinstance(node, list):
            yield from (item for item in node if isinstance(item, dict))
        return
    step, rest = steps[0], steps[1:]
    if not isinstance(node, dict):
        return
    if step.startswith("<"):
        for value in node.values():
            yield from containers(value, rest)
        return
    listed = step.endswith("[]")
    value = node.get(step.removesuffix("[]"))
    for item in (value if listed and isinstance(value, list) else [value]):
        yield from containers(item, rest)


def holders(key: Key, document: dict) -> list[dict]:
    steps = [] if key.scope == PROFILE else SCOPES[key.scope].split(".")
    return list(containers(document, steps))


def test_every_key_says_what_it_means_what_it_accepts_and_shows_an_example():
    assert list(CATALOGUE.texts) == [key.address for key in KEYS]
    assert [address for address, text in CATALOGUE.texts.items()
            if not (text.meaning and text.accepts and text.example)] == []


def test_the_plain_address_of_every_key_is_unique_and_has_no_placeholder():
    plains = [plain(key.address) for key in KEYS]
    assert len(set(plains)) == len(plains)
    assert not [p for p in plains if "<" in p or "[" in p]
    assert plain("parts.<part>.imports.may") == "parts.imports.may"
    assert plain("docs.naming[].kind") == "docs.naming.kind"
    assert plain("tiers.<tier>.docs.subject") == "tiers.docs.subject"


def test_every_rule_a_key_feeds_is_a_rule_id_of_check():
    assert [(key.address, rule) for key in KEYS for rule in key.rules if rule not in RULES] == []


def test_a_key_that_holds_keys_opens_a_scope_and_every_scope_but_the_file_is_opened_by_one_key():
    opened = [key.opens for key in KEYS if key.opens]
    assert all(scope in SCOPES and keys_of(scope) for scope in opened)
    assert sorted(opened) == sorted(scope for scope in SCOPES if scope != PROFILE)


def test_the_guards_the_table_names_are_the_guards_the_loader_reads():
    assert {key.name for key in keys_of(GUARD)} == set(ORDER) - {"package-only"}
    assert all(key.rules == (key.name,) for key in keys_of(GUARD))
    assert next(key for key in keys_of("part") if key.name == "package_only").rules == ("package-only",)


@pytest.mark.parametrize("key", KEYS, ids=lambda key: plain(key.address))
def test_the_example_of_a_key_uses_the_key_and_loads_in_the_smallest_profile_it_needs(key):
    document = document_of(key)
    assert any(key.name in holder or key.name in holder.values() for holder in holders(key, document)), \
        CATALOGUE.texts[key.address].example
    load(document)


@pytest.mark.parametrize("slot", SLOTS, ids=lambda slot: plain(slot.address))
def test_the_example_of_a_slot_of_an_eval_uses_the_slot_and_loads_in_the_smallest_profile(slot):
    document = merged(BASE, yaml.safe_load(filled(CATALOGUE.slots[slot.address].example)))
    written = {"yes": True, "no": False}.get(slot.name, slot.name)
    assert any(written in held for held in containers(document, slot.where.split("."))), slot.address
    assert load(document).evals


@pytest.mark.parametrize("slot", [slot for slot in SLOTS if slot.required], ids=lambda slot: plain(slot.address))
def test_a_slot_an_eval_needs_is_missing_in_the_loader_when_left_out(slot):
    document = merged(BASE, yaml.safe_load(filled(CATALOGUE.slots[slot.address].example)))
    del next(containers(document, slot.where.split(".")))[slot.name]
    assert any(f"missing `{slot.name}`" in problem for problem in problems(document, bundled=BUNDLED,
                                                                          folders=every_folder(document)))


@pytest.mark.parametrize("key", [key for key in KEYS if key.required], ids=lambda key: plain(key.address))
def test_a_required_key_is_missing_in_the_loader_when_left_out(key):
    document = document_of(key)
    del holders(key, document)[0][key.name]
    assert any(f"missing `{key.name}`" in problem for problem in problems(document, bundled=BUNDLED,
                                                                         folders=every_folder(document)))


def test_the_smallest_profile_loads_and_every_symbol_is_explained():
    assert load(yaml.safe_load(CATALOGUE.smallest)).parts["documents"].path == ("documents",)
    assert CATALOGUE.symbols and all(symbol and meaning for symbol, meaning in CATALOGUE.symbols)


@pytest.mark.parametrize("scope", sorted(set(SCOPES) - {PART_IMPORTS_MAY}))
def test_the_keys_the_loader_names_in_its_unknown_key_message_are_the_keys_of_the_table(scope):
    document = document_of(keys_of(scope)[0])
    holders(keys_of(scope)[0], document)[0]["zz_unknown"] = 1
    found = [p for p in problems(document, bundled=BUNDLED, folders=every_folder(document)) if "zz_unknown" in p]
    assert found, f"{scope}: the loader accepts an unknown key"
    named = set(found[0].split(": use ")[-1].split(", "))
    assert named == {key.name for key in keys_of(scope)}


def test_the_choices_a_key_offers_are_bundled_names_testing_presets_or_languages():
    assert {key.choices for key in KEYS if key.choices} == {CHOICE_BUNDLED, CHOICE_PRESETS, CHOICE_LANGUAGES}
    assert set(PRESETS) == {"pytest"}


def test_every_text_of_the_table_is_said_in_the_words_of_a_language_with_no_word_left_over():
    texts = [*(part for text in CATALOGUE.texts.values() for part in (text.meaning, text.accepts, text.example)),
             *(text for pair in CATALOGUE.symbols for text in pair), CATALOGUE.smallest]
    assert [text for text in texts if "%" in said(text, PYTHON)] == []


def test_a_word_of_the_table_is_what_the_language_says_for_it():
    assert said("every %language% file, `%package_file%`, a list of %extension% names, `%namespace%.open`", PYTHON) == (
        "every Python file, `__init__.py`, a list of .py names, `builtins.open`")
    assert said("a %interface% as `%interface_path%`; %other%", PYTHON) == "a Protocol as `typing.Protocol`; %other%"
    assert said("%interface%s", Language()) == "s"
    assert said("a name that starts with `%private%`", PYTHON) == "a name that starts with `_`"


def test_the_ending_and_the_package_file_a_text_says_are_the_language_s_first_and_nothing_when_it_has_none():
    assert said("%extension% `%package_file%`", BRACE) == ".ts `index.ts`"
    assert said("%extension% `%package_file%`", PERCENT) == ".cls ``"


def test_the_path_of_an_interface_is_said_with_the_member_of_the_language():
    based = (InterfaceMark(("%Library", "RegisteredObject")),)
    hashed = replace(PERCENT, checked=replace(PERCENT.checked, member="#", interface=based))
    assert said("`%interface_path%`", hashed) == "`%Library#RegisteredObject`"


def test_an_interface_is_called_by_the_last_step_of_its_first_base_or_by_its_keyword():
    assert (PYTHON.interface_name, BRACE.interface_name, PERCENT.interface_name, Language().interface_name) == (
        "Protocol", "interface", "Abstract", "")


def test_the_path_of_an_interface_is_its_first_base_or_its_keyword():
    assert [said("`%interface_path%`", language) for language in (PYTHON, BRACE, PERCENT, Language())] == [
        "`typing.Protocol`", "`interface`", "`Abstract`", "``"]


def test_the_annotations_of_no_value_are_said_each_as_written_joined_by_or():
    assert [said("%nothing%", language) for language in (PYTHON, BRACE, PERCENT)] == ["None", "void or Promise<void>", ""]
