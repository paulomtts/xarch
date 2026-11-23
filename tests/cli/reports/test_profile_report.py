"""How `xarch profile` shows what it found, on hand-made results: a key the format lacks, and a copy just written."""
import json
from dataclasses import replace
from pathlib import Path

import pytest

from xarch.cli.reports.profile_report import (
    check_document,
    check_lines,
    created_lines,
    key_document,
    key_lines,
    new_taken,
    overview_lines,
    unknown_document,
    unknown_message,
)
from xarch.modules.rules.contract import ChecksHeld, Loosened, ProfileHeld, ProfileUnloaded, Resemblance, Reviewed
from xarch.modules.spec.contract import (
    FilesTaken,
    FormatExplained,
    KeyExplained,
    Need,
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
        "ok": False, "error": unknown_message(found), "key": "tire", "nearest": ["tier", "tiers"], "words": [],
        "retired": None}


def test_an_unknown_key_near_words_of_a_check_keeps_the_keys_and_the_words_apart_in_json():
    found = UnknownKey("public", ("name",))
    assert json.loads(unknown_document(found, ("filters.public",))) == {
        "ok": False, "error": "no key `public` in the format: the nearest are name; of the words of a check, "
                              "filters.public", "key": "public", "nearest": ["name"], "words": ["filters.public"],
        "retired": None}


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


READS_LESS = "holds reads no top-level functions: the language Toy does not supply function.top_level"


def test_a_fact_a_key_reads_only_when_supplied_is_said_absent_and_what_its_check_reads_less_on_a_line_of_its_own():
    absent = Need("function.top_level", "whether a function is at the top level")
    lines = key_lines(explained(absent, short=(Shortfall("parts.holds", "function.top_level", READS_LESS, True),)))
    assert lines[6:9] == [
        "  needs: function.top_level: the facts of the source its check reads; Toy supplies not",
        "    function.top_level", f"  {READS_LESS}"]


def test_a_key_another_command_reads_is_said_to_be_read_by_it_and_never_by_check():
    held = KeyExplained("review.never", "review", "the files review never sends", "a list of paths", False, False,
                        (), "review:\n  never: [a]", (), (), read_by="review")
    assert key_lines(held)[5] == ("  enforced: no: check never acts on it (written wrong, the profile is invalid for "
                                  "every command); only xarch review reads what it says")
    assert json.loads(key_document(held))["read_by"] == "review"
    shape = (Shown("docs", 0, "the docs", False, False), Shown("review", 0, "what review may send", False, False, "review"))
    rows = overview_lines(FormatExplained(shape, (Symbol("<word>", "a repeating folder"),), "name: n\n"))[4:6]
    assert [row.split()[:3] for row in rows] == [["docs", "optional", "documentary"], ["review", "optional", "review"]]


COUNTS = (("parts", 12, 15), ("part_keys", 72, 91), ("tiers", 21, 31), ("guards", 11, 11), ("profile", 9, 9))
"""The counts of xarch's own profile against cli."""
MATCH = ("  match: 80% with cli (based_on): 12 of 15 parts, 72 of 91 part keys, 21 of 31 tier entries, 11 of 11 guards, "
         "9 of 9 profile keys sit where both profiles have them")
"""The match line of a profile based on cli that matches it at 80%, with COUNTS."""


def based_on_cli(**changes) -> Resemblance:
    """A custom profile based on cli, matching it at 80% with COUNTS and nothing unpaired; the fields given replaced."""
    return replace(Resemblance(False, "cli", (), "based_on", 0.8, False, COUNTS), **changes)


AGAINST_WEB = based_on_cli(compared="web", chosen_by="against")
"""A custom profile compared with web because --against names it, matching it at 80% with COUNTS."""


def checked(resemblance: Resemblance) -> list[str]:
    """What `profile check` says of a valid profile that resembles the bundled ones as given, but its verdict."""
    return check_lines(ProfileHeld(Reviewed("mine.yaml", (), 1, resemblance), ChecksHeld((), 0)))[:-1]


def matched(resemblance: Resemblance) -> list[str]:
    """The lines `profile check` says of the match: those between the examples and the comparison."""
    return checked(resemblance)[4:-1]


