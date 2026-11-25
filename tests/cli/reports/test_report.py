"""How `xarch check` shows what it found, on hand-made violations and enforcement states: the text lines, the
enforcement section and the JSON document."""
import json
from dataclasses import replace
from pathlib import Path

import pytest

from xarch.cli.reports.report import LABELS, check_lines, json_document
from xarch.kernel.violations import Violation
from xarch.modules.rules.contract import (
    SECTIONS,
    AppChecked,
    ApproximateView,
    At,
    EnforcementView,
    ExcludedView,
    FindingView,
    KnownName,
    OwnCheckView,
    Translation,
    Unresolved,
    UnresolvedView,
    Weak,
)
from xarch.modules.spec.contract import Loosened, Origin

A = Violation("app/a.py", 3, "a problem", "may-import", "do this")
B = Violation("app/a.py", 7, "another", "may-import", "do that")
C = Violation("app/b.py", 1, "a third", "tiers", "do the other")
WHOLE = Violation("app/a.py", 0, "missing x/", "structure", "create x/")
WEB = ["enforcement", "  profile:     web (bundled)"]
"""The enforcement section of a check under the bundled web profile with nothing to report."""
OK = ["OK: no violations", *WEB]
"""What a check under the bundled web profile shows when it finds nothing at all."""


def lines(found=(), hints=None, state: EnforcementView = EnforcementView(), origin: Origin = Origin("web"),
          strict: bool = False) -> list[str]:
    """What `xarch check` shows as text of a check that found found, with hints, and state as its enforcement."""
    return check_lines(origin, AppChecked(tuple(found), state, hints or {}, False), strict, Path("/src"))


@pytest.mark.parametrize("found, hints, shown", [
    pytest.param([], {}, OK, id="no violation is said so"),
    pytest.param([A, B, C], {}, [
        "app/a.py:3: a problem", "    fix: do this", "app/a.py:7: another", "    fix: do that",
        "app/b.py:1: a third", "    fix: do the other", "3 violation(s) in 2 file(s)", *WEB],
        id="each finding is followed by its fix, and the summary counts the violations and their files"),
    pytest.param([WHOLE], {}, ["app/a.py: missing x/", "    fix: create x/", "1 violation(s) in 1 file(s)", *WEB],
                 id="a finding of a whole file shows no line"),
    pytest.param([A, B], {"may-import": "see docs/rules.md"}, [
        "app/a.py:3: a problem", "    fix: do this", "    hint: see docs/rules.md",
        "app/a.py:7: another", "    fix: do that", "    hint: see docs/rules.md", "2 violation(s) in 1 file(s)", *WEB],
        id="the hint of the rule follows the fix of each of its findings"),
    pytest.param([A, C], {"tiers": "ask the owner"}, [
        "app/a.py:3: a problem", "    fix: do this", "app/b.py:1: a third", "    fix: do the other",
        "    hint: ask the owner", "2 violation(s) in 2 file(s)", *WEB],
        id="a finding of another rule gets no hint"),
    pytest.param([A], {"stand-ins": "unused"}, ["app/a.py:3: a problem", "    fix: do this",
                                                 "1 violation(s) in 1 file(s)", *WEB],
                 id="a hint for a rule that found nothing is not shown"),
])
def test_the_text_of_a_check_is_its_violations_then_its_enforcement_section(found, hints, shown):
    assert lines(found, hints) == shown


SKIPS = tuple(At("tests/test_a.py", line) for line in range(1, 8))


@pytest.mark.parametrize("skipped, line", [
    pytest.param(SKIPS[:5], "  skipped:     5 skips (" + ", ".join(f"tests/test_a.py:{n}" for n in range(1, 6)) + ")",
                 id="up to five skips are each named"),
    pytest.param(SKIPS, "  skipped:     7 skips (" + ", ".join(f"tests/test_a.py:{n}" for n in range(1, 6))
                 + " and 2 more)", id="past five the rest are counted"),
    pytest.param(SKIPS[:1], "  skipped:     1 skip (tests/test_a.py:1)", id="one skip is singular"),
])
def test_a_line_of_skips_names_five_places_then_counts_the_rest(skipped, line):
    assert lines(state=EnforcementView(skipped=skipped)) == [*OK, line]


