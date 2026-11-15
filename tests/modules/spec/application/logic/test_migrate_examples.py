"""Converting the examples of a profile of format 1: each example file goes to the path it illustrates in a folder of
example projects, the templates quote it by that path, and a tier's example note loses its parentheses."""
import pytest

from tests.modules.spec.application.logic.test_migrate_profile import made, old, tiered
from xarch.modules.spec.application.logic.migrate_examples import Copy, rewrite_examples

EXAMPLES = {
    "text": {"part": "shared", "path": "shared/text.py", "file": "ex/text.py", "note": "a pure function"},
    "route": {"part": "api", "path": "src/billing/api/route.py", "file": "ex/route.py"},
}
DOCS = {"arch.md": {"from": "arch.md"}}


def with_examples(**changes) -> dict:
    return old(examples=EXAMPLES, docs=DOCS) | changes


def test_every_example_file_is_copied_to_the_path_it_illustrates_below_one_folder_of_examples():
    converted = made(with_examples())
    assert converted.document["docs"]["examples"] == ["examples"]
    assert Copy("examples/shared/text.py", "ex/text.py") in converted.copies
    assert Copy("examples/src/billing/api/route.py", "ex/route.py") in converted.copies
    assert converted.names == {"text": "shared/text.py", "route": "src/billing/api/route.py"}


def test_the_note_of_an_example_is_kept_by_its_path():
    assert made(with_examples()).document["docs"]["example_notes"] == {"shared/text.py": "a pure function"}


def test_a_template_is_copied_to_its_own_path_to_have_its_example_placeholders_rewritten():
    assert Copy("arch.md", "arch.md", rewritten=True) in made(with_examples()).copies


def test_a_profile_with_no_examples_has_no_example_folder_and_copies_only_its_templates():
    converted = made(old(docs=DOCS))
    assert "examples" not in converted.document["docs"]
    assert converted.copies == (Copy("arch.md", "arch.md", rewritten=True),)


@pytest.mark.parametrize("text, names, written, unknown", [
    pytest.param("{{example:text}}", {"text": "shared/text.py"}, "{{example:shared/text.py}}", (),
                 id="a name is the path of its example"),
    pytest.param("a {{example: text, route}} b", {"text": "t.py", "route": "r.py"}, "a {{example:t.py, r.py}} b", (),
                 id="several names keep their order"),
    pytest.param("{{example:nope}} {{tiers}}", {"text": "t.py"}, "{{example:nope}} {{tiers}}", ("nope",),
                 id="a name no example has stays as written and is reported"),
    pytest.param("{{tier_examples}}{{app}}", {}, "{{tier_examples}}{{app}}", (),
                 id="the other placeholders are not touched"),
])
def test_the_example_placeholders_of_a_template_name_paths_and_an_unknown_name_is_reported(text, names, written, unknown):
    assert rewrite_examples(text, names) == (written, unknown)


def test_the_example_and_the_helpers_of_a_tier_are_paths_in_the_example_project_with_notes_in_plain_text():
    document = tiered()
    document["tiers"][0]["example"] = {"path": "tests/src/test_rules.py", "file": "ex/rules.py",
                                        "note": " (one per rule)"}
    document["tiers"][0]["helpers"] = [{"path": "tests/src/builders.py", "file": "ex/builders.py"}]
    converted = made(document)
    assert converted.document["tiers"]["unit"]["docs"]["example"] == "tests/src/test_rules.py"
    assert converted.document["tiers"]["unit"]["docs"]["helpers"] == ["tests/src/builders.py"]
    assert converted.document["docs"]["example_notes"] == {"tests/src/test_rules.py": "one per rule"}
    assert Copy("examples/tests/src/builders.py", "ex/builders.py") in converted.copies
    assert not any("note" in change for change in converted.changes)


def test_a_tier_note_that_was_not_in_parentheses_loses_its_punctuation_and_the_change_is_reported():
    document = tiered()
    document["tiers"][0]["example"] = {"path": "tests/src/test_rules.py", "file": "ex/rules.py", "note": ": see below"}
    converted = made(document)
    assert converted.document["docs"]["example_notes"] == {"tests/src/test_rules.py": ": see below".strip(": ")}
    assert any("tiers.unit.example" in change and "parentheses" in change for change in converted.changes)


def test_a_note_with_parentheses_inside_loses_only_the_outer_pair():
    document = tiered()
    document["tiers"][0]["example"] = {"path": "tests/src/test_rules.py", "file": "ex/rules.py",
                                        "note": " (it calls f(x))"}
    assert made(document).document["docs"]["example_notes"] == {"tests/src/test_rules.py": "it calls f(x)"}


def test_two_examples_at_one_path_in_different_files_keep_the_first_and_report_the_other():
    examples = EXAMPLES | {"again": {"part": "shared", "path": "shared/text.py", "file": "ex/other.py"}}
    converted = made(with_examples(examples=examples))
    assert Copy("examples/shared/text.py", "ex/text.py") in converted.copies
    assert not any(copy.source == "ex/other.py" for copy in converted.copies)
    assert any("again" in item and "shared/text.py" in item for item in converted.by_hand)


def test_the_same_file_under_two_names_is_one_example_with_both_names():
    examples = EXAMPLES | {"alias": {"part": "shared", "path": "shared/text.py", "file": "ex/text.py"}}
    converted = made(with_examples(examples=examples))
    assert converted.names["alias"] == "shared/text.py"
    assert converted.by_hand == ()


def test_an_example_whose_file_is_missing_is_reported_and_left_out_of_the_names():
    converted = made(with_examples(), missing={"ex/route.py"})
    assert "route" not in converted.names
    assert any("route" in item and "ex/route.py" in item for item in converted.by_hand)


def test_a_file_the_project_gets_that_is_also_an_example_is_written_from_the_example_that_holds_it():
    document = tiered(files={"tests/test_rules.py": {"from": "ex/rules.py", "pinned": True}})
    document["tiers"][0]["example"] = {"path": "tests/src/test_rules.py", "file": "ex/rules.py"}
    converted = made(document)
    assert converted.document["files"] == {"tests/test_rules.py": {"from": "examples/tests/src/test_rules.py",
                                                                    "pinned": True}}
    assert [copy.source for copy in converted.copies].count("ex/rules.py") == 1


def test_the_files_below_a_folder_entry_are_all_copied_to_their_own_paths():
    document = old(files={"presets/": {"from": "kit/"}})
    converted = made(document, files={"kit": ("a.txt", "deep/b.txt")})
    assert converted.copies == (Copy("kit/a.txt", "kit/a.txt"), Copy("kit/deep/b.txt", "kit/deep/b.txt"))
    assert converted.document["files"] == {"presets/": "kit/"}


def test_the_folder_of_examples_has_a_name_no_other_copied_file_lies_under():
    document = with_examples(files={"x.txt": {"from": "examples/note.txt"}})
    converted = made(document)
    assert converted.document["docs"]["examples"] == ["examples-1"]
    assert Copy("examples/note.txt", "examples/note.txt") in converted.copies
    assert Copy("examples-1/shared/text.py", "ex/text.py") in converted.copies