@pytest.mark.parametrize("resemblance, words", [
    pytest.param(Resemblance(True), "bundled", id="a bundled profile"),
    pytest.param(based_on_cli(), "custom; based_on: cli", id="a custom one names the profile it is based on"),
    pytest.param(based_on_cli(chosen_by="closest"), "custom; closest bundled: cli, match 80%",
                 id="a custom one names the bundled profile of highest match, with the match"),
    pytest.param(Resemblance(False), "custom; no bundled profile resembles it",
                 id="a custom one that resembles none says so"),
    pytest.param(replace(AGAINST_WEB, based_on="cli"), "custom; against web, given with --against; based_on: cli",
                 id="a custom one compared with the profile against names says so, then what it is based on"),
    pytest.param(AGAINST_WEB, "custom; against web, given with --against",
                 id="a custom one based on nothing compared with the profile against names says so"),
    pytest.param(replace(AGAINST_WEB, bundled=True), "bundled; against web, given with --against",
                 id="a bundled one compared with the profile against names says so"),
])
def test_profile_check_is_headed_with_where_the_profile_comes_from(resemblance, words):
    assert checked(resemblance)[0] == f"checking mine.yaml ({words})"


def test_the_match_is_said_with_its_counts_and_what_pairs_with_nothing_on_either_side_before_the_comparison():
    resemblance = based_on_cli(only_here=("part main", "part profile-values", "part reports", "tier wired"),
                               only_there=("tier rendering",))
    assert checked(resemblance)[4:] == [
        MATCH, "    only here: parts main, profile-values, reports; tier wired. only in cli: tier rendering",
        "  compared: no looser than cli"]


@pytest.mark.parametrize("only_here, only_there, said", [
    pytest.param((), ("part web", "tier rendering"), ["    only in cli: part web; tier rendering"],
                 id="an empty side is left out"),
    pytest.param(("tier wired",), (), ["    only here: tier wired"], id="an empty group is left out"),
    pytest.param((), (), [], id="with both sides empty the line is left out"),
    pytest.param(tuple(f"part p{n}" for n in range(7)), (), ["    only here: parts p0, p1, p2, p3, p4 and 2 more"],
                 id="past five names a group counts the rest"),
])
def test_what_pairs_with_nothing_is_said_by_side_and_by_group(only_here, only_there, said):
    assert matched(based_on_cli(only_here=only_here, only_there=only_there)) == [MATCH, *said]


def test_a_part_of_the_same_name_at_another_path_is_said_past_five_counting_the_rest():
    elsewhere = tuple(f"p{n}: modules/*/p{n} there" for n in range(7))
    assert matched(based_on_cli(elsewhere=elsewhere)) == [
        MATCH, "    same name, other path: p0: modules/*/p0 there, p1: modules/*/p1 there, p2: modules/*/p2 there, "
               "p3: modules/*/p3 there, p4: modules/*/p4 there and 2 more"]


@pytest.mark.parametrize("resemblance, said", [
    pytest.param(based_on_cli(compared="web", match=0.73, low=True),
                 "    low: 27% of what check reads under either profile has nothing to compare with in the other, so the "
                 "list below says little about how check would do under web",
                 id="by the share that has nothing to compare with"),
    pytest.param(based_on_cli(compared="web", match=0.75, low=True),
                 "    low: 25% of what check reads under either profile has nothing to compare with in the other, so the "
                 "list below says little about how check would do under web",
                 id="a match just below 75% that rounds to it is still low"),
    pytest.param(based_on_cli(compared="web", match=0.5, low=True, counts=(("parts", 0, 4), *COUNTS[1:])),
                 "    low: no part in common, so the list below says little about how check would do under web",
                 id="with no part in common"),
])
def test_a_low_match_says_why_the_comparison_says_little(resemblance, said):
    assert matched(resemblance)[-1] == said


def test_a_bundled_profile_of_higher_match_than_the_one_based_on_is_named_with_its_match():
    assert matched(based_on_cli(higher=("web", 0.88))) == [MATCH, "    web matches 88%"]


def test_nothing_of_a_match_is_said_when_nothing_is_compared():
    assert matched(Resemblance(True)) == matched(Resemblance(False)) == []


