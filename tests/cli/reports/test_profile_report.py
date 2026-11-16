"""How `xarch profile` shows what it found, on hand-made results: a key the format lacks, and a copy just written."""
import json
from pathlib import Path

import pytest

from xarch.cli.reports.profile_report import (
    check_document,
    check_lines,
    created_lines,
    key_document,
    key_lines,
    migrate_taken,
    new_taken,
    origin_words,
    overview_lines,
    unknown_document,
    unknown_message,
)
from xarch.modules.rules.contract import ChecksHeld, ProfileHeld, ProfileUnloaded, Resemblance, Reviewed
from xarch.modules.spec.contract import (
    FilesTaken,
    FormatExplained,
    KeyExplained,
    Need,
    Origin,
    ProfileCreated,
    Shortfall,
    Shown,
    Supply,
    Symbol,
    UnknownKey,
)


def test_an_unknown_key_is_said_with_the_nearest_ones_in_text_and_in_json():
    found = UnknownKey("tire", ("tier", "tiers"))
    assert unknown_message(found) == "no key `tire` in the format: the nearest are tier, tiers"
    assert json.loads(unknown_document(found)) == {
        "ok": False, "error": unknown_message(found), "key": "tire", "nearest": ["tier", "tiers"], "words": []}


def test_an_unknown_key_near_words_of_a_check_keeps_the_keys_and_the_words_apart_in_json():
    found = UnknownKey("public", ("name",))
    assert json.loads(unknown_document(found, ("filters.public",))) == {
        "ok": False, "error": "no key `public` in the format: the nearest are name; of the words of a check, "
                              "filters.public", "key": "public", "nearest": ["name"], "words": ["filters.public"]}


def test_a_new_profile_says_what_was_written_and_how_to_put_it_in_force_each_path_from_the_working_folder():
    done = ProfileCreated(Path("/work/mine"), Path("/work/mine/mine.yaml"),
                          ("mine.yaml", "templates/a.md", "templates/b.md"), "mine/mine.yaml")
    assert created_lines(done, "cli", Path("/work")) == [
        "wrote mine/, a copy of cli named mine, based_on: cli", "  mine.yaml", "  templates/ (2 files)",
        "to put it in force, add this under [tool.xarch] in pyproject.toml (`new` never edits it):",
        '  profile = "mine/mine.yaml"', "next:", "  edit mine/mine.yaml",
        "  xarch profile explain                 # the format, key by key", "  xarch profile check mine/mine.yaml"]


def explained(*needs: Need, short: tuple[Shortfall, ...] = ()) -> KeyExplained:
    return KeyExplained("parts.names", "parts.<part>", "how classes are named", "a pattern", False, True, ("names",),
                        "", (), (), needs, "Toy", True, "names", "part", short)


def test_a_key_says_the_facts_its_check_reads_and_how_the_language_supplies_them():
    exact = Need("class", "the classes", Supply("class", "exact"))
    assert key_lines(explained(exact))[6] == (
        "  needs: class: the facts of the source its check reads, which Toy supplies exactly")
    partly = Need("class", "the classes", Supply("class", "partial", "nested ones are not read"))
    absent = Need("call", "calls")
    short = (Shortfall("parts.names", "class", "nested ones are not read"), Shortfall("parts.names", "call", None))
    assert key_lines(explained(partly, absent, short=short))[6:8] == [
        "  needs: class, call: the facts of the source its check reads; Toy supplies class partly (nested",
        "    ones are not read), not call"]
    assert json.loads(key_document(explained(partly)))["needs"] == [
        {"fact": "class", "meaning": "the classes", "grade": "partial", "note": "nested ones are not read"}]


def test_a_key_another_command_reads_is_said_to_be_read_by_it_and_never_by_check():
    held = KeyExplained("review.never", "review", "the files review never sends", "a list of paths", False, False,
                        (), "review:\n  never: [a]", (), (), read_by="review")
    assert key_lines(held)[5] == "  enforced: no: check never reads it; xarch review does, for what it sends"
    assert json.loads(key_document(held))["read_by"] == "review"
    shape = (Shown("docs", 0, "the docs", False, False), Shown("review", 0, "what review may send", False, False, "review"))
    rows = overview_lines(FormatExplained(2, shape, (Symbol("<word>", "a repeating folder"),), "xarch: 2\n"))[4:6]
    assert [row.split()[:3] for row in rows] == [["docs", "optional", "documentary"], ["review", "optional", "review"]]


@pytest.mark.parametrize("origin, resemblance, words", [
    pytest.param(Origin("web"), Resemblance(True), "bundled", id="a bundled profile"),
    pytest.param(Origin("mine.yaml", False, "web"), Resemblance(False, "web"), "custom; closest bundled: web",
                 id="a custom one names the bundled profile closest to it"),
    pytest.param(Origin("mine.yaml", False), Resemblance(False), "custom; no bundled profile resembles it",
                 id="a custom one that resembles none says so"),
])
def test_where_a_profile_comes_from_is_said_the_same_by_profile_check_and_by_check(origin, resemblance, words):
    held = ProfileHeld(Reviewed(origin.location, (), 1, resemblance), ChecksHeld((), 0))
    assert (origin_words(origin), check_lines(held)[0]) == (words, f"checking {origin.location} ({words})")


def test_a_profile_that_does_not_load_is_said_to_be_custom_and_nothing_more():
    assert check_lines(ProfileUnloaded("mine.yaml", ("mine.yaml: unknown key 'colour'",)))[0] == (
        "checking mine.yaml (custom)")


def test_the_json_of_a_profile_that_does_not_load_counts_neither_its_files_nor_its_checks():
    document = json.loads(check_document(ProfileUnloaded("mine.yaml", ("mine.yaml: unknown key 'colour'",))))
    assert document == {"ok": False, "profile": "mine.yaml",
                        "problems": [{"check": "load", "message": "mine.yaml: unknown key 'colour'"}],
                        "files": None, "checks": None, "compared_with": None}


@pytest.mark.parametrize("files, said", [
    pytest.param(0, "  files: it points to none", id="none"),
    pytest.param(1, "  files: the one it points to is present", id="one"),
    pytest.param(3, "  files: all 3 it points to are present", id="several"),
])
def test_the_files_a_profile_points_to_are_said_as_many_as_they_are(files, said):
    held = ProfileHeld(Reviewed("web", (), files, Resemblance(True)), ChecksHeld((), 0))
    assert check_lines(held)[2] == said


MIGRATE = ": migrate writes only new files; pass `--out <folder>` to write somewhere else"


@pytest.mark.parametrize("taken, said", [
    pytest.param([Path("out/a.yaml")], "out/a.yaml already exists" + MIGRATE, id="one file exists"),
    pytest.param([Path("a"), Path("b")], "a, b already exist" + MIGRATE, id="two files exist"),
    pytest.param([Path(n) for n in "abcde"], "a, b, c and 2 more already exist" + MIGRATE,
                 id="past three the rest are counted"),
])
def test_a_refusal_to_write_over_files_names_up_to_three_then_counts_the_rest(taken, said):
    assert migrate_taken(FilesTaken(tuple(taken))) == said


def test_a_profile_that_would_be_written_over_files_names_them_and_says_how_to_write_elsewhere():
    taken = FilesTaken((Path("old-v2/architecture.md"),))
    assert (migrate_taken(taken), new_taken(taken)) == (
        "old-v2/architecture.md already exists: migrate writes only new files; pass `--out <folder>` to write "
        "somewhere else",
        "old-v2/architecture.md already exists: nothing was written; `new` writes only new files, so pass "
        "`--out <folder>` to write somewhere else, or choose another name")
