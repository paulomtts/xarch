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
from xarch.modules.spec.application.logic.key_lookup import keys_of, names_of, plain, required_of
from xarch.modules.spec.application.logic.profile_listing import referenced
from xarch.modules.spec.domain.guards import ORDER
from xarch.modules.spec.domain.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import (
    CHOICE_BUNDLED,
    CHOICE_LANGUAGES,
    CHOICE_PRESETS,
    COUNTERPART,
    EVAL,
    GUARD,
    HELD,
    MOCK_SPECS,
    PART,
    PART_IMPORTS_MAY,
    PROFILE,
    SCOPES,
    Key,
)
from xarch.modules.spec.domain.values import Language
from xarch.profile_values.language import InterfaceMark, SpecWriting

BASE = {"name": "example", "parts": {"documents/": {"role": "the documents"}}}
LISTING = ("src/documents.py", "tests/documents/check_documents.py", "tests/documents/builders.py")
BUNDLED = ("base",)
SUBSTITUTIONS = {"<bundled>": "base", "<preset>": "pytest", "<language>": "python"}


def filled(example: str) -> str:
    for token, name in SUBSTITUTIONS.items():
        example = example.replace(token, name)
    return said(example, PYTHON)


def merged(base: dict, extra: dict, top: bool = True) -> dict:
    """The example laid over the smallest profile; an example writing parts writes the whole tree of them."""
    result = deepcopy(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict) and not (top and key == "parts"):
            result[key] = merged(result[key], value, False)
        else:
            result[key] = value
    return result


def document_of(key: Key) -> dict:
    return merged(BASE, yaml.safe_load(filled(CATALOGUE.texts[key.address].example)))


def every_folder(document: dict) -> dict[str, tuple[str, ...]]:
    """LISTING as the files below every folder the document names."""
    return dict.fromkeys(referenced(document)[1], LISTING)


EVERY_SPEC = replace(READS_EVERY_FACT, checked=replace(READS_EVERY_FACT.checked, writing=replace(
    READS_EVERY_FACT.checked.writing, specs=SpecWriting(**{**vars(READS_EVERY_FACT.checked.writing.specs),
                                                            "type_argument": "{callee}<{before}{value}>()"}))))
"""Python, its reader supplying every fact, and writing a mock's spec by a type argument as well, as the TypeScript-like
test-only language does."""


def load(document: dict):
    """The document parsed under Python, its reader read as supplying every fact and its data file writing every way a
    mock names its spec: an example shows its key loading, whatever Python's own reader reads and its own file
    writes."""
    return parsed(document, bundled=BUNDLED, folders=every_folder(document), languages={"python": EVERY_SPEC})


def tree_parts(node: dict):
    """The map of every part in a folder tree: a file, or a folder holding a key of a part."""
    for key, value in node.items():
        if isinstance(value, dict) and (key.endswith("/") or "." in key):
            if "." in key or any(not (name.endswith("/") or "." in name) for name in value):
                yield value
            yield from tree_parts(value)


def containers(node, steps: list[str]):
    """Every mapping the steps of a scope's address lead to: `<x>` is any entry, `name[]` the items of a list, and
    `parts.<part>` each part of the folder tree."""
    if steps[:2] == ["parts", "<part>"] and isinstance(node, dict) and isinstance(node.get("parts"), dict):
        for part in tree_parts(node["parts"]):
            yield from containers(part, steps[2:])
        return
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


def beside_another_key(key: Key, holder: dict) -> None:
    """A part holds a key besides `role` where it is a part: without one it is only a folder."""
    if key.scope == PART:
        holder.setdefault("litmus", "a question")


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
    assert all(scope in SCOPES and (keys_of(scope) or scope in HELD.values()) for scope in opened)
    assert sorted(opened) == sorted(scope for scope in SCOPES if scope != PROFILE)


def test_the_guards_the_table_names_are_the_guards_the_loader_reads():
    assert {key.name for key in keys_of(GUARD)} == set(ORDER) - {"package-only"}
    assert all(key.rules == (key.name,) for key in keys_of(GUARD))
    assert next(key for key in keys_of("part") if key.name == "package_only").rules == ("package-only",)
    assert next(key for key in keys_of("part") if key.name == "optional").rules == ("structure",)


