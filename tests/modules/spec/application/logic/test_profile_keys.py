"""The table of profile keys explains every key the loader accepts, and only those: each key has its meaning, what it
accepts and an example, and every example loads through the loader of format 2 once merged into the smallest profile."""
from copy import deepcopy

import pytest
import yaml

from tests.modules.spec.profiles_v2 import PRESETS, parsed, problems
from xarch.kernel.violations import RULES
from xarch.modules.spec.application.logic.key_lookup import keys_of, plain
from xarch.modules.spec.domain.guards import GUARDS
from xarch.modules.spec.domain.profile_keys import (
    CHOICE_BUNDLED,
    CHOICE_PRESETS,
    GUARD,
    KEYS,
    PROFILE,
    SCOPES,
    SMALLEST,
    SYMBOLS,
    Key,
)

BASE = {"xarch": 2, "name": "example", "parts": {"documents": {"path": "documents", "role": "the documents"}}}
LISTING = ("src/documents.py", "tests/documents/check_documents.py", "tests/documents/builders.py")
BUNDLED = ("base",)
SUBSTITUTIONS = {"<bundled>": "base", "<preset>": "pytest"}


def filled(example: str) -> str:
    for token, name in SUBSTITUTIONS.items():
        example = example.replace(token, name)
    return example


def merged(base: dict, extra: dict) -> dict:
    result = deepcopy(base)
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merged(result[key], value)
        else:
            result[key] = value
    return result


def document_of(key: Key) -> dict:
    return merged(BASE, yaml.safe_load(filled(key.example)))


def load(document: dict):
    return parsed(document, bundled=BUNDLED, folder_files=lambda relative: LISTING)


def containers(node, steps: list[str]):
    """Every mapping the steps of a scope's address lead to: `<x>` is any entry, `name[]` the items of a list."""
    if not steps:
        if isinstance(node, dict):
            yield node
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
    assert [key.address for key in KEYS if not (key.meaning and key.accepts and key.example)] == []


def test_the_plain_address_of_every_key_is_unique_and_has_no_placeholder():
    plains = [plain(key.address) for key in KEYS]
    assert len(set(plains)) == len(plains)
    assert not [p for p in plains if "<" in p or "[" in p]
    assert plain("parts.<part>.may_import") == "parts.may_import"
    assert plain("docs.naming[].kind") == "docs.naming.kind"
    assert plain("tiers.<tier>.docs.subject") == "tiers.docs.subject"


def test_every_rule_a_key_feeds_is_a_rule_id_of_check():
    assert [(key.address, rule) for key in KEYS for rule in key.rules if rule not in RULES] == []


def test_a_key_that_holds_keys_opens_a_scope_and_every_scope_but_the_file_is_opened_by_one_key():
    opened = [key.opens for key in KEYS if key.opens]
    assert all(scope in SCOPES and keys_of(scope) for scope in opened)
    assert sorted(opened) == sorted(scope for scope in SCOPES if scope != PROFILE)


def test_the_guards_the_table_names_are_the_guards_the_loader_reads():
    assert {key.name for key in keys_of(GUARD)} == set(GUARDS) - {"package-only"}
    assert all(key.rules == (key.name,) for key in keys_of(GUARD))
    assert next(key for key in keys_of("part") if key.name == "package_only").rules == ("package-only",)


@pytest.mark.parametrize("key", KEYS, ids=lambda key: plain(key.address))
def test_the_example_of_a_key_uses_the_key_and_loads_in_the_smallest_profile_it_needs(key):
    document = document_of(key)
    assert any(key.name in holder for holder in holders(key, document)), key.example
    load(document)


@pytest.mark.parametrize("key", [key for key in KEYS if key.required], ids=lambda key: plain(key.address))
def test_a_required_key_is_missing_in_the_loader_when_left_out(key):
    document = document_of(key)
    for holder in holders(key, document):
        holder.pop(key.name, None)
    assert any(f"missing `{key.name}`" in problem for problem in problems(document, bundled=BUNDLED,
                                                                         folder_files=lambda relative: LISTING))


def test_the_smallest_profile_loads_and_every_symbol_is_explained():
    assert load(yaml.safe_load(SMALLEST)).parts["documents"].path == ("documents",)
    assert SYMBOLS and all(symbol and meaning for symbol, meaning in SYMBOLS)


@pytest.mark.parametrize("scope", sorted(SCOPES))
def test_the_keys_the_loader_names_in_its_unknown_key_message_are_the_keys_of_the_table(scope):
    document = document_of(keys_of(scope)[0])
    holders(keys_of(scope)[0], document)[0]["zz_unknown"] = 1
    found = [p for p in problems(document, bundled=BUNDLED, folder_files=lambda relative: LISTING) if "zz_unknown" in p]
    assert found, f"{scope}: the loader accepts an unknown key"
    named = set(found[0].split(": use ")[-1].split(", "))
    assert named == {key.name for key in keys_of(scope)}


def test_the_choices_a_key_offers_are_bundled_names_or_testing_presets():
    assert {key.choices for key in KEYS if key.choices} == {CHOICE_BUNDLED, CHOICE_PRESETS}
    assert set(PRESETS) == {"pytest"}