def test_the_json_of_profile_check_holds_every_field_of_the_profile_compared_with():
    resemblance = based_on_cli(looser=(Loosened("untested", "api", "", "api is newly marked untested (parts.api.untested)"),),
                               only_here=("part main", "tier wired"), only_there=("tier rendering",),
                               elsewhere=("store: src/*/store there",), higher=("web", 0.88))
    held = ProfileHeld(Reviewed("mine.yaml", (), 1, resemblance), ChecksHeld((), 0))
    assert json.loads(check_document(held))["compared_with"] == {
        "profile": "cli", "chosen_by": "based_on", "match": 0.8, "low": False,
        "counts": {"parts": [12, 15], "part_keys": [72, 91], "tiers": [21, 31], "guards": [11, 11], "profile": [9, 9]},
        "only_here": ["part main", "tier wired"], "only_there": ["tier rendering"],
        "elsewhere": ["store: src/*/store there"], "higher": {"profile": "web", "match": 0.88},
        "looser": [{"key": "untested", "part": "api", "what": "", "sentence": "api is newly marked untested (parts.api.untested)"}]}
    bundled = ProfileHeld(Reviewed("web", (), 1, Resemblance(True)), ChecksHeld((), 0))
    assert json.loads(check_document(bundled))["compared_with"] is None


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


NEW = (": nothing was written; `new` writes only new files, so pass `--out <folder>` to write somewhere else, or choose "
       "another name")


@pytest.mark.parametrize("taken, said", [
    pytest.param([Path("out/a.yaml")], "out/a.yaml already exists" + NEW, id="one file exists"),
    pytest.param([Path("a"), Path("b")], "a, b already exist" + NEW, id="two files exist"),
    pytest.param([Path(n) for n in "abcde"], "a, b, c and 2 more already exist" + NEW,
                 id="past three the rest are counted"),
])
def test_a_refusal_to_write_over_files_names_up_to_three_then_counts_the_rest(taken, said):
    assert new_taken(FilesTaken(tuple(taken))) == said


def test_a_profile_that_would_be_written_over_files_names_them_and_says_how_to_write_elsewhere():
    taken = FilesTaken((Path("old-v2/architecture.md"),))
    assert new_taken(taken) == (
        "old-v2/architecture.md already exists: nothing was written; `new` writes only new files, so pass "
        "`--out <folder>` to write somewhere else, or choose another name")


def test_the_problems_of_an_eval_of_the_profile_s_own_are_said_under_evals_not_checks():
    held = ProfileHeld(Reviewed("mine.yaml", (), 0, Resemblance(False, None, ())),
                       ChecksHeld((), 0, ("evals.rule.keep: no filter is named 'x'",), 1))
    lines = check_lines(held)
    assert lines[lines.index("  evals: 1 problem") + 1] == "    evals.rule.keep: no filter is named 'x'"
    assert not any(line.startswith("  checks:") for line in lines) and lines[-1] == "INVALID: 1 problem"
    assert json.loads(check_document(held))["problems"] == [{"check": "evals",
                                                              "message": "evals.rule.keep: no filter is named 'x'"}]


def test_an_address_xarch_retired_is_said_with_its_fixed_text_before_the_nearest_keys_and_in_json():
    found = UnknownKey("parts.tested_by", ("parts.untested",), "renamed in 0.3.0: write tier")
    assert unknown_message(found) == ("no key `parts.tested_by` in the format: renamed in 0.3.0: write tier; the nearest "
                                      "are parts.untested")
    assert unknown_message(found, ("filters.test",)) == (
        "no key `parts.tested_by` in the format: renamed in 0.3.0: write tier; the nearest are parts.untested; of the "
        "words of a check, filters.test")
    assert json.loads(unknown_document(found)) == {
        "ok": False, "error": unknown_message(found), "key": "parts.tested_by", "nearest": ["parts.untested"],
        "words": [], "retired": "renamed in 0.3.0: write tier"}


def test_a_profile_compared_with_the_one_against_names_says_so_in_its_match_and_a_bundled_one_is_compared_too():
    said = MATCH.replace("with cli (based_on)", "with web (--against)")
    assert matched(AGAINST_WEB) == [said]
    bundled = replace(AGAINST_WEB, bundled=True)
    assert matched(bundled) == [said]
    assert checked(bundled)[-1] == "  compared: no looser than web"
    compared = json.loads(check_document(ProfileHeld(Reviewed("cli", (), 1, bundled), ChecksHeld((), 0))))[
        "compared_with"]
    assert (compared["profile"], compared["chosen_by"], compared["higher"]) == ("web", "against", None)