@pytest.mark.parametrize("key", KEYS, ids=lambda key: plain(key.address))
def test_the_example_of_a_key_uses_the_key_and_loads_in_the_smallest_profile_it_needs(key):
    document = document_of(key)
    assert any(key.name in holder or key.name in holder.values() for holder in holders(key, document)), \
        CATALOGUE.texts[key.address].example
    load(document)


def slot_example(slot: Key) -> dict:
    """The example of the slot laid over the smallest profile, once it is seen to write the slot."""
    document = merged(BASE, yaml.safe_load(filled(CATALOGUE.slots[slot.address].example)))
    written = {"yes": True, "no": False}.get(slot.name, slot.name)
    assert any(written in held for held in containers(document, slot.where.split("."))), slot.address
    return document


@pytest.mark.parametrize("slot", [slot for slot in SLOTS if slot.scope == EVAL], ids=lambda slot: plain(slot.address))
def test_the_example_of_a_slot_of_an_eval_uses_the_slot_and_loads_in_the_smallest_profile(slot):
    assert load(slot_example(slot)).evals


@pytest.mark.parametrize("slot", [slot for slot in SLOTS if slot.scope == COUNTERPART],
                         ids=lambda slot: plain(slot.address))
def test_the_example_of_a_slot_of_a_counterpart_uses_the_slot_and_loads_in_the_smallest_profile(slot):
    assert load(slot_example(slot)).counterparts


@pytest.mark.parametrize("slot", [slot for slot in SLOTS if slot.required], ids=lambda slot: plain(slot.address))
def test_a_slot_an_eval_needs_is_missing_in_the_loader_when_left_out(slot):
    document = merged(BASE, yaml.safe_load(filled(CATALOGUE.slots[slot.address].example)))
    del next(containers(document, slot.where.split(".")))[slot.name]
    assert any(f"missing `{slot.name}`" in problem for problem in problems(document, bundled=BUNDLED,
                                                                          folders=every_folder(document)))


@pytest.mark.parametrize("key", [key for key in KEYS if key.required], ids=lambda key: plain(key.address))
def test_a_required_key_is_missing_in_the_loader_when_left_out(key):
    document = document_of(key)
    beside_another_key(key, holders(key, document)[0])
    del holders(key, document)[0][key.name]
    assert any(f"missing `{key.name}`" in problem for problem in problems(document, bundled=BUNDLED,
                                                                         folders=every_folder(document)))


def test_the_smallest_profile_loads_and_every_symbol_is_explained():
    assert load(yaml.safe_load(CATALOGUE.smallest)).parts["documents"].path == ("documents",)
    assert CATALOGUE.symbols and all(symbol and meaning for symbol, meaning in CATALOGUE.symbols)


@pytest.mark.parametrize("scope", sorted(set(SCOPES) - {PART_IMPORTS_MAY, MOCK_SPECS}
                                          - {held for held in HELD.values() if not keys_of(held)}))
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


def test_an_entry_of_the_mock_specs_with_a_key_besides_its_own_is_told_each_key_of_the_scope():
    document = document_of(keys_of(MOCK_SPECS)[0])
    holders(keys_of(MOCK_SPECS)[0], document)[0]["zz_unknown"] = 1
    found = [p for p in problems(document, bundled=BUNDLED, folders=every_folder(document)) if "specs.0:" in p]
    assert found and [key.name for key in keys_of(MOCK_SPECS) if f"{{{key.name}: <" not in found[0]] == []


def test_a_part_is_named_by_its_place_or_by_name_and_holds_no_path_and_no_folders():
    assert names_of(PART) == {"holds", "imports", "litmus", "name", "optional", "package_only", "role", "shared",
                              "tests", "untested", "uses"}
    assert required_of(PART) == ("role",)
    assert [key.name for key in KEYS if key.scope == PART][0] == "name"