def test_the_json_document_gives_each_violation_its_fix_and_the_hint_of_its_rule_as_keys_of_their_own():
    checked = AppChecked((A, C), EnforcementView(), {"may-import": "see the docs"}, False)
    document = json.loads(json_document("web", Origin("web"), checked, False))
    assert document["violations"] == [
        {"rule": "may-import", "file": "app/a.py", "line": 3, "message": "a problem", "fix": "do this",
         "hint": "see the docs"},
        {"rule": "tiers", "file": "app/b.py", "line": 1, "message": "a third", "fix": "do the other", "hint": None}]


def test_the_json_document_holds_the_violations_in_the_order_the_check_gives_them_and_both_lists_of_guards_off():
    origin = Origin("my.yaml", False, "web", ("closed-tree", "no-comments"), ("closed-tree",))
    document = json.loads(json_document("my.yaml", origin, AppChecked((C, A), EnforcementView(), {}, False), False))
    assert ([v["line"] for v in document["violations"]], document["enforcement"]["profile"]["guards_off"],
            document["enforcement"]["profile"]["baseline_off"]) == ([1, 3], ["closed-tree", "no-comments"],
                                                                    ["closed-tree"])


def test_an_excluded_folder_is_named_with_its_reason_after_the_ungoverned_files():
    state = EnforcementView(("app/stray.py",), ("app/stray.py",), excluded=(ExcludedView("app/examples", "shipped as data"),
                                                                  ExcludedView("app/kernel/legacy", "copied code")),
                            language="Pascal")
    assert lines(state=state) == [
        *OK, "  ungoverned:  1 Pascal file outside every part (app/stray.py)",
        "  excluded:    app/examples/ (shipped as data)",
        "  excluded:    app/kernel/legacy/ (copied code)"]


def test_the_json_document_lists_every_excluded_folder_with_its_reason():
    state = EnforcementView(excluded=(ExcludedView("app/examples", "shipped as data"),))
    document = json.loads(json_document("web", Origin("web"), AppChecked((), state, {}, True), False))
    assert document["enforcement"]["excluded"] == [{"folder": "app/examples", "reason": "shipped as data"}]


PASS = Weak("pass-through", "app/s.py", 4, "S.get only passes its arguments on to self.repo.get", "use self.repo.get")
OLD = Weak("stand-ins", "tests/fakes/r.py", 1, "FakeR does not define get, which R declares")


def test_a_weak_check_with_a_fix_shows_it_under_its_line_and_the_hint_of_its_rule_after_it():
    state = EnforcementView(weak=(OLD, PASS))
    assert lines(hints={"pass-through": "see the ADR"}, state=state) == [
        *OK, "  weak:        tests/fakes/r.py:1: FakeR does not define get, which R declares",
        "  weak:        app/s.py:4: S.get only passes its arguments on to self.repo.get",
        "      fix: use self.repo.get",
        "      hint: see the ADR"]
    assert lines(state=state) == [
        *OK, "  weak:        tests/fakes/r.py:1: FakeR does not define get, which R declares",
        "  weak:        app/s.py:4: S.get only passes its arguments on to self.repo.get", "      fix: use self.repo.get"]


def test_the_json_weak_items_hold_their_fix_or_null():
    state = EnforcementView(weak=(OLD, PASS))
    document = json.loads(json_document("web", Origin("web"), AppChecked((), state, {}, True), False))
    assert document["enforcement"]["weak"] == [
        {"rule": "stand-ins", "file": "tests/fakes/r.py", "line": 1,
         "message": "FakeR does not define get, which R declares", "fix": None},
        {"rule": "pass-through", "file": "app/s.py", "line": 4,
         "message": "S.get only passes its arguments on to self.repo.get", "fix": "use self.repo.get"}]


def test_ungoverned_files_are_source_files_when_the_language_is_not_named():
    state = EnforcementView(("app/a.src", "app/b.src"), ("app/a.src", "app/b.src"))
    assert lines(state=state) == [*OK, "  ungoverned:  2 source files outside every part (app/a.src, app/b.src)"]


APPROXIMATE = ApproximateView("parts.services.names", "class", "a class defined in a branch is not read",
                              "parts.services.names reads class only partly: a class defined in a branch is not read")


