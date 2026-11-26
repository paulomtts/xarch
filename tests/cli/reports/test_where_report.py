"""How `xarch where` shows its answer, on hand-made answers: the labelled lines and the JSON document."""
import json
from dataclasses import replace

from xarch.cli.reports.where_report import where_document, where_lines
from xarch.modules.rules.contract import ALL, InPart, InTests, Litmus, PartShown, TierInfoView, Ungoverned, Untested

PART = InPart("app/cli/app.py", True, PartShown("cli", "cli", role="the commands", litmus="Is it a command?"), (),
              "contract", ("typer",), (), Untested("a shim"))


def test_a_place_in_a_part_is_shown_with_its_part_role_and_what_it_may_import():
    assert where_lines(PART) == [
        "path:           app/cli/app.py (exists)", "part:           cli", "role:           the commands",
        "litmus:         Is it a command?", "may import:     contract", "libraries:      typer",
        "tested by:      nothing: a shim"]


def test_a_part_with_no_litmus_says_so():
    bare = InPart("app/cli/app.py", True, PartShown("cli", "cli", role="the commands"), (), "contract", ("typer",), (),
                  Untested("a shim"))
    assert where_lines(bare)[3] == "litmus:         none"


def test_a_place_in_no_part_is_shown_as_such_and_its_document_leaves_what_does_not_apply_null():
    nowhere = Ungoverned("app/odd.py", False, (), None, "")
    assert where_lines(nowhere) == ["path:           app/odd.py (new)", "part:           none: ungoverned"]
    document = json.loads(where_document("custom", nowhere))
    assert (document["ok"], document["profile"], document["kind"], document["part"], document["test"]) == (
        True, "custom", "ungoverned", None, None)


def test_the_names_a_part_never_uses_are_a_line_of_their_own_and_the_field_never_uses():
    held = replace(PART, uses_never=("socket", "builtins.open"))
    assert where_lines(held)[6] == "never uses:     socket, builtins.open"
    document = json.loads(where_document("custom", held))
    assert document["never_uses"] == ["socket", "builtins.open"] and "forbidden" not in document


def test_a_test_held_to_the_list_of_the_part_it_mirrors_shows_it_under_the_same_label_and_field():
    test = InTests("tests/cli/test_app.py", True, PART.part, (), "contract", (), ("socket",), None, False, "", "", "")
    assert "never uses:     socket" in where_lines(test)
    document = json.loads(where_document("custom", test))
    assert document["never_uses"] == ["socket"] and "forbidden" not in document


def test_an_answer_that_is_no_part_gives_never_uses_empty():
    document = json.loads(where_document("custom", Ungoverned("app/odd.py", False, (), None, "")))
    assert document["never_uses"] == [] and "forbidden" not in document


TIER = TierInfoView("unit", "a rule", "nothing", "Does it decide?")


def test_a_test_with_shared_test_code_names_it_on_its_test_code_line_and_in_its_document():
    test = InTests("tests/unit/test_app.py", True, None, (), "", (), (), TIER, False, "", "tests/unit/", "",
                   ("tests/support/", "tests/helpers.py"))
    assert "test code:      from tests/unit/ and the shared tests/support/, tests/helpers.py only" in where_lines(test)
    assert json.loads(where_document("custom", test))["test"]["shared"] == ["tests/support/", "tests/helpers.py"]


def test_a_test_with_no_shared_test_code_is_shown_as_before():
    test = InTests("tests/unit/test_app.py", True, None, (), "", (), (), TIER, False, "", "tests/unit/", "")
    assert "test code:      from tests/unit/ only" in where_lines(test)
    assert "shared" not in json.loads(where_document("custom", test))["test"]


LISTED = (Litmus("Does it parse\nthe arguments?", "1"), Litmus("Does it print?", "print"),
          Litmus("Is it thin?", "thin", ALL))


def test_a_litmus_list_is_said_on_its_line_then_one_line_per_entry_and_listed_in_the_document():
    listed = replace(PART, part=replace(PART.part, litmus="", litmus_list=LISTED))
    assert where_lines(listed)[3:7] == [
        "litmus:         at least one `any` entry and every `all` entry answers yes:",
        "                1 (any): Does it parse the arguments?", "                print (any): Does it print?",
        "                thin (all): Is it thin?"]
    assert json.loads(where_document("custom", listed))["part"]["litmus"] == [
        {"ask": "Does it parse\nthe arguments?", "label": "1", "mode": "any"},
        {"ask": "Does it print?", "label": "print", "mode": "any"}, {"ask": "Is it thin?", "label": "thin", "mode": "all"}]


def test_a_litmus_of_one_text_stays_a_text_in_the_document():
    assert json.loads(where_document("custom", PART))["part"]["litmus"] == "Is it a command?"


def test_a_tier_s_litmus_list_is_said_as_a_part_s_is():
    tier = replace(TIER, litmus="", litmus_list=LISTED[1:2])
    test = InTests("tests/unit/test_app.py", True, None, (), "", (), (), tier, False, "", "tests/unit/", "")
    lines = where_lines(test)
    at = lines.index("tier litmus:    at least one of these answers yes:")
    assert lines[at + 1] == "                print (any): Does it print?"
    assert json.loads(where_document("custom", test))["tier"]["litmus"] == [
        {"ask": "Does it print?", "label": "print", "mode": "any"}]
