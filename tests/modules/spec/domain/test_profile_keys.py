"""The table of retired names as xarch ships it: each entry has a scope of the format (or the scope of rule ids), a
name and one line of fixed text, once, and names nothing the format still has; at this step it has no entry."""
from xarch.kernel.violations import RULES
from xarch.modules.spec.domain.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import HELD, RETIRED, RULE_ID, SCOPES


def test_every_entry_has_a_scope_a_name_and_one_line_of_text():
    scopes = {*SCOPES, *HELD, RULE_ID}
    assert [entry for entry in RETIRED if entry.scope not in scopes or not entry.name or not entry.text.strip()
            or "\n" in entry.text] == []


def test_no_two_entries_share_a_scope_and_a_name():
    assert len({(entry.scope, entry.name) for entry in RETIRED}) == len(RETIRED)


def test_no_entry_names_a_key_its_scope_still_has_nor_a_rule_id_xarch_checks():
    known = {(key.scope, key.name) for key in (*KEYS, *SLOTS)} | {(RULE_ID, rule) for rule in RULES}
    assert [entry for entry in RETIRED if (entry.scope, entry.name) in known] == []


def test_no_name_is_retired_yet():
    assert RETIRED == ()
