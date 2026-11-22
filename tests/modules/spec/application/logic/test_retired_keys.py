"""The table of retired names, read by every path that refuses an unknown name: the lookup by scope and name, and by
the address `profile explain` is typed with; every unknown key of a mapping, of the file, under `hints` and under
`guards` that has an entry under its scope gives one problem of its own with the entry's fixed text, ahead of today's
message for the others, which is unchanged. A table built for each test is set where the lookup reads it."""
import pytest

from xarch.modules.spec.application.logic import key_lookup
from xarch.modules.spec.application.logic.key_lookup import retired, retired_at
from xarch.modules.spec.domain.profile_keys import EVAL, NAMING, PART, PROFILE, RULE_ID, TIER, Retired

RENAMED = "renamed in 0.3.0: write tier"
MOVED = "moved in 0.3.0: write uses: {never: <list>}"
MISPLACED = "a key of uses: write uses: {never: <list>}"


def table(monkeypatch: pytest.MonkeyPatch, *entries: tuple[str, str, str]) -> None:
    """The table of retired names is the entries given, each (scope, name, text), for this test alone."""
    monkeypatch.setattr(key_lookup, "RETIRED", tuple(Retired(scope, name, text) for scope, name, text in entries))


def test_the_lookup_gives_the_text_of_the_entry_for_a_scope_and_a_name_or_nothing(monkeypatch):
    table(monkeypatch, (PART, "tested_by", RENAMED))
    assert (retired(PART, "tested_by"), retired(TIER, "tested_by"), retired(PART, "banned"), retired("", "tested_by")) \
        == (RENAMED, "", "", "")


def test_the_shipped_table_gives_nothing():
    assert (retired(PART, "tier"), retired_at("parts.tier")) == ("", "")


@pytest.mark.parametrize("entry, address", [
    pytest.param((PART, "tested_by", RENAMED), "parts.tested_by", id="a key of a part, typed plain"),
    pytest.param((PART, "tested_by", RENAMED), "parts.<part>.tested_by", id="with the placeholder of the part"),
    pytest.param((PART, "tested_by", RENAMED), " parts.tested_by. ", id="with spaces and a stray dot"),
    pytest.param((PROFILE, "banned", MOVED), "banned", id="a key of the file, by its bare name"),
    pytest.param((NAMING, "level", MISPLACED), "docs.naming[].level", id="a key of a row of a list, with []"),
    pytest.param((NAMING, "level", MISPLACED), "docs.naming.level", id="a key of a row of a list, typed plain"),
    pytest.param((EVAL, "asks", RENAMED), "evals.<id>.asks", id="a slot of an eval, with the placeholder of its id"),
    pytest.param((EVAL, "asks", RENAMED), "evals.title-rule.asks", id="a slot of an eval, under an id"),
])
def test_an_address_of_an_entry_gives_its_text_however_it_is_typed(monkeypatch, entry, address):
    table(monkeypatch, entry)
    assert retired_at(address) == entry[2]


@pytest.mark.parametrize("entry, address", [
    pytest.param((PART, "tested_by", RENAMED), "tiers.tested_by", id="the name under another scope"),
    pytest.param((PART, "tested_by", RENAMED), "tested_by", id="the name at the top of the file"),
    pytest.param((PROFILE, "banned", MOVED), "parts.banned", id="a key of the file, under a part"),
    pytest.param((EVAL, "asks", RENAMED), "evals.placement.asks", id="placement is a key of evals, not an eval's id"),
    pytest.param((EVAL, "asks", RENAMED), "evals.asks", id="a slot of an eval, typed with no id step"),
    pytest.param((RULE_ID, "old-rule", RENAMED), "hints.old-rule", id="a rule id has no address"),
    pytest.param((RULE_ID, "old-rule", RENAMED), "old-rule", id="nor a bare one"),
])
def test_an_address_that_is_no_entry_gives_nothing(monkeypatch, entry, address):
    table(monkeypatch, entry)
    assert retired_at(address) == ""
