"""How `xarch where` shows its answer, on a hand-made WhereView: the labelled lines and the JSON document."""
import json

from xarch.cli.reports.where_report import where_document, where_lines
from xarch.modules.rules.contract import WhereView

PART = WhereView(kind="part", path="app/cli/app.py", exists=True, part="cli", role="the commands", litmus="Is it a command?",
                 folder="cli", may_import_text="contract", libraries=("typer",), untested="a shim")


def test_a_place_in_a_part_is_shown_with_its_part_role_and_what_it_may_import():
    assert where_lines("custom", PART) == [
        "path:           app/cli/app.py (exists)", "part:           cli", "role:           the commands",
        "litmus:         Is it a command?", "may import:     contract", "libraries:      typer",
        "tested by:      nothing: a shim"]


def test_a_place_in_no_part_is_shown_as_such_and_its_document_leaves_what_does_not_apply_null():
    nowhere = WhereView(kind="ungoverned", path="app/odd.py", exists=False)
    assert where_lines("custom", nowhere) == ["path:           app/odd.py (new)", "part:           none: ungoverned"]
    document = json.loads(where_document("custom", nowhere))
    assert (document["ok"], document["profile"], document["kind"], document["part"], document["test"]) == (
        True, "custom", "ungoverned", None, None)
