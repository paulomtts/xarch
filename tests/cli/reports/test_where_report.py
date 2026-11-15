"""How `xarch where` shows its answer, on hand-made answers: the labelled lines and the JSON document."""
import json

from xarch.cli.reports.where_report import where_document, where_lines
from xarch.modules.rules.contract import InPart, PartShown, Ungoverned, Untested

PART = InPart("app/cli/app.py", True, PartShown("cli", "cli", role="the commands", litmus="Is it a command?"), (),
              "contract", ("typer",), (), Untested("a shim"))


def test_a_place_in_a_part_is_shown_with_its_part_role_and_what_it_may_import():
    assert where_lines(PART) == [
        "path:           app/cli/app.py (exists)", "part:           cli", "role:           the commands",
        "litmus:         Is it a command?", "may import:     contract", "libraries:      typer",
        "tested by:      nothing: a shim"]


def test_a_place_in_no_part_is_shown_as_such_and_its_document_leaves_what_does_not_apply_null():
    nowhere = Ungoverned("app/odd.py", False, (), None, "")
    assert where_lines(nowhere) == ["path:           app/odd.py (new)", "part:           none: ungoverned"]
    document = json.loads(where_document("custom", nowhere))
    assert (document["ok"], document["profile"], document["kind"], document["part"], document["test"]) == (
        True, "custom", "ungoverned", None, None)