def test_a_key_read_approximately_has_a_line_of_its_own_and_is_an_item_of_the_json_document():
    state = EnforcementView(approximate=(APPROXIMATE,))
    assert lines(state=state) == [
        *OK, "  approximate: parts.services.names reads class only partly: a class defined in a branch is not read"]
    document = json.loads(json_document("web", Origin("web"), AppChecked((), state, {}, True), False))
    assert document["enforcement"]["approximate"] == [
        {"key": "parts.services.names", "fact": "class", "note": "a class defined in a branch is not read"}]


def test_a_check_of_the_profile_s_own_is_listed_with_what_it_read_and_one_that_read_nothing_says_so():
    state = EnforcementView(checks=(
        OwnCheckView("store-names", 2, "checks.store-names read 2 facts"),
        OwnCheckView("no-todo", 0, "checks.no-todo reads nothing")))
    assert lines(state=state, origin=Origin("mine.yaml")) == [
        "OK: no violations", "enforcement", "  profile:     mine.yaml (bundled)",
        "  own check:   checks.store-names read 2 facts", "  reads nothing: checks.no-todo reads nothing"]
    document = json.loads(json_document("mine.yaml", Origin("mine.yaml"), AppChecked((), state, {}, True), False))
    assert document["enforcement"]["checks"] == [
        {"id": "store-names", "read": 2, "said": "checks.store-names read 2 facts"},
        {"id": "no-todo", "read": 0, "said": "checks.no-todo reads nothing"}]


def test_a_profile_that_writes_no_check_of_its_own_has_no_checks_in_its_json_document():
    document = json.loads(json_document("web", Origin("web"), AppChecked((), EnforcementView(), {}, True), False))
    assert "checks" not in document["enforcement"]


def test_a_part_without_the_litmus_its_base_gives_it_is_said_under_the_profile_and_again_under_strict():
    said = "cli has no litmus, though the profile it is compared with gives it one (parts.cli.litmus)"
    origin = Origin("mine.yaml", False, "cli", looser=(Loosened("litmus", "cli", "", said),), chosen_by="based_on",
                    match=0.8, anchor="cli")
    assert lines(state=EnforcementView(strict=(FindingView("litmus", said),)), origin=origin, strict=True) == [
        "OK: no violations", "enforcement", "  profile:     mine.yaml (custom; compared with cli, based_on; match 80%)",
        f"    litmus:      {said}", "strict:      1 finding fails the check", f"    litmus: {said}"]


def test_every_section_of_the_enforcement_has_a_label():
    assert set(LABELS) == set(SECTIONS)


def test_a_pair_no_twins_accepts_as_a_translation_has_a_line_of_its_own_and_is_an_item_of_the_json_document():
    state = EnforcementView(translated=(Translation("app/adapters/spec.py", 7, "SpecProfiles.known", "Known", "KnownProfiles"),))
    assert lines(state=state) == [*OK, "  translated:  app/adapters/spec.py:7: SpecProfiles.known names Known, which its "
                                       "file builds, and KnownProfiles: no-twins accepts the pair as a translation "
                                       "(guards.no-twins.translated)"]
    document = json.loads(json_document("web", Origin("web"), AppChecked((), state, {}, True), False))
    assert document["enforcement"]["translated"] == [{"file": "app/adapters/spec.py", "line": 7, "function": "SpecProfiles.known",
                                                      "built": "Known", "other": "KnownProfiles"}]


def test_a_public_name_the_profile_accepts_as_only_the_tests_has_a_line_of_its_own_and_is_an_item_of_the_json_document():
    state = EnforcementView(excluded=(ExcludedView("app/examples", "shipped as data"),),
                            known=(KnownName("app/wiring.py", 12, "build"), KnownName("app/rules.py", 3, "Rule")))
    said = "is public, a test names it and no other file of the app does, which the profile accepts (guards.dead-code.known)"
    assert lines(state=state) == [*OK, "  excluded:    app/examples/ (shipped as data)",
                                  f"  known:       app/wiring.py:12: build {said}", f"  known:       app/rules.py:3: Rule {said}"]
    document = json.loads(json_document("web", Origin("web"), AppChecked((), state, {}, True), False))
    assert document["enforcement"]["known"] == [{"file": "app/wiring.py", "line": 12, "name": "build"},
                                                {"file": "app/rules.py", "line": 3, "name": "Rule"}]


