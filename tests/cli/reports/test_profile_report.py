"""How `xarch profile` shows what it found, on hand-made results: a key the format lacks, and a copy just written."""
import json
from pathlib import Path

import pytest

from xarch.cli.reports.profile_report import (
    check_lines,
    created_lines,
    key_document,
    key_lines,
    origin_words,
    unknown_document,
    unknown_message,
)
from xarch.kernel.capabilities import EXACT, Supply
from xarch.modules.spec.contract import KeyExplained, Need, Origin, ProfileChecked, ProfileCreated, UnknownKey


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
                        "", (), (), needs, "Toy", True)


def test_a_key_says_the_facts_its_check_reads_and_how_the_language_supplies_them():
    exact = Need("class", "the classes", Supply("class", EXACT))
    assert key_lines(explained(exact))[6] == (
        "  needs: class: the facts of the source its check reads, which Toy supplies exactly")
    partly = Need("class", "the classes", Supply("class", "partial", "nested ones are not read"))
    absent = Need("call", "calls")
    assert key_lines(explained(partly, absent))[6:8] == [
        "  needs: class, call: the facts of the source its check reads; Toy supplies class partly (nested",
        "    ones are not read), not call"]
    assert json.loads(key_document(explained(partly)))["needs"] == [
        {"fact": "class", "meaning": "the classes", "grade": "partial", "note": "nested ones are not read"}]


@pytest.mark.parametrize("origin, words", [
    pytest.param(Origin("web"), "bundled", id="a bundled profile"),
    pytest.param(Origin("mine.yaml", False, "web"), "custom; closest bundled: web",
                 id="a custom one names the bundled profile closest to it"),
    pytest.param(Origin("mine.yaml", False), "custom; no bundled profile resembles it",
                 id="a custom one that resembles none says so"),
])
def test_where_a_profile_comes_from_is_said_the_same_by_profile_check_and_by_check(origin, words):
    assert (origin_words(origin), check_lines(ProfileChecked(origin.location, (), 1, origin))[0]) == (
        words, f"checking {origin.location} ({words})")


def test_a_profile_that_does_not_load_is_said_to_be_custom_and_nothing_more():
    assert check_lines(ProfileChecked("mine.yaml", (), 0, None))[0] == "checking mine.yaml (custom)"
