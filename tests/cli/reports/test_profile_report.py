"""How `xarch profile` shows what it found, on hand-made results: a key the format lacks, and a copy just written."""
import json
from pathlib import Path

from xarch.cli.reports.profile_report import created_lines, key_document, key_lines, unknown_document, unknown_message
from xarch.modules.spec.contract import KeyExplained, Need, ProfileCreated, UnknownKey


def test_an_unknown_key_is_said_with_the_nearest_ones_in_text_and_in_json():
    found = UnknownKey("tire", ("tier", "tiers"))
    assert unknown_message(found) == "no key `tire` in the format: the nearest are tier, tiers"
    assert json.loads(unknown_document(found)) == {
        "ok": False, "error": unknown_message(found), "key": "tire", "nearest": ["tier", "tiers"]}


def test_a_new_profile_says_what_was_written_and_how_to_put_it_in_force():
    done = ProfileCreated(Path("mine"), Path("mine/mine.yaml"), ("mine.yaml", "templates/a.md", "templates/b.md"),
                          "mine/mine.yaml")
    lines = created_lines(done, "cli")
    assert lines[:3] == ["wrote mine/, a copy of cli named mine, based_on: cli", "  mine.yaml",
                         "  templates/ (2 files)"]
    assert '  profile = "mine/mine.yaml"' in lines


def explained(*needs: Need) -> KeyExplained:
    return KeyExplained("parts.names", "parts.<part>", "how classes are named", "a pattern", False, True, ("names",),
                        "", (), (), needs, "Toy")


def test_a_key_says_the_facts_its_check_reads_and_how_the_language_supplies_them():
    exact = Need("class", "the classes", "exact")
    assert key_lines(explained(exact))[6] == (
        "  needs: class: the facts of the source its check reads, which Toy supplies exactly")
    partly, absent = Need("class", "the classes", "partial", "nested ones are not read"), Need("call", "calls", "absent")
    assert key_lines(explained(partly, absent))[6:8] == [
        "  needs: class, call: the facts of the source its check reads; Toy supplies class partly (nested",
        "    ones are not read), not call"]
    assert json.loads(key_document(explained(partly)))["needs"] == [
        {"fact": "class", "meaning": "the classes", "grade": "partial", "note": "nested ones are not read"}]
