"""What `xarch profile explain` reads from the table of keys: the overview's keys, the key at an address a person types,
an example with the names xarch ships, and the nearest keys to an address that does not exist."""
from xarch.modules.spec.application.logic.explain import (
    cleaned,
    example_of,
    held_by,
    key_at,
    nearest,
    overview_keys,
)
from xarch.modules.spec.application.logic.key_lookup import plain
from xarch.modules.spec.domain.key_table import KEYS, SLOTS


def test_the_overview_lists_the_keys_of_the_file_with_the_keys_of_each_map_below_it_and_goes_no_deeper():
    found = [(plain(key.address), depth) for key, depth in overview_keys()]
    assert found[:3] == [("name", 0), ("based_on", 0), ("language", 0)]
    assert ("parts", 0) in found and ("parts.may_import", 1) in found
    assert {depth for _, depth in found} == {0, 1}


def test_every_key_of_the_table_is_reached_from_the_overview_through_the_keys_each_key_holds():
    reached: set[str] = set()
    pending = [key for key, depth in overview_keys() if depth == 0]
    while pending:
        key = pending.pop()
        reached.add(plain(key.address))
        pending += held_by(key)
    assert reached == {plain(key.address) for key in (*KEYS, *SLOTS)}


def test_a_key_is_found_by_the_address_a_person_types_with_or_without_the_placeholders():
    found = key_at("parts.may_import")
    assert found is not None and found.rules == ("may-import",) and found.where == "parts.<part>"
    assert key_at("parts.<part>.may_import") is found and key_at(" parts.may_import. ") is found
    assert key_at("guards.no-duplicates").rules == ("no-duplicates",)
    assert key_at("parts.may_imports") is None and cleaned(" a.<b>.c. ") == "a.c"


def test_a_key_that_holds_keys_gives_them_and_one_that_holds_none_gives_none():
    assert [key.name for key in held_by(key_at("fakes"))] == ["folder", "for", "prefix"]
    assert held_by(key_at("parts.may_import")) == ()


def test_the_example_of_a_key_that_names_something_xarch_ships_uses_the_first_name_of_the_list():
    assert example_of(key_at("based_on"), "based_on: <bundled>", ("base", "other")) == "based_on: base"
    assert example_of(key_at("based_on"), "based_on: <bundled>", ()) == "based_on: <bundled>"
    assert example_of(key_at("parts.may_import"), "may_import: [<bundled>]", ("base",)) == "may_import: [<bundled>]"


def test_the_nearest_keys_read_like_what_was_typed_else_are_the_keys_of_the_deepest_key_that_exists():
    assert nearest("parts.may_imports")[0] == "parts.may_import" and nearest("pats")[0] == "parts"
    assert all(key.startswith("parts.") for key in nearest("parts.colour"))
    assert "name" in nearest("zzzzzz")