def test_a_guard_switched_on_by_a_key_of_a_part_is_named_with_that_key_where_it_is_left_off():
    origin = Origin("mine.yaml", False, None, ("package-only", "no-comments"), ())
    state = EnforcementView(strict=(FindingView("guards_off", "package-only"), FindingView("guards_off", "no-comments")))
    assert lines(state=state, origin=origin, strict=True) == [
        "OK: no violations", "enforcement", "  profile:     mine.yaml (custom; no bundled profile resembles it)",
        "    guards off:  package-only (parts.<part>.package_only), no-comments", "strict:      2 findings fail the check",
        "    guards off: package-only (parts.<part>.package_only)", "    guards off: no-comments"]


COUNTS = (("parts", 4, 5), ("part_keys", 7, 7), ("tiers", 0, 0), ("guards", 1, 1), ("profile", 1, 1))
"""The counts of a profile with one part of its own besides four it shares."""


def closest(location: str, **changes) -> Origin:
    """A custom profile at location compared with web, the bundled profile of highest match, at 81% with COUNTS; the
    fields given replaced."""
    return replace(Origin(location, False, "web", chosen_by="closest", match=0.81, counts=COUNTS), **changes)


def test_a_profile_compared_with_the_one_against_names_says_so_on_its_profile_line_bundled_or_custom():
    bundled = Origin("web", True, "cli", chosen_by="against", match=0.89, counts=COUNTS)
    assert lines(origin=bundled)[2:] == ["  profile:     web (bundled; compared with cli, --against; match 89%)"]
    custom = closest("/src/mine.yaml", chosen_by="against", match=0.73, low=True)
    assert lines(origin=custom)[2:] == [
        "  profile:     mine.yaml (custom; compared with web, --against; match 73%)",
        "    match:       73%, low: 27% of what check reads under either profile has nothing to compare with in the "
        "other, so the list below says little about how check would do under web"]
    profile = json.loads(json_document("web", bundled, AppChecked((), EnforcementView(), {}, True), False))[
        "enforcement"]["profile"]
    assert (profile["bundled"], profile["compared_with"]["profile"], profile["compared_with"]["chosen_by"]) == (
        True, "cli", "against")


def test_a_profile_file_below_the_working_folder_is_named_from_it():
    assert lines(origin=closest("/src/arch/mine.yaml"))[:3] == [
        "OK: no violations", "enforcement", "  profile:     arch/mine.yaml (custom; compared with web, closest; match 81%)"]
    assert lines(origin=closest("/elsewhere/mine.yaml"))[2] == (
        "  profile:     /elsewhere/mine.yaml (custom; compared with web, closest; match 81%)")


def test_a_low_match_is_said_under_the_profile_line_with_why_and_one_that_is_not_low_only_in_it():
    low = closest("/src/mine.yaml", match=0.73, low=True, guards_off=("no-comments",))
    assert lines(origin=low)[2:5] == [
        "  profile:     mine.yaml (custom; compared with web, closest; match 73%)",
        "    match:       73%, low: 27% of what check reads under either profile has nothing to compare with in the "
        "other, so the list below says little about how check would do under web",
        "    guards off:  no-comments"]
    assert lines(origin=closest("/src/mine.yaml"))[2:] == [
        "  profile:     mine.yaml (custom; compared with web, closest; match 81%)"]


def test_the_json_document_holds_the_profile_compared_with_under_compared_with_and_no_closest_key():
    origin = closest("mine.yaml", only_here=("part jobs",))
    profile = json.loads(json_document("mine.yaml", origin, AppChecked((), EnforcementView(), {}, True), False))[
        "enforcement"]["profile"]
    assert list(profile) == ["location", "bundled", "compared_with", "guards_off", "baseline_off", "looser"]
    assert profile["compared_with"] == {
        "profile": "web", "chosen_by": "closest", "match": 0.81, "low": False,
        "counts": {"parts": [4, 5], "part_keys": [7, 7], "tiers": [0, 0], "guards": [1, 1], "profile": [1, 1]},
        "only_here": ["part jobs"], "only_there": [], "elsewhere": [], "higher": None, "anchor": None, "looser": []}
    bundled = json.loads(json_document("web", Origin("web"), AppChecked((), EnforcementView(), {}, True), False))
    assert bundled["enforcement"]["profile"]["compared_with"] is None
    assert "closest" not in bundled["enforcement"]["profile"]


