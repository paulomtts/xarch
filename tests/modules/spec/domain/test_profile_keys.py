"""The table of retired names as xarch ships it: each entry has a scope of the format (or the scope of rule ids), a
name and one line of fixed text, once, and names nothing the format still has; it holds the part key tier, renamed
tests, the old names of never and its keys, those keys written outside uses, and the rule id rules, renamed
may-import."""
from xarch.kernel.violations import RULES
from xarch.modules.spec.domain.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import HELD, PART, PROFILE, RETIRED, RULE_ID, SCOPES, TIER, Retired


def test_every_entry_has_a_scope_a_name_and_one_line_of_text():
    scopes = {*SCOPES, *HELD, RULE_ID}
    assert [entry for entry in RETIRED if entry.scope not in scopes or not entry.name or not entry.text.strip()
            or "\n" in entry.text] == []


def test_no_two_entries_share_a_scope_and_a_name():
    assert len({(entry.scope, entry.name) for entry in RETIRED}) == len(RETIRED)


def test_no_entry_names_a_key_its_scope_still_has_nor_a_rule_id_xarch_checks():
    known = {(key.scope, key.name) for key in (*KEYS, *SLOTS)} | {(RULE_ID, rule) for rule in RULES}
    assert [entry for entry in RETIRED if (entry.scope, entry.name) in known] == []


def test_the_names_retired_are_tier_the_old_names_of_never_and_its_keys_written_outside_uses_and_the_rule_id_rules():
    assert RETIRED == (
        Retired(PART, "tier", "renamed in 0.3.0: write tests"),
        Retired(PART, "forbidden", "moved in 0.3.0: write uses: {never: <list>}"),
        Retired(TIER, "apply_forbidden", "moved in 0.3.0: write uses: {apply_never: true}"),
        Retired(PROFILE, "forbidden", "renamed in 0.3.0: write never"),
        Retired(RULE_ID, "forbidden", "renamed in 0.3.0: write never-use"),
        Retired(PART, "never", "a key of uses: write uses: {never: <list>}"),
        Retired(TIER, "apply_never", "a key of uses: write uses: {apply_never: true}"),
        Retired(RULE_ID, "rules", "renamed in 0.3.0: write may-import"),
        Retired(PART, "no_callbacks", "moved in 0.3.0: write guards: {no-callbacks: {parts: [<part>, ...]}}"))
