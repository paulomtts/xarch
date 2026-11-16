"""The JSON document every command prints: indented by two, its text as it is."""
from xarch.cli.reports.document import document


def test_a_document_is_indented_and_keeps_its_text_as_it_is():
    assert document({"ok": False, "error": "café"}) == '{\n  "ok": false,\n  "error": "café"\n}'