LOST = UnresolvedView(Unresolved("app/domain/services.py", 3, ".ordr"),
                      'app/domain/services.py:3: import ".ordr" names no file of the app')
GONE = UnresolvedView(Unresolved("tests/test_a.py", 1, "..gone"),
                      'tests/test_a.py:1: import "..gone" names no file of the app')


def test_each_import_the_reader_could_not_follow_has_a_line_of_its_own_after_the_dynamic_imports_and_before_weak():
    state = EnforcementView(dynamic=(At("app/kernel/dyn.py", 3),), weak=(OLD,), unresolved=(LOST, GONE))
    assert lines(state=state) == [
        *OK, "  dynamic:     1 dynamic import (app/kernel/dyn.py:3)",
        '  unresolved:  app/domain/services.py:3: import ".ordr" names no file of the app',
        '  unresolved:  tests/test_a.py:1: import "..gone" names no file of the app',
        "  weak:        tests/fakes/r.py:1: FakeR does not define get, which R declares"]
    assert lines(state=EnforcementView()) == OK


def test_every_import_the_reader_could_not_follow_has_its_line_however_many_there_are():
    many = tuple(UnresolvedView(Unresolved("app/a.py", n, ".x"), f'app/a.py:{n}: import ".x" names no file of the app')
                 for n in range(1, 8))
    assert lines(state=EnforcementView(unresolved=many)) == [
        *OK, *(f'  unresolved:  app/a.py:{n}: import ".x" names no file of the app' for n in range(1, 8))]


def test_the_json_document_lists_each_import_the_reader_could_not_follow_and_none_as_an_empty_list():
    state = EnforcementView(unresolved=(LOST, GONE))
    document = json.loads(json_document("web", Origin("web"), AppChecked((), state, {}, True), False))
    assert document["enforcement"]["unresolved"] == [
        {"file": "app/domain/services.py", "line": 3, "written": ".ordr"},
        {"file": "tests/test_a.py", "line": 1, "written": "..gone"}]
    keys = list(document["enforcement"])
    assert keys.index("unresolved") == keys.index("dynamic") + 1
    empty = json.loads(json_document("web", Origin("web"), AppChecked((), EnforcementView(), {}, True), False))
    assert empty["enforcement"]["unresolved"] == []


def test_an_import_the_reader_could_not_follow_is_listed_under_strict_by_its_sentence():
    state = EnforcementView(strict=(FindingView("unresolved", LOST.sentence),), unresolved=(LOST,))
    assert lines(state=state, strict=True) == [
        *OK, f"  unresolved:  {LOST.sentence}", "strict:      1 finding fails the check",
        f"    unresolved: {LOST.sentence}"]


def test_a_profile_based_on_a_profile_file_says_the_bundled_profile_strict_rests_on_on_its_profile_line():
    based = Origin("/src/mine.yaml", False, "../team.yaml", chosen_by="based_on", match=0.92, counts=COUNTS,
                   anchor="cli")
    assert lines(origin=based)[2:] == [
        "  profile:     mine.yaml (custom; compared with ../team.yaml, based_on; match 92%; --strict rests on cli)"]
    assert lines(origin=replace(based, anchor=None))[2] == (
        "  profile:     mine.yaml (custom; compared with ../team.yaml, based_on; match 92%; --strict rests on no "
        "bundled profile)")
    assert lines(origin=replace(based, compared="cli"))[2] == (
        "  profile:     mine.yaml (custom; compared with cli, based_on; match 92%)")
    assert lines(origin=closest("/src/mine.yaml", anchor="web"))[2] == (
        "  profile:     mine.yaml (custom; compared with web, closest; match 81%)")
    against = replace(based, compared="web", chosen_by="against", anchor=None, based_on="../team.yaml")
    assert lines(origin=against)[2] == "  profile:     mine.yaml (custom; compared with web, --against; match 92%)"
    profile = json.loads(json_document("mine.yaml", based, AppChecked((), EnforcementView(), {}, True), False))[
        "enforcement"]["profile"]
    assert profile["compared_with"]["anchor"] == "cli"
    assert json.loads(json_document("mine.yaml", against, AppChecked((), EnforcementView(), {}, True), False))[
        "enforcement"]["profile"]["compared_with"]["anchor"] is None
